# Technology Context: SF-Bench

## Technology Stack

### Core Language
- **Python 3.10+**: Primary implementation language
- **Type Hints**: All function signatures include type annotations
- **PEP 8 Compliance**: Black formatter, line length 100

### Dependencies

#### Production Dependencies
```
httpx>=0.27.0       # HTTP client for API calls
python-dotenv>=1.0.0 # Environment variable management
tenacity>=8.2.0     # Retry logic implementation
pydantic>=2.0       # Data validation and settings
```

#### Development Dependencies
```
pytest>=8.0.0       # Test framework
pytest-cov>=4.0.0   # Coverage reporting
black>=24.0.0       # Code formatting
isort>=5.13.0       # Import sorting
flake8>=7.0.0       # Linting
mypy>=1.8.0         # Type checking
```

### External Tools

#### Salesforce CLI (sf/sfdx)
- **Version**: Latest stable
- **Purpose**: Scratch org management, deployment, test execution
- **Commands Used**:
  - `sf org create scratch`
  - `sf project deploy start`
  - `sf apex run test`
  - `sf apex run`
  - `sf org delete scratch`

#### Git
- **Purpose**: Repository management, patch application
- **Commands Used**:
  - `git clone`
  - `git apply`
  - `git status`
  - `git checkout`

## Development Environment Setup

### Prerequisites
1. Python 3.10+ installed
2. Salesforce CLI installed and authenticated
3. DevHub org configured
4. API keys for AI providers

### Installation
```bash
# Clone repository
git clone https://github.com/sf-bench/SF-bench.git
cd SF-bench

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.sample .env
# Edit .env with API keys
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ROUTELLM_API_KEY` | Conditional | RouteLLM provider API key |
| `OPENROUTER_API_KEY` | Conditional | OpenRouter provider API key |
| `GOOGLE_API_KEY` | Conditional | Google AI provider API key |
| `ANTHROPIC_API_KEY` | Conditional | Anthropic provider API key |

At least one provider API key is required for evaluation.

## Technical Constraints

### Salesforce Platform Limits
- **Daily Scratch Org Limit**: Varies by DevHub edition (typically 6-200/day)
- **Active Scratch Org Limit**: Varies by edition
- **Storage Limits**: 200MB data storage per scratch org
- **Governor Limits**: 100 SOQL queries, 150 DML statements per transaction

### API Rate Limits
- AI provider rate limits vary by plan
- Salesforce API limits vary by edition
- Implement exponential backoff for all API calls

### Execution Time Constraints
- Scratch org creation: 30-120 seconds
- Deployment: 10-60 seconds depending on complexity
- Test execution: 10-300 seconds depending on test count
- Total task time: 2-10 minutes typical

## Directory Structure

```
SF-bench/
├── sfbench/                 # Core evaluation engine
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── engine.py           # BenchmarkEngine orchestrator
│   ├── main.py             # CLI entry point
│   ├── runners/            # Task-specific runners
│   │   ├── apex_runner.py
│   │   ├── lwc_runner.py
│   │   ├── flow_runner.py
│   │   └── ...
│   ├── utils/              # Utility modules
│   │   ├── ai_agent.py     # AI provider integration
│   │   ├── checkpoint.py   # Checkpoint management
│   │   ├── git.py          # Git operations
│   │   ├── preflight.py    # Preflight validation
│   │   ├── sfdx.py         # Salesforce CLI wrapper
│   │   └── ...
│   └── validators/         # Validation logic
├── scripts/                # Evaluation scripts
│   ├── evaluate.py         # Main evaluation entry
│   └── ...
├── data/                   # Task definitions
│   └── tasks/             # Task JSON files
├── tests/                  # Test suite
├── docs/                   # GitHub Pages documentation
└── results/               # Evaluation results (git-ignored)
```

## Build and Deployment

### Local Development
```bash
# Run tests
pytest

# Run linting
flake8 sfbench/
black --check sfbench/
isort --check sfbench/

# Run type checking
mypy sfbench/
```

### Running Evaluations
```bash
# With preflight checks
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json

# With functional validation
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json --functional
```

### Documentation
- GitHub Pages: `docs/` directory
- Build: Jekyll via GitHub Actions
- Deploy: Automatic on push to main
