# 🔧 NOUS REPOSITORY REORGANIZATION PLAN
## Step-by-Step Implementation Guide

**Version:** 1.0
**Date:** November 15, 2025
**Status:** Ready for Implementation
**Estimated Time:** 6-8 weeks

---

## 🎯 OBJECTIVES

1. **Eliminate 37% file duplication** (150+ duplicate files)
2. **Fix critical security vulnerability** (hardcoded API key)
3. **Organize scattered files** (150+ root scripts)
4. **Consolidate documentation** (81 → ~50 markdown files)
5. **Create production-ready structure**

---

## 📅 IMPLEMENTATION TIMELINE

### **PHASE 1: IMMEDIATE ACTIONS** (Week 1)
**Goal:** Fix critical issues, quick wins
**Effort:** 2-3 days
**Savings:** ~76 files + security fix

### **PHASE 2: CONSOLIDATION** (Weeks 2-3)
**Goal:** Organize documentation and outputs
**Effort:** 1-2 weeks
**Savings:** ~40 files + improved navigation

### **PHASE 3: REFACTORING** (Weeks 4-6)
**Goal:** Code consolidation and standardization
**Effort:** 2-3 weeks
**Benefit:** Maintainable codebase

### **PHASE 4: PRODUCTION HARDENING** (Weeks 7-8)
**Goal:** Production-ready infrastructure
**Effort:** 1-2 weeks
**Benefit:** Deployable system

---

## 🚨 PHASE 1: IMMEDIATE ACTIONS (Week 1)

### Day 1: Security & Cleanup

#### ❗ CRITICAL: Security Fix
```bash
# 1. Remove hardcoded API key
# File: /home/user/NOUS/cloud_data_puller.py:237
# Action: Replace with environment variable

# Before:
"api_key_provided": "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"

# After:
"api_key_provided": os.getenv("GEMINI_API_KEY")

# 2. Rotate the compromised API key in Google Cloud Console
# 3. Update all environments with new key
```

#### ❗ Delete Anomalous Files
```bash
# Delete all pip installation artifacts
rm /home/user/NOUS/=*

# Expected deletions: 13 files
# =0.7.0, =0.11.0, =0.12.0, =0.18.0, =1.0.0, =1.3.0,
# =1.7.0, =1.8.0, =1.21.0, =2.1.0, =3.4.0, =4.62.0, =6.2.0
```

**Checkpoint 1:** Commit security fixes
```bash
git add cloud_data_puller.py
git commit -m "SECURITY: Remove hardcoded API key, use environment variable"
```

---

### Day 2: Eliminate Major Duplicates

#### Decision 1: Society Simulation Directory
```bash
# CHOOSE ONE:
# Option A: Keep /src/, delete /gcp_deployment/
# Option B: Keep /gcp_deployment/, delete /src/

# Recommendation: Keep /src/ (clearer name)

# First, verify they're identical:
diff -r /home/user/NOUS/src /home/user/NOUS/gcp_deployment

# If identical, delete duplicate:
rm -rf /home/user/NOUS/gcp_deployment/

# Files saved: ~50
```

#### Decision 2: PADRES Spatial Environment
```bash
# Keep: /home/user/NOUS/environments/hack0/padres/
# Delete: /home/user/NOUS/spatial_rl_mvp/

# Verify equivalence:
diff -r environments/hack0/padres spatial_rl_mvp

# Delete duplicate:
rm -rf /home/user/NOUS/spatial_rl_mvp/

# Files saved: 4
```

#### Decision 3: Evolution System
```bash
# Option 1: Keep /evolution/, delete /gcp_deployment/evolution/
# Option 2: If /gcp_deployment/ was kept, delete /evolution/

# Assuming /gcp_deployment/ was deleted in Decision 1:
# Only /evolution/ remains - no action needed

# If /gcp_deployment/ kept:
# rm -rf /home/user/NOUS/evolution/

# Files saved: 9 (if applicable)
```

#### Decision 4: Discovered Functions
```bash
# Consolidate discovered_functions and test_functions

# Create outputs directory:
mkdir -p /home/user/NOUS/outputs/functions

# Move unique functions:
mv /home/user/NOUS/discovered_functions/* /home/user/NOUS/outputs/functions/

# Delete duplicate:
rm -rf /home/user/NOUS/test_functions/

# Clean up old directory:
rm -rf /home/user/NOUS/discovered_functions/

# Files saved: ~42
```

**Checkpoint 2:** Commit duplicate elimination
```bash
git add .
git commit -m "Eliminate major duplicates: save 76+ files

- Delete duplicate society simulation directory
- Delete duplicate PADRES spatial environment
- Consolidate discovered functions
- Delete pip installation artifacts"
```

---

### Day 3: Create Organized Directories

#### Create New Directory Structure
```bash
# Create organized directories
mkdir -p /home/user/NOUS/scripts/{analytics,research,deployment,spatial,llm,demos,utilities}
mkdir -p /home/user/NOUS/outputs/{papers,functions,datasets,reports}
mkdir -p /home/user/NOUS/lib/{llm_clients,data_managers,paper_generators}
mkdir -p /home/user/NOUS/docs/{systems,research,infrastructure,api}
```

**Checkpoint 3:** Commit directory structure
```bash
git add .
git commit -m "Create organized directory structure for reorganization"
```

---

## 📚 PHASE 2: CONSOLIDATION (Weeks 2-3)

### Week 2: Documentation Consolidation

#### Task 2.1: Consolidate AMIEN Documentation
```bash
# Merge 4 files into 1

# Source files:
# - AMIEN_SYSTEM_STATUS_REPORT.md
# - AMIEN_COMPLETE_DEPLOYMENT_SUMMARY.md
# - AMIEN_PRODUCTION_SUMMARY.md
# - FINAL_AMIEN_COMPLETION_SUMMARY.md

# Create consolidated doc:
cat > docs/systems/AMIEN_STATUS.md << 'EOF'
# AMIEN System Status

## Current Status
[Merge content from all 4 files]

## Version History
- v1.0: Initial deployment
- v2.0: Production release
...
EOF

# Move old files to archive:
mkdir -p docs/archive
mv AMIEN_*.md docs/archive/
mv FINAL_AMIEN_COMPLETION_SUMMARY.md docs/archive/

# Files saved: 3
```

#### Task 2.2: Consolidate "Final" Summaries
```bash
# Create single project status file
cat > docs/PROJECT_STATUS.md << 'EOF'
# NOUS Project Status

## Overall Status
[Consolidated content]

## Component Status
### AMIEN
[Content from FINAL_AMIEN_COMPLETION_SUMMARY.md]

### Systems
[Content from FINAL_SYSTEM_SUMMARY.md]

### GCP Infrastructure
[Content from FINAL_GCP_ANALYSIS_SUMMARY.md]

### Comprehensive Status
[Content from FINAL_COMPREHENSIVE_SUMMARY.md]
EOF

# Move old files:
mv FINAL_*.md docs/archive/

# Files saved: 3
```

#### Task 2.3: Consolidate Society Simulation Roadmaps
```bash
# Create single roadmap file
cat > docs/systems/SOCIETY_ROADMAP.md << 'EOF'
# Society Simulation Roadmap

## Phase α (Complete)
[Content from PHASE_1_COMPLETE.md]

## Phase β (In Progress)
[Content from PHASE_BETA_ROADMAP.md]

## Phase γ (Planned)
[Content from comprehensive_2500_agent_llm_society_plan.md]

## Implementation Timeline
[Content from PROJECT_IMPLEMENTATION_ROADMAP.md]

## Development Details
[Content from DEVELOPMENT_PLAN.md]
EOF

# Move old files:
mv comprehensive_2500_agent_llm_society_plan.md docs/archive/
mv PHASE_*.md docs/archive/
mv DEVELOPMENT_PLAN.md docs/archive/
mv PROJECT_IMPLEMENTATION_ROADMAP.md docs/archive/

# Files saved: 4
```

#### Task 2.4: Create VR Studies Index
```bash
# Create index file
cat > docs/research/VR_STUDIES_INDEX.md << 'EOF'
# VR Research Studies Index

## Large-Scale Studies

### 1,000 Experiment Study
- File: [VR_1000_EXPERIMENT_RESEARCH_REPORT.md](../../VR_1000_EXPERIMENT_RESEARCH_REPORT.md)
- Date: May 27, 2025
- Experiments: 1,000
- Success Rate: 100%
- Duration: 11.5 minutes

### 25 Experiment Study
- File: [VR_RESEARCH_STUDY_REPORT.md](../../VR_RESEARCH_STUDY_REPORT.md)
- Date: May 2025
- Experiments: 25
- Type: Real PyBullet physics

## Analysis Reports
[Links to other VR studies...]
EOF

# Keep original files, just organize:
mkdir -p docs/research/vr_studies
mv VR_*EXPERIMENT*.md docs/research/vr_studies/
mv comprehensive_vr_*.md docs/research/vr_studies/
mv enhanced_vr_*.md docs/research/vr_studies/

# Files saved via better organization: 3
```

**Checkpoint 4:** Commit documentation consolidation
```bash
git add docs/
git commit -m "Consolidate documentation: save 13+ files

- Merge AMIEN docs into single status file
- Consolidate all 'Final' summaries
- Merge society simulation roadmaps
- Create VR studies index"
```

---

### Week 3: Organize Research Outputs & Scripts

#### Task 2.5: Organize Research Outputs
```bash
# Move generated papers
mv generated_papers outputs/papers/automated/
mv test_papers outputs/papers/archive/  # Mark as archive
mv amien_research_output/* outputs/papers/amien/
rm -rf amien_research_output

# Move functions (already done in Phase 1)
# outputs/functions/ already contains consolidated functions

# Organize datasets
mkdir -p outputs/datasets
# If synthetic_vr_experiments.json exists, move it:
# mv synthetic_vr_experiments.json outputs/datasets/

# Organize reports
mkdir -p outputs/reports
mv *_integration_report*.md outputs/reports/ 2>/dev/null || true
```

#### Task 2.6: Organize Root Scripts (Part 1 - Analytics)
```bash
# Move analytics scripts
mv advanced_analytics_system.py scripts/analytics/
mv advanced_visualization.py scripts/analytics/
mv analysis_*.py scripts/analytics/ 2>/dev/null || true
mv comprehensive_*.py scripts/analytics/ 2>/dev/null || true
mv visualize_*.py scripts/analytics/ 2>/dev/null || true
mv god_portal_analysis*.py scripts/analytics/ 2>/dev/null || true
```

#### Task 2.7: Organize Root Scripts (Part 2 - Research)
```bash
# Move research pipeline scripts
mv production_research_pipeline.py scripts/research/
mv paper_generator.py scripts/research/
mv enhanced_research*.py scripts/research/ 2>/dev/null || true
mv scientific_*.py scripts/research/ 2>/dev/null || true
mv research_*.py scripts/research/ 2>/dev/null || true
mv *_pipeline.py scripts/research/ 2>/dev/null || true
```

#### Task 2.8: Organize Root Scripts (Part 3 - Deployment)
```bash
# Move deployment scripts
mv deploy_*.py scripts/deployment/ 2>/dev/null || true
mv deploy_*.sh scripts/deployment/ 2>/dev/null || true
mv cloud_*.py scripts/deployment/ 2>/dev/null || true
mv gcp_*.py scripts/deployment/ 2>/dev/null || true
mv gcp_*.sh scripts/deployment/ 2>/dev/null || true
mv setup_*.sh scripts/deployment/ 2>/dev/null || true
```

#### Task 2.9: Organize Root Scripts (Part 4 - Spatial/LLM/Demos)
```bash
# Move spatial scripts
mv spatial_*.py scripts/spatial/ 2>/dev/null || true
mv run_spatial_*.py scripts/spatial/ 2>/dev/null || true
mv autonomous_spatial*.py scripts/spatial/ 2>/dev/null || true

# Move LLM scripts
mv llm_*.py scripts/llm/ 2>/dev/null || true
mv groq_*.py scripts/llm/ 2>/dev/null || true
mv gemini_*.py scripts/llm/ 2>/dev/null || true
mv implement_*_integration.py scripts/llm/ 2>/dev/null || true

# Move demo scripts
mv demo_*.py scripts/demos/ 2>/dev/null || true
mv simple_*.py scripts/demos/ 2>/dev/null || true
mv ai_agent_demonstration.py scripts/demos/

# Move utilities
mv bigquery_manager.py scripts/utilities/
mv agent_communication_system.py scripts/utilities/ 2>/dev/null || true
```

**Checkpoint 5:** Commit reorganization
```bash
git add .
git commit -m "Organize research outputs and root scripts

- Move generated papers to outputs/papers/
- Organize 150+ root scripts into categorized directories
- Consolidate research outputs
- Create clear directory structure"
```

---

## 🔨 PHASE 3: REFACTORING (Weeks 4-6)

### Week 4: Code Consolidation

#### Task 3.1: Create Unified LLM Clients Library
```bash
# Create library structure
mkdir -p lib/llm_clients
cd lib/llm_clients

# Create unified interface
cat > __init__.py << 'EOF'
"""Unified LLM client library for NOUS project."""
from .base import BaseLLMClient
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .groq_client import GroqClient

__all__ = [
    'BaseLLMClient',
    'AnthropicClient',
    'OpenAIClient',
    'GeminiClient',
    'GroqClient',
]
EOF

# Create base client
cat > base.py << 'EOF'
"""Base LLM client with common functionality."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

class BaseLLMClient(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_api_key()

    @abstractmethod
    def _get_api_key(self) -> str:
        """Get API key from environment."""
        pass

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion."""
        pass

    async def complete_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Complete with automatic retry logic."""
        # Common retry logic
        pass
EOF

# Extract and consolidate existing clients:
# 1. Copy from backend_services/mcp_servers/claude_mcp_server.py → anthropic_client.py
# 2. Copy from backend_services/mcp_servers/gemini_mcp_server.py → gemini_client.py
# 3. Copy from backend_services/mcp_servers/openai_mcp_server.py → openai_client.py
# 4. Create groq_client.py from scattered implementations

# Update all imports across codebase:
# OLD: from environments.hack0.padres.llm_services import get_anthropic_completion
# NEW: from lib.llm_clients import AnthropicClient
```

#### Task 3.2: Consolidate Research Pipelines
```bash
# Create canonical research pipeline
cd scripts/research

# Choose production_research_pipeline.py as canonical
# Merge features from:
# - enhanced_research_pipeline.py
# - enhanced_research_without_mcp.py
# - enhanced_research_orchestrator.py
# - scientific_research_framework.py

# Create consolidated pipeline with feature flags:
cat > research_pipeline.py << 'EOF'
"""Canonical research pipeline with configurable features."""

class ResearchPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_mcp = config.get('use_mcp', True)
        self.mode = config.get('mode', 'production')  # production | enhanced | scientific

    async def run(self):
        # Unified pipeline implementation
        pass
EOF

# Archive old implementations:
mkdir -p ../archive/research_pipelines
mv enhanced_research*.py ../archive/research_pipelines/
mv scientific_research_framework.py ../archive/research_pipelines/
```

#### Task 3.3: Consolidate Paper Generators
```bash
# Move to library
mkdir -p lib/paper_generators
cd lib/paper_generators

# Use paper_generator.py as base (627 lines, most comprehensive)
cp ../../scripts/research/paper_generator.py ./paper_generator.py

# Add features from:
# - simple_paper_generator.py → simple_mode flag
# - comprehensive_research_paper.py → comprehensive_mode flag

# Create library interface:
cat > __init__.py << 'EOF'
"""Paper generation library."""
from .paper_generator import AutomatedPaperGenerator

__all__ = ['AutomatedPaperGenerator']
EOF
```

**Checkpoint 6:** Commit code consolidation
```bash
git add lib/
git add scripts/
git commit -m "Consolidate shared code into libraries

- Create unified llm_clients library
- Consolidate research pipelines
- Consolidate paper generators
- Establish single source of truth for shared functionality"
```

---

### Week 5: Configuration Standardization

#### Task 3.4: Standardize Python Version
```bash
# Update all Dockerfiles to Python 3.11
find . -name "Dockerfile*" -type f -exec sed -i 's/python:3\.9/python:3.11/g' {} \;
find . -name "Dockerfile*" -type f -exec sed -i 's/python:3\.10/python:3.11/g' {} \;

# Update pyproject.toml
sed -i 's/python = ">=3.10"/python = ">=3.11"/g' pyproject.toml

# Update CI/CD
sed -i 's/python-version: \[3.8, 3.9, 3.10\]/python-version: [3.11]/g' .github/workflows/cicd.yml
```

#### Task 3.5: Pin Docker Image Tags
```bash
# Update k8s/deployment.yaml
sed -i 's/:latest/:v1.0.0/g' k8s/deployment.yaml

# Update docker-compose.yml
sed -i 's/prom\/prometheus:latest/prom\/prometheus:v2.45.0/g' docker-compose.yml

# Update cloudbuild.yaml
# Change: gcr.io/$PROJECT_ID/spatial-experiment:latest
# To: gcr.io/$PROJECT_ID/spatial-experiment:$COMMIT_SHA
```

#### Task 3.6: Add TLS/SSL Configuration
```bash
# Update k8s/service.yaml to use Ingress with TLS
cat > k8s/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cloudvr-perfguard-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.nous-research.example.com
    secretName: cloudvr-perfguard-tls
  rules:
  - host: api.nous-research.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cloudvr-perfguard-ai
            port:
              number: 80
EOF
```

#### Task 3.7: Consolidate Container Registry
```bash
# Choose Artifact Registry over GCR (recommended by Google)
# Update all cloudbuild.yaml files:

# OLD: gcr.io/$PROJECT_ID/image-name
# NEW: us-central1-docker.pkg.dev/$PROJECT_ID/nous-images/image-name

find . -name "cloudbuild.yaml" -type f -exec \
  sed -i 's|gcr.io/\$PROJECT_ID|us-central1-docker.pkg.dev/\$PROJECT_ID/nous-images|g' {} \;
```

**Checkpoint 7:** Commit configuration standardization
```bash
git add .
git commit -m "Standardize configurations

- Python 3.11 everywhere
- Pin all Docker image tags
- Add TLS/SSL via Ingress
- Consolidate to Artifact Registry"
```

---

### Week 6: Testing Infrastructure

#### Task 3.8: Migrate Tests to pytest
```bash
# Move all test files to tests/
mkdir -p tests/{unit,integration,performance,stress}

# Categorize and move tests:
# Unit tests
mv test_spatial_lab_basic.py tests/unit/
mv test_dashboard_components.py tests/unit/

# Integration tests
mv test_spatial_lab_integration.py tests/integration/
mv test_real_llm_integration.py tests/integration/
mv test_gemini_integration.py tests/integration/
mv test_cloud_deployment.py tests/integration/

# Performance tests
mv run_real_spatial_test.py tests/performance/
mv spatial_reasoning_3d_test.py tests/performance/

# Stress tests
mv stress_test_validation.py tests/stress/
mv scale_test_*.py tests/stress/

# Create conftest.py for shared fixtures:
cat > tests/conftest.py << 'EOF'
"""Shared pytest fixtures."""
import pytest
from lib.llm_clients import AnthropicClient, GeminiClient

@pytest.fixture
def anthropic_client():
    return AnthropicClient()

@pytest.fixture
def gemini_client():
    return GeminiClient()
EOF
```

#### Task 3.9: Add Coverage Tracking
```bash
# Update pytest.ini
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=atroposlib
    --cov=backend_services
    --cov=cloudvr_perfguard
    --cov=src
    --cov=lib
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
EOF

# Add pytest-cov to requirements
echo "pytest-cov>=4.1.0" >> requirements-dev.txt
```

#### Task 3.10: Update CI/CD for New Test Structure
```bash
# Update .github/workflows/cicd.yml
cat > .github/workflows/cicd.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Upload coverage
        uses: codecov/codecov-action@v3
EOF
```

**Checkpoint 8:** Commit testing infrastructure
```bash
git add tests/
git add pytest.ini
git add .github/workflows/
git commit -m "Migrate to organized pytest structure

- Categorize tests: unit, integration, performance, stress
- Add pytest-cov for coverage tracking
- Update CI/CD for new test structure
- Add shared fixtures in conftest.py"
```

---

## 🛡️ PHASE 4: PRODUCTION HARDENING (Weeks 7-8)

### Week 7: Infrastructure Security & Reliability

#### Task 4.1: Implement Secrets Management
```bash
# Create GCP Secret Manager setup script
cat > scripts/deployment/setup_secrets.sh << 'EOF'
#!/bin/bash
# Setup GCP Secret Manager

PROJECT_ID="amien-research-pipeline"

# Create secrets
echo "Creating secrets in Secret Manager..."
gcloud secrets create gemini-api-key --project=$PROJECT_ID
gcloud secrets create openai-api-key --project=$PROJECT_ID
gcloud secrets create anthropic-api-key --project=$PROJECT_ID

echo "Grant Cloud Run access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Update your deployment configs to use secrets."
EOF

chmod +x scripts/deployment/setup_secrets.sh

# Update Cloud Run configs to use Secret Manager
# Example: gcp_deployment/api_service.yaml
```

#### Task 4.2: Add Comprehensive Health Checks
```bash
# Update backend_services/main.py
cat >> backend_services/main.py << 'EOF'

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }

    # Check MCP manager
    try:
        mcp_servers = await mcp_manager.list_servers()
        health_status["components"]["mcp_manager"] = "healthy"
        health_status["components"]["mcp_servers"] = len(mcp_servers)
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["mcp_manager"] = f"unhealthy: {str(e)}"

    # Check Celery
    try:
        celery_inspect = celery_app.control.inspect()
        active_workers = celery_inspect.active()
        health_status["components"]["celery"] = "healthy" if active_workers else "no_workers"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["celery"] = f"unhealthy: {str(e)}"

    # Check database connections, etc.

    return health_status

@app.get("/ready")
async def readiness_check():
    """Readiness check for load balancer."""
    # Check if app is ready to receive traffic
    return {"ready": True}
EOF
```

#### Task 4.3: Implement Resource Quotas
```bash
# Create k8s resource quota
cat > k8s/resource-quota.yaml << 'EOF'
apiVersion: v1
kind: ResourceQuota
metadata:
  name: nous-compute-quota
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "4"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: nous-limit-range
spec:
  limits:
  - max:
      cpu: "2"
      memory: 4Gi
    min:
      cpu: "100m"
      memory: 128Mi
    type: Container
EOF
```

#### Task 4.4: Add Centralized Logging
```bash
# Update docker-compose.yml to add Loki
cat >> docker-compose.yml << 'EOF'

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki-config.yaml:/etc/loki/local-config.yaml
      - loki-data:/loki
    restart: unless-stopped

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log
      - ./monitoring/promtail-config.yaml:/etc/promtail/config.yml
    restart: unless-stopped

volumes:
  loki-data:
EOF

# Create Loki config
mkdir -p monitoring
cat > monitoring/loki-config.yaml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks
EOF
```

**Checkpoint 9:** Commit infrastructure hardening
```bash
git add scripts/deployment/
git add k8s/
git add monitoring/
git add backend_services/
git add docker-compose.yml
git commit -m "Production infrastructure hardening

- Implement GCP Secret Manager
- Add comprehensive health checks
- Add Kubernetes resource quotas
- Implement centralized logging with Loki"
```

---

### Week 8: Documentation & Deployment

#### Task 4.5: Create Architecture Diagrams
```bash
# Install mermaid-cli or use mermaid.live
# Create architecture diagram

cat > docs/ARCHITECTURE.md << 'EOF'
# NOUS Architecture

## System Overview

```mermaid
graph TB
    User[User/Client] --> API[FastAPI Gateway]
    API --> MCP[MCP Manager]
    MCP --> Claude[Claude MCP]
    MCP --> Gemini[Gemini MCP]
    MCP --> BQ[BigQuery MCP]
    MCP --> FS[Firestore MCP]

    API --> Celery[Celery Queue]
    Celery --> Worker1[Worker Pool]
    Worker1 --> Spatial[Spatial Lab]
    Worker1 --> VR[CloudVR-PerfGuard]
    Worker1 --> Society[Society Simulation]

    Spatial --> PyBullet[PyBullet Physics]
    VR --> AI[AI Research Pipeline]
    Society --> Mesa[Mesa Framework]
```

## Component Breakdown
[Detailed descriptions of each component]
EOF
```

#### Task 4.6: Write Deployment Runbooks
```bash
# Create deployment runbook
cat > docs/infrastructure/DEPLOYMENT_RUNBOOK.md << 'EOF'
# Deployment Runbook

## Prerequisites
- GCP account with billing enabled
- kubectl installed
- Docker installed
- gcloud CLI configured

## Step 1: Setup GCP Project
```bash
export PROJECT_ID="amien-research-pipeline"
gcloud config set project $PROJECT_ID
```

## Step 2: Setup Secrets
```bash
./scripts/deployment/setup_secrets.sh
```

## Step 3: Build and Push Images
```bash
./scripts/deployment/build_images.sh
```

## Step 4: Deploy to Kubernetes
```bash
kubectl apply -f k8s/
```

## Step 5: Deploy to Cloud Run
```bash
./scripts/deployment/deploy_cloud_run.sh
```

## Step 6: Verify Deployment
```bash
curl https://api.nous-research.example.com/health
```

## Rollback Procedure
[Detailed rollback steps]

## Troubleshooting
[Common issues and solutions]
EOF
```

#### Task 4.7: API Documentation
```bash
# FastAPI auto-generates OpenAPI docs at /docs
# Create additional API documentation

cat > docs/api/README.md << 'EOF'
# NOUS API Documentation

## Base URLs
- Production: `https://api.nous-research.example.com`
- Staging: `https://staging-api.nous-research.example.com`

## Authentication
All API requests require an API key:
```bash
curl -H "X-API-Key: your_api_key" https://api.nous-research.example.com/endpoint
```

## Endpoints

### POST /experiments/batch
Submit a batch of experiments for execution.

**Request:**
```json
{
  "experiments": [...],
  "priority": "normal"
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "status": "queued"
}
```

[Complete API documentation]
EOF
```

#### Task 4.8: Create Migration Guide
```bash
cat > docs/MIGRATION_GUIDE.md << 'EOF'
# Migration Guide: Old Structure → New Structure

## Import Changes

### LLM Clients
```python
# OLD
from environments.hack0.padres.llm_services import get_anthropic_completion

# NEW
from lib.llm_clients import AnthropicClient
client = AnthropicClient()
response = await client.complete(prompt)
```

### Research Pipeline
```python
# OLD
from production_research_pipeline import Production24x7Pipeline

# NEW
from scripts.research.research_pipeline import ResearchPipeline
pipeline = ResearchPipeline(config)
```

### Paper Generator
```python
# OLD
from paper_generator import AutomatedPaperGenerator

# NEW
from lib.paper_generators import AutomatedPaperGenerator
```

## File Location Changes
[Complete mapping of old → new file locations]

## Configuration Changes
[How to update configs for new structure]

## Testing Changes
[How to run tests in new structure]
EOF
```

#### Task 4.9: Final README Update
```bash
# Update main README.md
cat > README.md << 'EOF'
# NOUS Research Platform

🚀 Multi-system AI research platform with production-grade infrastructure

## Features
- ✅ Atroposlib: RL training framework
- ✅ Backend Services: MCP architecture
- ✅ CloudVR-PerfGuard: VR performance testing
- ✅ Spatial Lab: Multi-agent coordination
- ✅ Society Simulation: 2,500-agent LLM simulation

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Backend Services
```bash
python backend_services/main.py
```

### Run Tests
```bash
pytest tests/
```

## Documentation
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/api/README.md)
- [Deployment Runbook](docs/infrastructure/DEPLOYMENT_RUNBOOK.md)
- [Migration Guide](docs/MIGRATION_GUIDE.md)

## Project Structure
[Link to FORENSIC_ANALYSIS_REPORT.md for complete breakdown]

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
[Your license]
EOF
```

**Checkpoint 10:** Final commit
```bash
git add docs/
git add README.md
git commit -m "Complete documentation and deployment guides

- Add architecture diagrams
- Create deployment runbooks
- Document API endpoints
- Write migration guide
- Update main README"
```

---

## ✅ FINAL VERIFICATION CHECKLIST

### Security ✓
- [ ] Hardcoded API key removed
- [ ] API key rotated in Google Cloud Console
- [ ] GCP Secret Manager configured
- [ ] All secrets use environment variables
- [ ] Docker images pinned to specific versions
- [ ] TLS/SSL configured for all public endpoints

### Organization ✓
- [ ] All duplicate files deleted (150+ files)
- [ ] Root scripts organized into subdirectories
- [ ] Research outputs organized
- [ ] Documentation consolidated
- [ ] Tests organized into pytest structure

### Code Quality ✓
- [ ] LLM clients library created
- [ ] Research pipelines consolidated
- [ ] Paper generators consolidated
- [ ] Python version standardized (3.11)
- [ ] Import statements updated
- [ ] All tests passing

### Infrastructure ✓
- [ ] Resource quotas defined
- [ ] Health checks implemented
- [ ] Centralized logging configured
- [ ] Monitoring dashboards updated
- [ ] CI/CD pipeline updated

### Documentation ✓
- [ ] Architecture diagrams created
- [ ] Deployment runbook written
- [ ] API documentation complete
- [ ] Migration guide written
- [ ] README updated

---

## 📊 SUCCESS METRICS

### Before
- Files: ~600
- Duplicates: 150+ (37%)
- Security issues: 1 critical
- Organization: Poor
- Test coverage: Unknown
- Documentation: Scattered

### After
- Files: ~380 (37% reduction)
- Duplicates: 0
- Security issues: 0
- Organization: Excellent
- Test coverage: >70%
- Documentation: Comprehensive

---

## 🎉 COMPLETION

Once all phases are complete:

1. **Tag the release:**
```bash
git tag -a v2.0.0 -m "Complete repository reorganization"
git push origin v2.0.0
```

2. **Create GitHub release** with notes from FORENSIC_ANALYSIS_REPORT.md

3. **Update all deployment targets** to use new structure

4. **Notify team** with migration guide

5. **Celebrate!** 🎊 You've transformed a research prototype into a production-ready platform!

---

**Reorganization Plan Complete**
**Ready for Implementation: ✅**
**Estimated Time: 6-8 weeks**
**Expected Benefits: Massive improvement in maintainability, security, and usability**
