# Engineering Unit Converter

A Python Flask app with HTML and CSS only

## Setup

1. Open this folder in VS Code.
2. Install Flask: `python -m pip install -r requirements.txt`
3. Start: `python app.py`
4. Visit http://127.0.0.1:5000 in your browser.

Eight conversion types, input validation, timestamps, persistent CSV history, and statistics by conversion type.
Conversion records are saved to `conversion_log.csv` beside `app.py`.

For local development only: disable Flask debug mode before deployment.
