# 🔀 REPOSITORY SEPARATION STRATEGY
## NOUS → 4 Independent Repositories

**Date:** November 15, 2025
**Status:** Planning Phase
**Execution Time:** 6 weeks (recommended)

---

## 🎯 OBJECTIVE

Separate the monolithic NOUS repository into **4 independent, maintainable repositories**:

1. **`spatial-lab`** - Warehouse Robotics AI System
2. **`llm-society`** - 2,500-Agent LLM-Driven Society Simulation
3. **`amien-research`** - AI Research Automation Platform
4. **`atroposlib`** - RL Training Framework (already separated)

---

## 📊 EXECUTIVE SUMMARY

### Current State
- **Total Files:** ~600 files in monorepo
- **Duplication:** 37% (150+ duplicate files)
- **Systems:** 4 distinct systems with minimal cross-dependencies
- **Shared Code:** Minimal - each system is largely independent

### Target State
- **4 Independent Repositories** with clear boundaries
- **0% Duplication** - each system owns its code
- **Clear Dependencies** - Atroposlib as external package
- **Independent Deployment** - each system deployable separately

### Complexity Assessment
| System | Separation Difficulty | Files | Main Challenge |
|--------|----------------------|-------|----------------|
| Atroposlib | ✅ **Easy** (Done) | 45 | Already separated |
| CloudVR-PerfGuard | ✅ **Easy** | 35 | Already isolated |
| Spatial Lab | ⚠️ **Medium** | 25 | Import updates needed |
| Society Simulation | ⚠️ **Hard** | 50 | Delete duplicate directory |

---

## 📦 REPOSITORY 1: SPATIAL LAB (Warehouse Robotics)

### **Target Name:** `spatial-lab` or `warehouse-robotics-ai`

### **Purpose**
Multi-agent warehouse robotics coordination system using LLM-driven spatial reasoning.

### **Core Capabilities**
- Multi-robot fleet coordination
- A* pathfinding and collision avoidance
- Warehouse layout generation and optimization
- LLM-based task planning (Gemini, Llama)
- Real-time performance metrics and evaluation
- Research validation and statistical analysis

---

### **Files to Include** (32 total)

#### **Source Code** (25 files from `src/spatial_lab/`)
```
spatial_lab/
├── __init__.py
├── config.py (423 lines) - Configuration management
├── experiment_runner.py (634 lines) - Main entry point
│
├── environments/
│   ├── __init__.py
│   ├── warehouse_environment.py (852 lines) - Main Atropos environment
│   ├── warehouse_layout.py (287 lines) - Grid-based warehouse
│   └── warehouse_tasks.py (456 lines) - Pick, pack, navigation tasks
│
├── coordination/
│   ├── __init__.py
│   ├── multi_agent_coordinator.py (523 lines) - Coordination logic
│   ├── robot_fleet.py (412 lines) - Robot fleet management
│   ├── path_planning.py (301 lines) - A* pathfinding
│   └── communication.py (234 lines) - Inter-agent messaging
│
├── evaluation/
│   ├── __init__.py
│   ├── spatial_metrics.py (445 lines) - Performance metrics
│   ├── performance_analyzer.py (378 lines) - Analysis tools
│   ├── statistical_analysis.py (312 lines) - Statistical tests
│   └── coordination_metrics.py (289 lines) - Coordination scoring
│
├── llm/
│   ├── __init__.py
│   ├── llm_coordinator.py (522 lines) - LLM orchestration
│   ├── gemini_client.py (368 lines) - Google Gemini integration
│   └── llama_client.py (294 lines) - Llama model integration
│
├── research/
│   ├── __init__.py
│   └── research_validator.py (267 lines) - Experiment validation
│
└── performance/
    ├── __init__.py
    └── performance_collector.py (189 lines) - Metrics collection
```

#### **Test Files** (7 files)
```
tests/
├── test_spatial_lab_basic.py
├── test_spatial_lab_integration.py
├── test_warehouse_environment.py (create from simple_spatial_test.py)
├── test_coordination.py (create from run_real_spatial_test.py)
├── demo_spatial_lab.py
├── autonomous_spatial_experiment.py
└── spatial_reasoning_3d_test.py
```

#### **Documentation** (4 files)
```
docs/
├── SPATIAL_LAB_README.md → README.md (main)
├── SPATIAL_LAB_SUCCESS_SUMMARY.md → docs/RESULTS.md
├── SPATIAL_AI_LAB_IMPLEMENTATION_SUMMARY.md → docs/IMPLEMENTATION.md
└── SPATIAL_EXPERIMENT_CLOUD_DEPLOYMENT_SUMMARY.md → docs/DEPLOYMENT.md
```

#### **Configuration & Deployment** (3 files)
```
config/
├── warehouse_configs.py (from config.py)
└── experiment_configs.yaml (new)

deployment/
├── deploy_spatial_lab.sh
└── Dockerfile (new)
```

---

### **Dependencies**

#### **External Package Dependency**
```python
# requirements.txt
atroposlib>=0.2.1  # 🔗 RL framework (published PyPI package)
```

**Usage:**
```python
from atroposlib.envs.base import BaseEnv, BaseEnvConfig
from atroposlib.envs.server_handling.server_baseline import APIServerConfig
from atroposlib.type_definitions import Item, Message
```

#### **Python Dependencies**
```python
# requirements.txt
atroposlib>=0.2.1
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
asyncio>=3.4.3
aiohttp>=3.8.0
pydantic>=2.0.0
wandb>=0.12.0
google-generativeai>=0.3.0  # Gemini
transformers>=4.20.0         # Llama
python-dotenv>=0.19.0
```

#### **No Dependencies On:**
- ❌ Society Simulation
- ❌ CloudVR-PerfGuard
- ❌ Other NOUS systems

---

### **Separation Steps**

#### **Step 1: Copy Directory Structure**
```bash
# Create new repository
git init spatial-lab
cd spatial-lab

# Copy core code
cp -r /path/to/NOUS/src/spatial_lab/ ./spatial_lab/

# Copy tests
mkdir -p tests/
cp /path/to/NOUS/test_spatial_lab*.py tests/
cp /path/to/NOUS/demo_spatial_lab.py tests/
cp /path/to/NOUS/autonomous_spatial_experiment.py tests/
cp /path/to/NOUS/spatial_reasoning_3d_test.py tests/
cp /path/to/NOUS/run_real_spatial_test.py tests/
cp /path/to/NOUS/simple_spatial_test.py tests/

# Copy documentation
mkdir -p docs/
cp /path/to/NOUS/SPATIAL_LAB_*.md docs/
```

#### **Step 2: Update Imports**
```python
# OLD (in NOUS monorepo):
from src.spatial_lab.environments import WarehouseEnvironment
from src.spatial_lab.coordination import MultiAgentCoordinator
from src.spatial_lab.llm import GeminiClient

# NEW (in spatial-lab repo):
from spatial_lab.environments import WarehouseEnvironment
from spatial_lab.coordination import MultiAgentCoordinator
from spatial_lab.llm import GeminiClient
```

**Automated Update:**
```bash
# Replace all imports
find spatial_lab/ tests/ -name "*.py" -type f -exec \
  sed -i 's/from src\.spatial_lab\./from spatial_lab./g' {} \;
find spatial_lab/ tests/ -name "*.py" -type f -exec \
  sed -i 's/import src\.spatial_lab\./import spatial_lab./g' {} \;
```

#### **Step 3: Create Package Structure**
```bash
# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="spatial-lab",
    version="1.0.0",
    description="Multi-agent warehouse robotics coordination system",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "atroposlib>=0.2.1",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        # ... (full requirements)
    ],
)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
atroposlib>=0.2.1
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
aiohttp>=3.8.0
pydantic>=2.0.0
wandb>=0.12.0
google-generativeai>=0.3.0
transformers>=4.20.0
python-dotenv>=0.19.0
EOF

# Create .env.example
cat > .env.example << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
WANDB_API_KEY=your_wandb_api_key_here
EOF
```

#### **Step 4: Create README**
```markdown
# Spatial Lab - Warehouse Robotics AI

Multi-agent warehouse robotics coordination system using LLM-driven spatial reasoning.

## Features
- 🤖 Multi-robot fleet coordination
- 🧭 A* pathfinding with collision avoidance
- 🏭 Warehouse layout generation
- 🧠 LLM-based task planning (Gemini, Llama)
- 📊 Real-time performance metrics
- 🔬 Research validation framework

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Run Example
```python
from spatial_lab.experiment_runner import SpatialLabExperiment

experiment = SpatialLabExperiment(config="basic_warehouse")
experiment.run()
```

## Architecture
[Link to docs/ARCHITECTURE.md]

## Documentation
- [Implementation Guide](docs/IMPLEMENTATION.md)
- [Results Summary](docs/RESULTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
```

#### **Step 5: Test Independence**
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run demo
python tests/demo_spatial_lab.py
```

---

## 📦 REPOSITORY 2: LLM SOCIETY (2,500-Agent Simulation)

### **Target Name:** `llm-society` or `mesa-llm-simulation`

### **Purpose**
Large-scale agent-based society simulation with 2,500 LLM-driven agents, economic systems, social networks, and family dynamics.

### **Core Capabilities**
- 2,500 concurrent LLM-based agents
- Economic system (banking, markets, trade)
- Social networks and family relationships
- GPU-accelerated simulation (FLAME GPU)
- Asset generation (3D models via Point-E)
- Real-time monitoring and visualization

---

### **Files to Include** (60+ total)

#### **Source Code** (50+ files from `src/`)
```
llm_society/
├── __init__.py
├── main.py (entry point - Typer CLI)
│
├── agents/
│   ├── __init__.py
│   └── llm_agent.py (1,247 lines) - Core LLM-driven agent
│
├── simulation/
│   ├── __init__.py
│   └── society_simulator.py (1,834 lines) - Mesa-based simulation
│
├── llm/
│   ├── __init__.py
│   └── coordinator.py (688 lines) - LLM request coordination
│
├── social/
│   ├── __init__.py
│   └── family_system.py (567 lines) - Family relationships
│
├── economics/
│   ├── __init__.py
│   ├── banking_system.py (423 lines)
│   ├── market_system.py (512 lines)
│   └── economic_analyzer.py (289 lines)
│
├── flame_gpu/
│   ├── __init__.py
│   ├── flame_gpu_simulation.py (892 lines) - GPU acceleration
│   ├── agent_kernels.py (445 lines)
│   ├── gpu_memory_manager.py (234 lines)
│   └── performance_profiler.py (312 lines)
│
├── asset_generation/
│   ├── __init__.py
│   ├── asset_manager.py (456 lines)
│   └── point_e_handler.py (378 lines)
│
├── assets/
│   ├── __init__.py
│   └── point_e_generator.py (289 lines)
│
├── database/
│   ├── __init__.py
│   └── database_handler.py (512 lines)
│
├── monitoring/
│   ├── __init__.py
│   └── metrics.py (234 lines)
│
└── utils/
    ├── __init__.py
    ├── config.py (445 lines)
    └── text_utils.py (123 lines)
```

#### **Test & Demo Files** (10+ files)
```
tests/
├── test_llm_agent.py (create from simple_society_demo.py)
├── test_economics.py (create from demo_population_dynamics.py)
├── test_family_system.py
├── demo_society.py
├── demo_all_capabilities.py
├── live_society_dashboard.py
└── ultimate_society_demo.py
```

#### **Documentation** (5 files)
```
docs/
├── LLM_SOCIETY_README.md → README.md
├── POPULATION_DYNAMICS_README.md → docs/POPULATION.md
├── COMPREHENSIVE_2500_AGENT_ANALYSIS.md → docs/RESEARCH.md
├── COMPREHENSIVE_2500_AGENT_LLM_SOCIETY_PLAN.md → docs/ROADMAP.md
└── FINAL_SYSTEM_SUMMARY.md → docs/STATUS.md
```

---

### **🚨 CRITICAL: Delete Duplicate Directory First**

#### **Before Separation**
```bash
# IMPORTANT: gcp_deployment/ is a 100% duplicate of src/
# Verify they're identical:
diff -r /path/to/NOUS/src /path/to/NOUS/gcp_deployment

# If identical (they are), DELETE gcp_deployment/:
rm -rf /path/to/NOUS/gcp_deployment/

# This saves 50+ duplicate files
```

---

### **Dependencies**

#### **No Dependencies On Other NOUS Systems**
- ❌ No dependency on Atroposlib (uses Mesa instead)
- ❌ No dependency on Spatial Lab
- ❌ No dependency on CloudVR-PerfGuard

**Completely independent!**

#### **Python Dependencies**
```python
# requirements.txt
mesa>=1.0.0                # Agent-based modeling framework
google-generativeai>=0.3.0 # Gemini API
anthropic>=0.5.0           # Claude API (optional)
openai>=1.0.0              # OpenAI API (optional)
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
aiohttp>=3.8.0
asyncio>=3.4.3
pydantic>=2.0.0
typer>=0.9.0               # CLI framework
rich>=13.0.0               # Terminal output
python-dotenv>=0.19.0

# Optional GPU acceleration
torch>=1.11.0
flamegpu>=2.0.0            # GPU-accelerated agent simulation
```

---

### **Separation Steps**

#### **Step 1: Delete Duplicate**
```bash
# CRITICAL: Delete gcp_deployment/ directory first
cd /path/to/NOUS
rm -rf gcp_deployment/
git add gcp_deployment/
git commit -m "Delete duplicate gcp_deployment/ directory"
```

#### **Step 2: Copy Source Code**
```bash
# Create new repository
git init llm-society
cd llm-society

# Copy entire src/ directory (minus spatial_lab)
cp -r /path/to/NOUS/src/* ./llm_society/
rm -rf llm_society/spatial_lab/  # Remove spatial lab

# Copy tests and demos
mkdir -p tests/
cp /path/to/NOUS/*society*.py tests/
cp /path/to/NOUS/*demo*.py tests/
cp /path/to/NOUS/test_dashboard*.py tests/

# Copy documentation
mkdir -p docs/
cp /path/to/NOUS/LLM_SOCIETY_*.md docs/
cp /path/to/NOUS/POPULATION_*.md docs/
cp /path/to/NOUS/COMPREHENSIVE_2500_*.md docs/
```

#### **Step 3: Update Imports**
```python
# OLD (in NOUS monorepo):
from src.agents.llm_agent import LLMAgent
from src.simulation.society_simulator import SocietySimulator
from src.economics.market_system import MarketSystem

# NEW (in llm-society repo):
from llm_society.agents.llm_agent import LLMAgent
from llm_society.simulation.society_simulator import SocietySimulator
from llm_society.economics.market_system import MarketSystem
```

**Automated Update:**
```bash
# Replace all imports
find llm_society/ tests/ -name "*.py" -type f -exec \
  sed -i 's/from src\./from llm_society./g' {} \;
find llm_society/ tests/ -name "*.py" -type f -exec \
  sed -i 's/import src\./import llm_society./g' {} \;
```

#### **Step 4: Create Package Structure**
```bash
# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="llm-society",
    version="1.0.0",
    description="2,500-agent LLM-driven society simulation",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "mesa>=1.0.0",
        "google-generativeai>=0.3.0",
        # ... (full requirements)
    ],
    entry_points={
        "console_scripts": [
            "llm-society=llm_society.main:app",
        ],
    },
)
EOF

# Create CLI entry point
cat > llm_society/main.py << 'EOF'
import typer
from llm_society.simulation.society_simulator import SocietySimulator

app = typer.Typer()

@app.command()
def run(agents: int = 2500):
    """Run society simulation with N agents."""
    simulator = SocietySimulator(num_agents=agents)
    simulator.run()

if __name__ == "__main__":
    app()
EOF
```

#### **Step 5: Test Independence**
```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
llm-society run --agents 100  # Start with 100 for testing

# Run tests
pytest tests/ -v
```

---

## 📦 REPOSITORY 3: AMIEN RESEARCH (AI Research Automation)

### **Target Name:** `amien-research` or `cloudvr-perfguard`

### **Purpose**
AI-driven research automation platform that generates research papers, discovers optimization functions, and analyzes VR performance data.

### **Core Capabilities**
- Autonomous research paper generation (88/100 quality)
- VR performance regression detection
- AI Scientist integration (Sakana AI)
- FunSearch integration (Google DeepMind)
- Multi-AI research orchestration
- Automated dataset generation

---

### **Files to Include** (43 total)

#### **Source Code** (35 files)
```
amien_research/
├── cloudvr_perfguard/
│   ├── __init__.py
│   ├── core/
│   │   ├── database.py (456 lines) - SQLite performance DB
│   │   ├── performance_tester.py (678 lines) - VR testing
│   │   ├── regression_detector.py (523 lines) - Statistical analysis
│   │   ├── gpu_monitor.py (312 lines)
│   │   └── container_manager.py (445 lines)
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py (389 lines) - FastAPI service
│   ├── ai_integration/
│   │   ├── __init__.py
│   │   ├── research_orchestrator.py (734 lines) - Multi-AI coordinator
│   │   ├── ai_scientist_integration.py (612 lines) - Sakana AI wrapper
│   │   ├── funsearch_integration.py (567 lines) - FunSearch wrapper
│   │   ├── paper_generator.py (489 lines)
│   │   ├── function_discovery.py (523 lines)
│   │   ├── data_adapter.py (234 lines)
│   │   ├── real_data_integration.py (389 lines)
│   │   └── continuous_research_pipeline.py (856 lines)
│   └── scripts/
│       └── populate_test_data.py (178 lines)
│
└── ai_research/
    ├── __init__.py
    ├── ai_scientist_manager.py (892 lines) - AI Scientist wrapper
    └── funsearch_manager.py (745 lines) - FunSearch wrapper
```

#### **Test Files** (8 files)
```
tests/
├── test_cloudvr_basic.py
├── test_ai_research_integration.py
├── test_ai_research_simple.py
├── test_performance_tester.py
├── test_regression_detector.py
└── demo_research_pipeline.py
```

#### **Research Outputs**
```
research_outputs/
├── papers/
│   ├── amien/ (25 files from amien_research_output/)
│   └── automated/ (84 files from generated_papers/)
├── functions/
│   └── discovered/ (42 files from discovered_functions/)
└── datasets/
    └── synthetic_vr_experiments.json (200 experiments)
```

#### **Documentation** (5 files)
```
docs/
├── cloudvr_perfguard/README.md → README.md
├── AMIEN_COMPLETE_DEPLOYMENT_SUMMARY.md → docs/DEPLOYMENT.md
├── AMIEN_SYSTEM_STATUS_REPORT.md → docs/STATUS.md
├── AI_INTEGRATION_DEPLOYMENT_GUIDE.md → docs/INTEGRATION.md
└── RESEARCH_PIPELINE_SUCCESS_SUMMARY.md → docs/RESULTS.md
```

---

### **Dependencies**

#### **No Dependencies On Other NOUS Systems**
- ❌ Completely independent
- ❌ No shared code with other systems

**Self-contained AI research platform!**

#### **Python Dependencies**
```python
# requirements.txt
fastapi>=0.95.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
aiosqlite>=0.17.0
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0
docker>=6.0.0
google-generativeai>=0.3.0
openai>=1.0.0
python-dotenv>=0.19.0
```

---

### **Separation Steps**

#### **Step 1: Copy Directory Structure** (Easiest separation!)
```bash
# Create new repository
git init amien-research
cd amien-research

# Copy entire cloudvr_perfguard/ directory
cp -r /path/to/NOUS/cloudvr_perfguard/ ./

# Copy ai_research/ directory
cp -r /path/to/NOUS/ai_research/ ./

# Copy research outputs
mkdir -p research_outputs/papers/{amien,automated}
mkdir -p research_outputs/functions/discovered
mkdir -p research_outputs/datasets

cp -r /path/to/NOUS/amien_research_output/* research_outputs/papers/amien/
cp -r /path/to/NOUS/generated_papers/* research_outputs/papers/automated/
cp -r /path/to/NOUS/discovered_functions/* research_outputs/functions/discovered/

# Copy documentation
mkdir -p docs/
cp /path/to/NOUS/AMIEN_*.md docs/
cp /path/to/NOUS/AI_INTEGRATION_*.md docs/
cp /path/to/NOUS/RESEARCH_PIPELINE_*.md docs/
```

#### **Step 2: No Import Updates Needed!**
```python
# Already correct:
from cloudvr_perfguard.core import PerformanceTester
from cloudvr_perfguard.ai_integration import ResearchOrchestrator
from ai_research import AIScientistManager
```

**No changes needed - already self-contained!**

#### **Step 3: Test Independence**
```bash
# Install dependencies
pip install -r cloudvr_perfguard/requirements.txt

# Run FastAPI service
uvicorn cloudvr_perfguard.api.main:app --reload

# Run tests
pytest tests/ -v
```

---

## 📦 REPOSITORY 4: ATROPOSLIB (RL Framework)

### **Target Name:** `atroposlib`

### **Status:** ✅ **Already Separated**

This is already a standalone repository and published PyPI package.

**PyPI Package:** https://pypi.org/project/atroposlib/
**Version:** 0.2.1

### **No Action Needed**

Other systems should simply install it:
```bash
pip install atroposlib>=0.2.1
```

---

## 🔗 DEPENDENCY GRAPH

```
                    ┌─────────────────────┐
                    │    ATROPOSLIB       │
                    │   (RL Framework)    │
                    │                     │
                    │  PyPI Package v0.2.1│
                    └──────────┬──────────┘
                               │
                               │ pip install
                               ▼
                    ┌─────────────────────┐
                    │   SPATIAL LAB       │
                    │ (Warehouse Robotics)│
                    │                     │
                    │ Uses: BaseEnv,      │
                    │ APIServerConfig     │
                    └─────────────────────┘


┌─────────────────────┐              ┌─────────────────────┐
│   LLM SOCIETY       │              │  AMIEN RESEARCH     │
│ (2500 Agent Sim)    │              │ (AI Automation)     │
│                     │              │                     │
│ Independent         │              │ Independent         │
│ Uses Mesa           │              │ Self-contained      │
└─────────────────────┘              └─────────────────────┘
```

**Key Insight:** Only ONE dependency exists - Spatial Lab depends on Atroposlib (via pip).

---

## 📋 STEP-BY-STEP EXECUTION PLAN

### **Week 1: Preparation & Cleanup**

#### **Day 1: Audit & Tag**
```bash
# Audit all files
find . -name "*.py" | wc -l  # Count Python files
find . -name "*.md" | wc -l  # Count Markdown files

# Create pre-separation tag
git tag -a pre-separation -m "State before repository separation"
git push origin pre-separation

# Create separation manifest
cat > SEPARATION_MANIFEST.md << 'EOF'
# Repository Separation Manifest

## Files by Repository

### Spatial Lab
- src/spatial_lab/ (25 files)
- test_spatial_lab*.py (7 files)
- SPATIAL_LAB_*.md (4 files)

### LLM Society
- src/ minus spatial_lab/ (50 files)
- *society*.py, *demo*.py (10 files)
- LLM_SOCIETY_*.md (5 files)

### AMIEN Research
- cloudvr_perfguard/ (35 files)
- ai_research/ (3 files)
- AMIEN_*.md (5 files)

### Atroposlib
- Already separated (no action)
EOF
```

#### **Day 2-3: Delete Duplicates**
```bash
# CRITICAL: Delete gcp_deployment/ (100% duplicate of src/)
rm -rf gcp_deployment/
git add gcp_deployment/
git commit -m "Delete duplicate gcp_deployment/ directory"

# Delete duplicate PADRES environments
rm -rf spatial_rl_mvp/  # Keep environments/hack0/padres/ instead
git add spatial_rl_mvp/
git commit -m "Delete duplicate spatial_rl_mvp/"

# Delete duplicate test functions
rm -rf test_functions/  # Keep discovered_functions/
git add test_functions/
git commit -m "Delete duplicate test_functions/"

# Files saved: ~150 files
```

---

### **Week 2: Separate AMIEN Research** (Easiest)

#### **Rationale:** Start with easiest to build confidence

```bash
# Create new repo on GitHub
gh repo create amien-research --public

# Clone locally
git clone https://github.com/yourusername/amien-research.git
cd amien-research

# Copy files from NOUS
cp -r /path/to/NOUS/cloudvr_perfguard/ ./
cp -r /path/to/NOUS/ai_research/ ./
mkdir -p research_outputs/papers/amien
cp -r /path/to/NOUS/amien_research_output/* research_outputs/papers/amien/

# Copy docs
mkdir -p docs/
cp /path/to/NOUS/AMIEN_*.md docs/
cp /path/to/NOUS/cloudvr_perfguard/README.md README.md

# Create requirements.txt
cp cloudvr_perfguard/requirements.txt requirements.txt

# Test
pip install -r requirements.txt
pytest cloudvr_perfguard/ -v

# Commit and push
git add .
git commit -m "Initial commit: AMIEN research platform"
git push origin main
```

**Verification:**
```bash
# Run FastAPI service
uvicorn cloudvr_perfguard.api.main:app --reload

# Test endpoint
curl http://localhost:8000/health
```

---

### **Week 3: Verify Atroposlib** (Already done)

```bash
# Verify package works
pip install atroposlib==0.2.1

# Test import
python -c "from atroposlib.envs.base import BaseEnv; print('✅ Works!')"

# Update documentation
# Confirm version, dependencies, examples
```

---

### **Week 4: Separate Spatial Lab** (Medium difficulty)

```bash
# Create new repo
gh repo create spatial-lab --public
git clone https://github.com/yourusername/spatial-lab.git
cd spatial-lab

# Copy source
cp -r /path/to/NOUS/src/spatial_lab/ ./spatial_lab/

# Copy tests
mkdir -p tests/
cp /path/to/NOUS/test_spatial_lab*.py tests/
cp /path/to/NOUS/demo_spatial_lab.py tests/

# Copy docs
mkdir -p docs/
cp /path/to/NOUS/SPATIAL_LAB_*.md docs/

# Update imports
find spatial_lab/ tests/ -name "*.py" -type f -exec \
  sed -i 's/from src\.spatial_lab\./from spatial_lab./g' {} \;

# Create requirements.txt
cat > requirements.txt << 'EOF'
atroposlib>=0.2.1
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
google-generativeai>=0.3.0
transformers>=4.20.0
wandb>=0.12.0
EOF

# Install and test
pip install -r requirements.txt
pytest tests/ -v

# Commit
git add .
git commit -m "Initial commit: Spatial Lab warehouse robotics"
git push origin main
```

**Verification:**
```python
# Test basic import
from spatial_lab.experiment_runner import SpatialLabExperiment
experiment = SpatialLabExperiment(config="basic_warehouse")
print("✅ Spatial Lab works!")
```

---

### **Week 5: Separate LLM Society** (Hardest)

```bash
# CRITICAL: Ensure gcp_deployment/ is already deleted

# Create new repo
gh repo create llm-society --public
git clone https://github.com/yourusername/llm-society.git
cd llm-society

# Copy source (minus spatial_lab)
cp -r /path/to/NOUS/src/* ./llm_society/
rm -rf llm_society/spatial_lab/

# Copy tests
mkdir -p tests/
cp /path/to/NOUS/*society*.py tests/
cp /path/to/NOUS/*demo*.py tests/

# Copy docs
mkdir -p docs/
cp /path/to/NOUS/LLM_SOCIETY_*.md docs/
cp /path/to/NOUS/POPULATION_*.md docs/

# Update ALL imports
find llm_society/ tests/ -name "*.py" -type f -exec \
  sed -i 's/from src\./from llm_society./g' {} \;
find llm_society/ tests/ -name "*.py" -type f -exec \
  sed -i 's/import src\./import llm_society./g' {} \;

# Create requirements.txt
cat > requirements.txt << 'EOF'
mesa>=1.0.0
google-generativeai>=0.3.0
anthropic>=0.5.0
numpy>=1.21.0
typer>=0.9.0
rich>=13.0.0
EOF

# Create CLI entry point
cat > llm_society/main.py << 'EOF'
import typer
from llm_society.simulation.society_simulator import SocietySimulator

app = typer.Typer()

@app.command()
def run(agents: int = 2500):
    """Run society simulation."""
    simulator = SocietySimulator(num_agents=agents)
    simulator.run()

if __name__ == "__main__":
    app()
EOF

# Install and test
pip install -r requirements.txt
python llm_society/main.py run --agents 10  # Start small

# Commit
git add .
git commit -m "Initial commit: LLM Society 2500-agent simulation"
git push origin main
```

**Verification:**
```bash
# Test CLI
llm-society run --agents 100

# Test import
python -c "from llm_society.agents.llm_agent import LLMAgent; print('✅ Works!')"
```

---

### **Week 6: Cleanup & Documentation**

#### **Update Each Repository**

**For each repo, create:**

1. **README.md** with quick start
2. **CONTRIBUTING.md** with development guide
3. **ARCHITECTURE.md** with system design
4. **LICENSE** file
5. **.gitignore** file
6. **GitHub Actions** for CI/CD

**Example .github/workflows/test.yml:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

#### **Archive Original NOUS Repository**

```bash
# In original NOUS repo
cat > README.md << 'EOF'
# NOUS (Archived)

⚠️ This monolithic repository has been separated into 4 independent repositories:

1. **[spatial-lab](https://github.com/yourusername/spatial-lab)** - Warehouse Robotics AI
2. **[llm-society](https://github.com/yourusername/llm-society)** - 2,500-Agent Simulation
3. **[amien-research](https://github.com/yourusername/amien-research)** - AI Research Automation
4. **[atroposlib](https://github.com/yourusername/atroposlib)** - RL Training Framework

This repository is archived for historical reference.

See [SEPARATION_STRATEGY.md](SEPARATION_STRATEGY.md) for details.
EOF

git add README.md
git commit -m "Archive repository - separated into 4 independent repos"
git push origin main

# Archive the repository on GitHub
gh repo archive yourusername/NOUS
```

---

## ✅ VERIFICATION CHECKLIST

### **For Each Repository:**

#### **Code Quality**
- [ ] All imports work correctly
- [ ] No references to `src.` or other repos
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Linting passes: `flake8 .`
- [ ] Type checking passes: `mypy .` (if using types)

#### **Dependencies**
- [ ] `requirements.txt` is complete
- [ ] No dependencies on other NOUS systems (except Atroposlib via pip)
- [ ] All external APIs work (Gemini, OpenAI, etc.)
- [ ] Package installs cleanly: `pip install -e .`

#### **Documentation**
- [ ] README.md with quick start
- [ ] CONTRIBUTING.md with dev guidelines
- [ ] ARCHITECTURE.md with system design
- [ ] All API endpoints documented (if applicable)
- [ ] Examples work

#### **Infrastructure**
- [ ] CI/CD pipeline works (GitHub Actions)
- [ ] Tests run automatically on PR
- [ ] Docker builds successfully (if applicable)
- [ ] Deployment scripts work

#### **Git Hygiene**
- [ ] No large files committed (use Git LFS if needed)
- [ ] `.gitignore` configured properly
- [ ] Clean commit history
- [ ] Tagged with v1.0.0

---

## 📊 SUCCESS METRICS

### **Before Separation**
- **Repositories:** 1 monorepo
- **Total Files:** ~600
- **Duplication:** 37% (150+ files)
- **Clear Ownership:** None
- **Independent Deployment:** Impossible
- **Maintenance Complexity:** Very High

### **After Separation**
- **Repositories:** 4 independent repos
- **Total Files:** ~450 (25% reduction via deduplication)
- **Duplication:** 0%
- **Clear Ownership:** Each repo has clear purpose
- **Independent Deployment:** Each deployable separately
- **Maintenance Complexity:** Low

### **Benefits Achieved**
✅ **Clarity** - Each repo has single, clear purpose
✅ **Independence** - Deploy and version independently
✅ **Maintainability** - Smaller, focused codebases
✅ **Team Velocity** - Parallel development possible
✅ **Reduced Complexity** - No cross-system dependencies

---

## 🚨 RISKS & MITIGATION

### **Risk 1: Breaking Changes During Separation**
**Mitigation:**
- Tag current state: `git tag pre-separation`
- Test each repo independently before archiving original
- Keep original repo for 6 months as backup

### **Risk 2: Forgotten Dependencies**
**Mitigation:**
- Run full test suite in each repo
- Check all imports with: `python -m compileall .`
- Use dependency checker: `pipdeptree`

### **Risk 3: Documentation Drift**
**Mitigation:**
- Cross-link repositories in READMEs
- Maintain SEPARATION_STRATEGY.md as reference
- Update package discovery documentation

### **Risk 4: Lost Git History**
**Mitigation:**
- Keep original NOUS repo archived
- Use `git log --follow` to track file origins
- Document separation in each repo's README

---

## 💡 RECOMMENDATIONS

### **Do Separate If:**
✅ You want independent deployment
✅ You have separate teams for each system
✅ You want clearer ownership boundaries
✅ You want faster CI/CD pipelines
✅ You want to reduce complexity

### **Don't Separate If:**
❌ Systems are still under heavy development
❌ There's significant code sharing between systems
❌ You have a very small team (<3 people)
❌ You need frequent cross-system changes

### **For NOUS Repository:**
**Recommendation: ✅ SEPARATE**

**Reasoning:**
1. Systems are mature and independent
2. Minimal code sharing (only Atroposlib dependency)
3. 37% duplication to eliminate
4. Clear system boundaries
5. Different deployment targets

---

## 📞 FINAL THOUGHTS

The NOUS repository contains **4 excellent, independent systems** that deserve their own homes. The separation will:

- **Eliminate 150+ duplicate files** (37% reduction)
- **Enable independent deployment** of each system
- **Improve maintainability** with focused codebases
- **Clarify ownership** and responsibilities
- **Accelerate development** with parallel teams

The separation is **medium complexity** - mostly moving files and updating imports. The hardest part is the LLM Society repo due to the `gcp_deployment/` duplicate that must be deleted first.

**Recommended Execution Order:**
1. Week 1: Preparation + delete duplicates
2. Week 2: AMIEN Research (easiest, builds confidence)
3. Week 3: Verify Atroposlib (already done)
4. Week 4: Spatial Lab (medium, has one dependency)
5. Week 5: LLM Society (hardest, but achievable)
6. Week 6: Cleanup + documentation

**Total Time:** 6 weeks
**Total Effort:** ~40-60 hours
**Expected Benefit:** Transformational improvement in maintainability

---

**Document Version:** 1.0
**Last Updated:** November 15, 2025
**Status:** Ready for Execution
