from flask import Flask, render_template, request, jsonify, send_file
from transformers import pipeline
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3, os, re, io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "summaries.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

print("Loading summarization model (first run may take a few minutes)...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-xsum-6-6")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            summary TEXT NOT NULL,
            original_words INTEGER,
            summary_words INTEGER,
            compression REAL,
            created_at TEXT
        )""")
init_db()

def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()

def chunks(text, max_words=450):
    words=text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0,len(words),max_words)] or [""]

def summarize_text(text, length="medium"):
    text=clean_text(text)
    if len(text.split()) < 35:
        return text
    params={"short": (35, 70), "medium": (55, 100), "long": (80, 130)}
    min_len,max_len=params.get(length,params["medium"])
    parts=[]
    for c in chunks(text):
        # model has token limits; approximate word-based chunks
        if len(c.split()) < 35:
            parts.append(c)
            continue
        result=summarizer(c, max_length=max_len, min_length=min(min_len, max_len-5),
                          do_sample=False, truncation=True)
        parts.append(result[0]["summary_text"])
    if len(parts)==1:
        return parts[0]
    joined=" ".join(parts)
    if len(joined.split()) > max_len*1.7:
        result=summarizer(joined, max_length=max_len, min_length=min_len,
                          do_sample=False, truncation=True)
        return result[0]["summary_text"]
    return joined

def keyword_extract(text, n=10):
    stop=set("""a an the and or but if then than is are was were be been being to of in on for from with by as at into about over after before between through during this that these those it its they them their he she his her we our you your i me my have has had do does did can could will would should may might must not no yes very more most some any all each both other another such also only own same so too just than""".split())
    words=re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    freq={}
    for w in words:
        if w not in stop:
            freq[w]=freq.get(w,0)+1
    return [w for w,_ in sorted(freq.items(), key=lambda x:(-x[1],x[0]))[:n]]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        text=request.form.get("text","")
        length=request.form.get("length","medium")
        file=request.files.get("file")
        if file and file.filename:
            filename=secure_filename(file.filename)
            if not filename.lower().endswith(".txt"):
                return jsonify({"error":"Only .txt files are supported."}),400
            text=file.read().decode("utf-8", errors="ignore")
        text=clean_text(text)
        if len(text.split()) < 35:
            return jsonify({"error":"Please provide at least 35 words for a meaningful summary."}),400
        summary=summarize_text(text,length)
        ow=len(text.split()); sw=len(summary.split())
        compression=round((1-sw/ow)*100,2) if ow else 0
        keywords=keyword_extract(text)
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""INSERT INTO summaries
                (original_text,summary,original_words,summary_words,compression,created_at)
                VALUES (?,?,?,?,?,?)""",
                (text,summary,ow,sw,compression,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return jsonify({"summary":summary,"original_words":ow,"summary_words":sw,
                        "compression":compression,"keywords":keywords})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/history")
def history():
    with sqlite3.connect(DB_PATH) as con:
        rows=con.execute("""SELECT id,summary,original_words,summary_words,compression,created_at
                            FROM summaries ORDER BY id DESC LIMIT 20""").fetchall()
    return render_template("history.html", rows=rows)

@app.route("/download", methods=["POST"])
def download():
    summary=request.form.get("summary","")
    data=summary.encode("utf-8")
    return send_file(io.BytesIO(data), as_attachment=True,
                     download_name="smartbrief_summary.txt", mimetype="text/plain")

if __name__=="__main__":
    app.run(debug=True)
