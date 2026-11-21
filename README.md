# PaystubAnalyzer
Python program that scans a PDF paystub to see how much and what percentage of taxes and benefits are taken out of a paycheck.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python "Paystub Analyzer.py"
```

## Building the macOS app

```bash
pip install -r requirements-build.txt
pyinstaller "Paystub Analyzer.spec"
```

The app is written to `dist/`. Build output is not committed to git: it freezes copies of every
library inside it, which then never receive security fixes. Publish the built app as a GitHub Release
asset instead, and rebuild whenever `requirements.txt` changes.
