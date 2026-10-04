# SmartBrief AI – Abstractive Summarization System

IR Mini Project: **Develop an Abstractive Summarization System**

## Features
- Transformer-based abstractive summarization
- Short / Medium / Detailed modes
- TXT file upload
- Keyword extraction
- Word-count and compression analysis
- SQLite history
- Download generated summary
- Modern responsive Flask UI

## Run
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

### First run
The Hugging Face model `sshleifer/distilbart-cnn-12-6` is downloaded automatically. Internet is needed only for the first model download. After that it is cached locally.

## Project title
**Develop a Abstractive Summarization System**

## Model
DistilBART CNN/DailyMail fine-tuned summarization model.

## Academic note
Abstractive summarization generates a new summary using a sequence-to-sequence Transformer model. The system also provides basic information-retrieval-oriented preprocessing and keyword extraction for analysis.
