# LLM Lab: Prompt Engineering
# Supply Chain Optimization Domain

## Project Overview
This lab investigates how prompt phrasing, structure, and constraints influence LLM response quality for engineering contexts.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Gemini API key
export GOOGLE_API_KEY="your-api-key-here"

# 3. Run the evaluation notebook
jupyter notebook notebooks/prompt_evaluation.ipynb
```

## Project Structure

```
LLM_Lab_Prompt_Engineering/
├── config/
│   └── experiment_config.yaml    # Reproducibility settings
├── src/
│   ├── llm_clients.py            # Gemini API wrapper
│   ├── prompts.py                # Prompt variant loader
│   ├── evaluator.py              # Metrics and scoring
│   └── visualizations.py         # Charts and plots
├── notebooks/
│   └── prompt_evaluation.ipynb   # Main evaluation notebook
├── results/                      # Generated outputs
├── docs/
│   ├── team_report.md            # 4-page report template
│   └── best_practices.md         # 1-page summary
└── requirements.txt
```

## Team Roles
- **Prompt Architect** – Designs and iterates on prompt variants
- **Evaluation Engineer** – Handles metrics and quantitative analysis
- **Safety & Mitigation Analyst** – Identifies failures and proposes fixes
- **MLOps Integrator** – Manages config, reproducibility, visualization
- **Technical Communicator** – Writes report and documentation

## Configuration
All experiment parameters are in `config/experiment_config.yaml` for reproducibility.
