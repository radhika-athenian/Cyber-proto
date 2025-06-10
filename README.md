This repository contains a simple prototype for running asset scanners and visualizing risk scores.
The scanners are built with asynchronous networking. The SSL and technology scanners now leverage `asyncio` to make concurrent requests for much faster execution. A small benchmark script is included to compare sequential and asynchronous modes.

### Requirements

- Python 3.8+
- `streamlit`
- Optional scanning dependencies: `Wappalyzer` and other libraries used in the scanner modules.

Install dependencies:

```bash
pip install -r requirements.txt
```
### Running Tests

Use pytest to execute the unit test suite:

```bash
pytest
```


### Running the Dashboard

Launch the Streamlit app from the project root:


```bash
streamlit run src/dashboard/app.py
```

The sidebar lets you kick off scans on your chosen domain.  Results are displayed in tables with a light theme similar to UpGuard.

### Running All Scanners from the CLI

You can also execute every scanner from the command line:

```bash
python run_all.py --domain example.com --ports 1-100 --workers 100
```

### Benchmarking

You can quickly gauge the benefit of the asynchronous scanners by running:

```bash
python benchmarks/benchmark_scanners.py
```

Results will be saved under the `data/` directory with timestamped filenames.
The folder will be created automatically when you run the scanners, so you don't need to add it manually.

### Risk Score Calculation

Risk scores can be generated in two ways:

1. **Machine Learning Model** (`src/ML/risk_model.py`)
   - Features from port scans, SSL checks and leak detection are fed into a trained model.
   - The model outputs a risk score from 0 to 100 for each subdomain.

2. **Average Calculation** (`src/utils/risk_calculator.py`)
   - When the ML model is not available, individual check scores are averaged to produce an overall risk value.

Once integrated into the dashboard, either approach can be used to populate the tables with calculated risk scores.
