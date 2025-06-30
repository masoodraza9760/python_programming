import streamlit as st
import pytesseract
import pdf2image
from PyPDF2 import PdfReader
import re
from PIL import Image
import tempfile

# Optional: Set path if not in system PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("UGC NET Score Analyzer (PDF + OCR)")
st.write("Upload your **Response Sheet PDF** and **Answer Key PDF (even scanned)** to calculate your score.")

response_pdf = st.file_uploader("Upload Response Sheet PDF", type="pdf")
answer_pdf = st.file_uploader("Upload Answer Key PDF", type="pdf")

# === Parsing Functions ===

def extract_text_from_response(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def parse_response_text(text):
    pattern = r"Question ID\s*:\s*(\d+).*?Chosen Option\s*:\s*(\d)"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

def extract_text_from_answer_key(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    pages = pdf2image.convert_from_path(tmp_path, dpi=300)
    text = ""
    for img in pages:
        text += pytesseract.image_to_string(img)
    return text

def parse_answer_key_text(text):
    pattern = r"(\d{10})\s+(DROPPED|[1234])"
    return {qid: opt for qid, opt in re.findall(pattern, text)}

def calculate_score(response, answer_key):
    correct = incorrect = dropped = 0
    total = len(answer_key)

    for qid, correct_opt in answer_key.items():
        chosen = response.get(qid)
        if correct_opt.upper() == "DROPPED":
            dropped += 1
        elif chosen is None:
            continue
        elif chosen == correct_opt:
            correct += 1
        else:
            incorrect += 1

    unattempted = total - (correct + incorrect + dropped)
    score = correct * 2
    return {
        "Total Questions": total,
        "Attempted": correct + incorrect,
        "Correct": correct,
        "Incorrect": incorrect,
        "Unattempted": unattempted,
        "Dropped": dropped,
        "Final Score": score
    }

# === Logic ===

if response_pdf and answer_pdf:
    with st.spinner("Processing PDFs..."):
        response_text = extract_text_from_response(response_pdf)
        response_data = parse_response_text(response_text)

        answer_text = extract_text_from_answer_key(answer_pdf)
        answer_key_data = parse_answer_key_text(answer_text)

        result = calculate_score(response_data, answer_key_data)

    st.success("Score calculated successfully!")
    for key, val in result.items():
        st.write(f"**{key}**: {val}")
