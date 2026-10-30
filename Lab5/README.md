# Lab 5: Static Code Analysis

**Student:** Satyam Goyal  
**SRN:** PES1UG24CS424  
**Assigned program:** Insurance Premium Calculator

## Contents

- `premium_calculator.py` — cleaned calculator.
- `issues.md` — findings and fixes, with original starter line references.
- `reflection.md` — four responses aligned to the handout outcomes; the provided PDF contains no actual reflection questions.
- `run_analysis.sh` — generates Pylint, Bandit, and Flake8 reports for before and after files.
- `before/premium_calculator.py` — unmodified starter file used for baseline analysis.

## Run locally

From this directory, create and activate a virtual environment, then install the assignment's dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the original starter, generate the before/after reports, then run the cleaned program:

```sh
python before/premium_calculator.py
python run_analysis.sh
python premium_calculator.py
```

The analysis script writes six reports to `reports/`: before and after outputs for each tool. Reports are generated locally so they reflect the tool versions installed on your machine.

## Analysis results

The included reports were generated with Python 3.14.2, Pylint 4.1.3, Bandit 1.9.4, and Flake8 7.5.0. The cleaned file scored **10.00/10** in Pylint, Bandit reported **no issues**, and Flake8 reported **no style violations**. The before reports contain the original findings.

## Notes on the cleaned implementation

The code preserves the starter's calculator features and demo while fixing issues recorded in `issues.md`. `defusedxml` is used for XML input. The authorization token is read from the `UNDERWRITER_TOKEN` environment variable and is not included in source. Set `PREMIUM_LOG_FILE` to choose a quote log location.
