## UpGuard Prototype Dashboard

This repository contains a simple prototype for running asset scanners and visualizing risk scores.
The scanners are parallelized using Python's ``concurrent.futures`` to reduce runtime.

### Requirements

- Python 3.8+
- `streamlit`
- Optional scanning dependencies: `nmap`, `Wappalyzer`, and other libraries used in the scanner modules.

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Dashboard

Launch the Streamlit app from the project root:


```bash
streamlit run dashboard/app.py
```

The sidebar allows you to run scanners on a domain or upload a JSON file of risk scores for visualization. All dashboard logic now lives in `dashboard/app.py` for simplicity.

### Running All Scanners from the CLI

You can also execute every scanner from the command line:

```bash
python run_all.py --domain example.com --ports 1-1000 --workers 4
```

Results will be saved under the `data/` directory with timestamped filenames.
