#!/usr/bin/env bash
set -euo pipefail

LOG_TS_FORMAT="+%Y-%m-%dT%H:%M:%SZ"

log() {
  local ts
  ts="$(date -u "$LOG_TS_FORMAT")"
  printf '[%s] %s\n' "$ts" "$*"
}

log_error() {
  local ts
  ts="$(date -u "$LOG_TS_FORMAT")"
  printf '[%s] ERROR: %s\n' "$ts" "$*" >&2
}

ensure_path_for_gcloud() {
  if command -v gcloud >/dev/null 2>&1; then
    return 0
  fi

  local candidates=(
    "$HOME/google-cloud-sdk/path.bash.inc"
    "/opt/homebrew/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
    "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
    "/opt/homebrew/google-cloud-sdk/path.bash.inc"
    "/usr/local/google-cloud-sdk/path.bash.inc"
  )
  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      # shellcheck disable=SC1090
      source "$candidate"
    fi
  done
}

install_homebrew_if_missing() {
  if command -v brew >/dev/null 2>&1; then
    return 0
  fi
  log "Homebrew not found; installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -d "/opt/homebrew/bin" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -d "/usr/local/bin" ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

ensure_mac_tools() {
  install_homebrew_if_missing
  if [[ -d "/opt/homebrew/bin" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
  elif [[ -d "/usr/local/bin" ]]; then
    eval "$(/usr/local/bin/brew shellenv)" 2>/dev/null || true
  fi

  ensure_path_for_gcloud

  if ! command -v gcloud >/dev/null 2>&1; then
    log "Installing Google Cloud SDK via Homebrew..."
    brew install --cask google-cloud-sdk
    ensure_path_for_gcloud
  fi

  if ! command -v gcloud >/dev/null 2>&1; then
    log_error "gcloud CLI still unavailable after installation."
    exit 1
  fi

  if ! command -v jq >/dev/null 2>&1; then
    log "Installing jq via Homebrew..."
    brew install jq
  fi
}

ensure_linux_tools() {
  local sudo_cmd="sudo"
  if ! command -v sudo >/dev/null 2>&1; then
    sudo_cmd=""
  fi

  if ! command -v gcloud >/dev/null 2>&1; then
    log "Installing Google Cloud SDK via apt..."
    $sudo_cmd apt-get update
    $sudo_cmd apt-get install -y apt-transport-https ca-certificates gnupg curl lsb-release
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
      | $sudo_cmd tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | $sudo_cmd gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
    $sudo_cmd apt-get update
    $sudo_cmd apt-get install -y google-cloud-sdk
  fi

  if ! command -v jq >/dev/null 2>&1; then
    log "Installing jq via apt..."
    $sudo_cmd apt-get install -y jq
  fi
}

ensure_components() {
  local missing=()
  command -v bq >/dev/null 2>&1 || missing+=("bq")
  command -v gsutil >/dev/null 2>&1 || missing+=("gsutil")

  if [[ ${#missing[@]} -eq 0 ]]; then
    log "Required gcloud components already present."
    return 0
  fi

  log "Installing missing gcloud components: ${missing[*]}"
  if ! gcloud components install "${missing[@]}" --quiet; then
    log "Component manager disabled; proceeding (components may already be accessible)."
  fi
}

ensure_authentication() {
  log "Checking Application Default Credentials..."
  if gcloud auth application-default print-access-token >/dev/null 2>&1; then
    log "ADC already configured."
    return 0
  fi

  log "ADC missing; launching browser login (one time)..."
  gcloud auth application-default login
  log "ADC login complete."
}

collect_projects() {
  PROJECT_IDS=()
  local count=0
  while IFS= read -r project_id; do
    [[ -z "$project_id" ]] && continue
    PROJECT_IDS+=("$project_id")
    count=$((count + 1))
    [[ $count -ge 10 ]] && break
  done < <(gcloud projects list --sort-by=projectId --format="value(projectId)")

  if [[ ${#PROJECT_IDS[@]} -eq 0 ]]; then
    log_error "No accessible projects found."
    exit 1
  fi

  log "Projects selected: ${PROJECT_IDS[*]}"
}

enable_apis() {
  local project="$1"
  log "Enabling required APIs on ${project} (idempotent)..."
  gcloud services enable \
    cloudasset.googleapis.com \
    bigquery.googleapis.com \
    cloudresourcemanager.googleapis.com \
    storage.googleapis.com \
    storagetransfer.googleapis.com \
    --project="$project"
}

create_bq_dataset() {
  local project="$1"
  local dataset="$2"
  local location="$3"
  log "Ensuring BigQuery dataset ${project}:${dataset} exists in ${location}..."
  if ! bq --location="$location" mk -f -d "${project}:${dataset}"; then
    log "Create failed (likely already exists); verifying..."
    if bq --location="$location" show "${project}:${dataset}" >/dev/null 2>&1; then
      log "Dataset ${project}:${dataset} already present."
    else
      log_error "Dataset ${project}:${dataset} unavailable after creation attempt."
      exit 1
    fi
  fi
}

export_assets_to_bigquery() {
  local table_ref="$1"
  for project_id in "${PROJECT_IDS[@]}"; do
    log "Exporting Cloud Asset Inventory for ${project_id}..."
    gcloud asset export \
      --project="$project_id" \
      --content-type=resource \
      --bigquery-table="$table_ref" \
      --partition-key=request-time \
      --output-bigquery-force
  done
}

verify_bigquery_table() {
  local project="$1"
  local dataset="$2"
  local table="assets_all"
  log "Checking BigQuery table ${project}.${dataset}.${table}..."
  if bq --location="$BQ_LOCATION" show "${project}:${dataset}.${table}" >/dev/null 2>&1; then
    log "Confirmed ${project}.${dataset}.${table} exists."
  else
    log "Table ${project}.${dataset}.${table} not yet readable; continuing."
  fi
}

create_destination_bucket() {
  local bucket_uri="$1"
  local location="$2"
  if gcloud storage buckets describe "$bucket_uri" >/dev/null 2>&1; then
    log "Destination bucket ${bucket_uri} already exists."
    return 0
  fi

  log "Creating destination bucket ${bucket_uri} in ${location}..."
  gcloud storage buckets create "$bucket_uri" --location="$location" --uniform-bucket-level-access
}

copy_storage_objects() {
  COPY_STATUS=()
  local dest_bucket_name="${DEST_BUCKET#gs://}"

  for project_id in "${PROJECT_IDS[@]}"; do
    log "Listing buckets in ${project_id}..."
    local bucket_list
    if ! bucket_list="$(gcloud storage buckets list --project="$project_id" --format="value(name)")"; then
      log_error "Bucket listing failed for ${project_id}."
      COPY_STATUS+=("${project_id},*,list_failed")
      continue
    fi

    if [[ -z "$bucket_list" ]]; then
      log "No buckets found in ${project_id}."
      continue
    fi

    while IFS= read -r bucket_name; do
      [[ -z "$bucket_name" ]] && continue

      if [[ "$bucket_name" == "$dest_bucket_name" ]]; then
        log "Skipping destination bucket ${bucket_name}."
        continue
      fi

      local destination_path="${DEST_BUCKET}/from-${project_id}/${bucket_name}/"
      log "Copying gs://${bucket_name} -> ${destination_path}"
      if gcloud --quiet --verbosity=warning storage cp --no-clobber -r "gs://${bucket_name}/**" "${destination_path}"; then
        COPY_STATUS+=("${project_id},${bucket_name},success")
      else
        log_error "Copy failed for ${bucket_name} in ${project_id}; recording failure and continuing."
        COPY_STATUS+=("${project_id},${bucket_name},failed")
      fi
    done <<<"$bucket_list"
  done
}

generate_manifest_and_sign_url() {
  local timestamp
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local manifest_object="manifest-${timestamp}.json"

  local projects_json
  projects_json="$(printf '%s\n' "${PROJECT_IDS[@]}" | jq -R . | jq -s .)"

  local copy_status_json="[]"
  if [[ ${#COPY_STATUS[@]} -gt 0 ]]; then
    copy_status_json="$(printf '%s\n' "${COPY_STATUS[@]}" \
      | jq -R 'split(",") | {project: .[0], bucket: .[1], status: .[2]}' | jq -s .)"
  fi

  local manifest_json
  manifest_json="$(jq -n \
    --arg timestamp "$timestamp" \
    --arg destBucket "$DEST_BUCKET" \
    --arg bqTable "${BQ_PROJECT}.${BQ_DATASET}.assets_all" \
    --argjson projects "$projects_json" \
    --argjson copyStatus "$copy_status_json" \
    '{timestamp: $timestamp, projects: $projects, bigquery_table: $bqTable, destination_bucket: $destBucket, copy_status: $copyStatus}')"

  log "Uploading manifest to ${DEST_BUCKET}/${manifest_object}..."
  printf '%s' "$manifest_json" | gcloud storage cp - "${DEST_BUCKET}/${manifest_object}"

  log "Generating 48-hour signed URL..."
  local sign_output
  sign_output="$(gcloud storage sign-url --http-verb=GET --duration=48h "${DEST_BUCKET}/${manifest_object}")"
  SIGNED_URL="$(printf '%s\n' "$sign_output" | awk '/https?:\/\// {print $NF}' | tail -n1)"

  if [[ -z "$SIGNED_URL" ]]; then
    log_error "Failed to obtain signed URL."
    exit 1
  fi

  FINAL_MANIFEST_OBJECT="$manifest_object"
  FINAL_SQL="SELECT name, resource.location AS location FROM \`${BQ_PROJECT}.${BQ_DATASET}.assets_all\` WHERE asset_type = 'storage.googleapis.com/Bucket';"
}

check_bigquery_connectivity() {
  curl -4 --silent --head --max-time 5 https://bigquery.googleapis.com >/dev/null 2>&1
}

check_cloud_build_permissions() {
  local required_roles=(
    "roles/cloudasset.owner"
    "roles/bigquery.dataEditor"
    "roles/bigquery.admin"
    "roles/storage.admin"
    "roles/serviceusage.serviceUsageAdmin"
  )
  local missing_roles=()
  local project_id="$1"
  local service_account="$2"

  for role in "${required_roles[@]}"; do
    if ! gcloud projects get-iam-policy "$project_id" --format="yaml" --filter="bindings.role:$role AND bindings.members:serviceAccount:$service_account" | grep -q "$role"; then
      missing_roles+=("$role")
    fi
  done

  if [[ ${#missing_roles[@]} -gt 0 ]]; then
    log_error "Cloud Build service account ${service_account} is missing the following required roles: ${missing_roles[*]}"
    log_error "Please grant these permissions following the instructions in packages/docs/runbooks/cloud_build_permissions.md"
    return 1
  fi
  return 0
}

run_via_cloud_build() {
  local project_id="$1"
  log "Local BigQuery endpoint unreachable; re-running inside Cloud Build."
  local tmpdir
  tmpdir="$(mktemp -d)"
  cp "$0" "${tmpdir}/gcp_all_in_one.sh"

  cat <<'EOF' > "${tmpdir}/cloudbuild.yaml"
steps:
- name: gcr.io/google.com/cloudsdktool/cloud-sdk:slim
  entrypoint: bash
  args:
  - -lc
  - |
      set -euo pipefail
      chmod +x gcp_all_in_one.sh
      SKIP_REMOTE_FALLBACK=1 SUPPRESS_FINAL_STDOUT=1 ./gcp_all_in_one.sh
options:
  logging: LEGACY
serviceAccount: projects/seven-l-prod/serviceAccounts/central-inventory-sa@seven-l-prod.iam.gserviceaccount.com
logsBucket: gs://seven-l-prod_cloudbuild
EOF

  local build_log
  build_log="$(mktemp)"

  if ! check_cloud_build_permissions "$project_id" "central-inventory-sa@seven-l-prod.iam.gserviceaccount.com"; then
    exit 1
  fi

  set +e
  CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT= gcloud builds submit "$tmpdir" --config="${tmpdir}/cloudbuild.yaml" | tee "$build_log"
  local build_status=$?
  set -e

  rm -rf "$tmpdir"

  if [[ $build_status -ne 0 ]]; then
    log_error "Cloud Build execution failed."
    cat "$build_log" >&2
    rm -f "$build_log"
    exit $build_status
  fi

  local signed_line
  signed_line="$(grep -F 'Signed URL:' "$build_log" | tail -n1 || true)"
  local sql_line
  sql_line="$(grep -F 'BigQuery SQL:' "$build_log" | tail -n1 || true)"

  rm -f "$build_log"

  if [[ -z "$signed_line" || -z "$sql_line" ]]; then
    log_error "Unable to parse final output from Cloud Build logs."
    exit 1
  fi

  SIGNED_URL="${signed_line##*Signed URL: }"
  FINAL_SQL="${sql_line##*BigQuery SQL: }"

  printf '===== FINAL RESULT =====\n'
  printf 'SIGNED_URL=%s\n' "$SIGNED_URL"
  printf 'SQL=%s\n' "$FINAL_SQL"
  exit 0
}

main() {
  log "Starting centralized GCP inventory workflow..."
  local platform
  platform="$(uname -s)"
  case "$platform" in
    Darwin)
      log "Detected macOS."
      ensure_mac_tools
      ;;
    Linux)
      log "Detected Linux."
      ensure_linux_tools
      ;;
    *)
      log_error "Unsupported OS: ${platform}"
      exit 1
      ;;
  esac

  ensure_components
  ensure_authentication
  collect_projects

  if [[ -z "${SKIP_REMOTE_FALLBACK:-}" ]]; then
    if ! check_bigquery_connectivity; then
      run_via_cloud_build "$RUNNER_PROJECT"
    fi
  fi

  RUNNER_PROJECT="${PROJECT_IDS[0]}"
  log "Setting billing quota project to ${RUNNER_PROJECT}..."
  gcloud config set billing/quota_project "$RUNNER_PROJECT"

  BQ_PROJECT="$RUNNER_PROJECT"
  BQ_LOCATION="US"
  BQ_DATASET="central_inventory"
  local date_stamp
  date_stamp="$(date -u +%Y%m%d)"
  DEST_BUCKET="gs://central-inventory-${date_stamp}-${RANDOM}"
  DEST_BUCKET_NAME="${DEST_BUCKET#gs://}"

  log "BigQuery project: ${BQ_PROJECT}"
  log "BigQuery dataset: ${BQ_DATASET} (${BQ_LOCATION})"
  log "Destination bucket: ${DEST_BUCKET}"

  enable_apis "$BQ_PROJECT"
  create_bq_dataset "$BQ_PROJECT" "$BQ_DATASET" "$BQ_LOCATION"

  local table_ref="projects/${BQ_PROJECT}/datasets/${BQ_DATASET}/tables/assets_all"
  export_assets_to_bigquery "$table_ref"
  verify_bigquery_table "$BQ_PROJECT" "$BQ_DATASET"

  create_destination_bucket "$DEST_BUCKET" "$BQ_LOCATION"
  copy_storage_objects
  generate_manifest_and_sign_url

  log "===== FINAL RESULT ====="
  log "Signed URL: ${SIGNED_URL}"
  log "BigQuery SQL: ${FINAL_SQL}"

  if [[ -z "${SUPPRESS_FINAL_STDOUT:-}" ]]; then
    printf '===== FINAL RESULT =====\n'
    printf 'SIGNED_URL=%s\n' "$SIGNED_URL"
    printf 'SQL=%s\n' "$FINAL_SQL"
  fi
}

main "$@"