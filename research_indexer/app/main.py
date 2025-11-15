import os, json, time
from datetime import datetime, timezone
from google.cloud import storage, bigquery, aiplatform
from dateutil.parser import isoparse
from flask import Flask, request
import threading

PROJECT = os.environ.get("PROJECT_ID", "seven-l-prod")
LOCATION = os.environ.get("LOCATION", "us-central1")
DATASET = os.environ.get("BQ_DATASET", "research_lake")
ARTIFACTS = f"{PROJECT}.{DATASET}.artifacts"

BUCKETS = os.environ.get("BUCKETS", "7l-data,7l-jsonl,7l-models,7l-pipelines").split(",")

# Init clients
storage_client = storage.Client()
bq = bigquery.Client()
aiplatform.init(project=PROJECT, location=LOCATION)

def embed_text(text: str):
    """Generate embedding using Vertex AI text-embedding-004"""
    try:
        from google.cloud import aiplatform
        model = aiplatform.TextEmbeddingModel.from_pretrained("text-embedding-004")
        # Keep it short to control cost
        text = text[:6000]
        vec = model.get_embeddings([text])[0].values
        return vec
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def summarize(name, path):
    """Generate summary using Gemini 1.5 Flash"""
    try:
        prompt = f"Give a concise 2-3 sentence summary for: {name} ({path}). If unknown, say what it likely contains based on the filename."
        from google.cloud import aiplatform
        # Gemini 1.5 Flash is cost-efficient for summaries
        model = aiplatform.GenerativeModel("gemini-1.5-flash-001")
        out = model.generate_content(prompt).text
        return out.strip()[:800]
    except Exception as e:
        print(f"Summary error: {e}")
        return f"(summary error) {e}"

def gcs_list(bucket):
    """List blobs in GCS bucket"""
    try:
        blobs = storage_client.list_blobs(bucket, prefix="")
        for b in blobs:
            yield b
    except Exception as e:
        print(f"Error listing bucket {bucket}: {e}")

def decide_kind(name):
    """Determine file type from extension"""
    lower = name.lower()
    for ext, kind in [
        (".pdf","pdf"),(".md","md"),(".ipynb","ipynb"),(".jpg","jpg"),
        (".jpeg","jpg"),(".png","png"),(".gif","gif"),(".csv","csv"),
        (".jsonl","jsonl"),(".ckpt","ckpt"),(".pt","ckpt"),(".h5","ckpt"),
        (".obj","mesh"),(".ply","mesh"),(".glb","mesh"),(".usdz","mesh"),
        (".json","json"),(".txt","txt"),(".py","python"),(".sh","script"),
        (".yml","yaml"),(".yaml","yaml"),(".html","html"),(".css","css"),
        (".js","javascript"),(".ts","typescript"),(".sql","sql")
    ]:
        if lower.endswith(ext): 
            return kind
    return "other"

def upsert_artifacts(rows):
    """Insert rows into BigQuery artifacts table"""
    try:
        table = bq.get_table(ARTIFACTS)
        errors = bq.insert_rows_json(table, rows)
        if errors:
            print(f"BigQuery insert errors: {errors}")
            raise RuntimeError(errors)
        print(f"Successfully inserted {len(rows)} artifacts")
    except Exception as e:
        print(f"Error inserting artifacts: {e}")

def create_artifacts_table():
    """Create the artifacts table if it doesn't exist"""
    try:
        # First, try to create the dataset if it doesn't exist
        try:
            dataset = bq.get_dataset(DATASET)
            print(f"Dataset {DATASET} already exists")
        except Exception:
            print(f"Creating dataset {DATASET}")
            dataset = bigquery.Dataset(f"{PROJECT}.{DATASET}")
            dataset.location = "US"
            dataset.description = "Research data lake for AI platform experiments"
            dataset = bq.create_dataset(dataset, timeout=30)
            print(f"Created dataset {DATASET}")
        
        # Check if table exists
        try:
            bq.get_table(ARTIFACTS)
            print(f"Table {ARTIFACTS} already exists")
        except Exception:
            print(f"Creating table {ARTIFACTS}")
            schema = [
                bigquery.SchemaField("uri", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("bucket", "STRING"),
                bigquery.SchemaField("path", "STRING"),
                bigquery.SchemaField("kind", "STRING"),
                bigquery.SchemaField("project", "STRING"),
                bigquery.SchemaField("tags", "STRING", mode="REPEATED"),
                bigquery.SchemaField("created", "TIMESTAMP"),
                bigquery.SchemaField("updated", "TIMESTAMP"),
                bigquery.SchemaField("size_bytes", "INT64"),
                bigquery.SchemaField("summary", "STRING"),
                bigquery.SchemaField("embedding", "FLOAT", mode="REPEATED"),  # Using REPEATED FLOAT instead of VECTOR for compatibility
            ]
            
            table = bigquery.Table(ARTIFACTS, schema=schema)
            table = bq.create_table(table, timeout=30)
            print(f"Created table {ARTIFACTS}")
    except Exception as e:
        print(f"Error creating dataset/table: {e}")
        raise

def main():
    """Main indexing function"""
    print(f"Starting indexer for project {PROJECT}")
    print(f"Buckets: {BUCKETS}")
    print(f"Dataset: {DATASET}")
    
    # Create table if needed
    create_artifacts_table()
    
    rows = []
    total_processed = 0
    
    for bucket in BUCKETS:
        bucket = bucket.strip()
        print(f"Processing bucket: {bucket}")
        
        for blob in gcs_list(bucket):
            # Skip folders
            if blob.name.endswith("/"):
                continue
                
            uri = f"gs://{bucket}/{blob.name}"
            kind = decide_kind(blob.name)
            path = blob.name
            created = blob.time_created
            updated = blob.updated

            # Determine project/tags from path
            project = None
            tags = []
            
            # Extract project from path structure
            path_parts = path.split("/")
            if len(path_parts) > 0:
                if path_parts[0] in ["papers", "refs", "renders"]:
                    project = "research"
                    tags.append("research")
                elif path_parts[0] in ["society", "ai_society"]:
                    project = "ai_society"
                    tags.append("ai_society")
                elif path_parts[0] in ["spatial_lab", "spatial"]:
                    project = "spatial_lab"
                    tags.append("spatial_lab")
                elif path_parts[0] in ["warehouse", "coordination", "padres"]:
                    project = "warehouse"
                    tags.append("warehouse")
                elif path_parts[0] in ["cloudvr", "vr"]:
                    project = "cloudvr"
                    tags.append("cloudvr")
                elif path_parts[0] in ["evolution", "experiments"]:
                    project = "evolution"
                    tags.append("evolution")
                else:
                    project = "general"
                    tags.append("general")
            
            # Add file type tag
            tags.append(kind)
            
            # Add bucket tag
            tags.append(bucket)

            # Lightweight summary + embedding
            try:
                summary = summarize(blob.name, path)
                embedding = embed_text(summary)
            except Exception as e:
                print(f"Error processing {blob.name}: {e}")
                summary = f"(processing error) {e}"
                embedding = None

            rows.append({
                "uri": uri,
                "bucket": bucket,
                "path": path,
                "kind": kind,
                "project": project,
                "tags": tags,
                "created": created.isoformat() if created else None,
                "updated": updated.isoformat() if updated else None,
                "size_bytes": blob.size,
                "summary": summary,
                "embedding": embedding,
            })
            
            total_processed += 1

            # Batch inserts periodically
            if len(rows) >= 100:  # Smaller batches for reliability
                upsert_artifacts(rows)
                rows.clear()
                print(f"Processed {total_processed} files so far...")

    # Insert remaining rows
    if rows:
        upsert_artifacts(rows)
    
    print(f"Indexing complete! Processed {total_processed} files total.")

# Flask app for Cloud Run
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """Cloud Run endpoint"""
    try:
        # Run indexing in background thread
        thread = threading.Thread(target=main)
        thread.start()
        return {"status": "indexing_started", "message": "Research indexer started successfully"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    # For local testing
    if os.environ.get("LOCAL_DEV"):
        main()
    else:
        # For Cloud Run
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
