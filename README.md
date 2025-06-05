## UpGuard Prototype Dashboard

This repository contains a simple prototype for running asset scanners and visualizing risk scores.
The scanners are built with asynchronous networking and ThreadPool executors to speed up execution.

### Requirements

- Python 3.8+
- `streamlit`
- Optional scanning dependencies: `Wappalyzer` and other libraries used in the scanner modules.

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Dashboard

Launch the Streamlit app from the project root:


```bash
streamlit run dashboard/app.py
```

The sidebar lets you kick off scans on your chosen domain and upload custom risk data.  Results are displayed in tables with a light theme similar to UpGuard.

### Running All Scanners from the CLI

You can also execute every scanner from the command line:

```bash
python run_all.py --domain example.com --ports 1-100 --workers 100
```

Results will be saved under the `data/` directory with timestamped filenames.
