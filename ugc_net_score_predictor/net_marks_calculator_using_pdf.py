import re
import PyPDF2

def extract_text_from_pdf(path):
    with open(path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        return "\n".join(page.extract_text() for page in pdf.pages)

def parse_response_sheet(text):
    """
    Extracts response as {question_id: chosen_option}
    """
    pattern = r"Question ID\s*:\s*(\d+).*?Chosen Option\s*:\s*(\d)"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

def parse_answer_key(text):
    """
    Extracts answer key as {question_id: correct_option}
    Ignores dropped questions marked with D
    """
    pattern = r"(\d{10})\s+([1234D])"
    return {qid: opt for qid, opt in re.findall(pattern, text) if opt in '1234'}

def calculate_marks(response_dict, answer_key_dict):
    correct = incorrect = dropped = unattempted = 0
    all_question_ids = set(answer_key_dict.keys())

    for qid in all_question_ids:
        correct_option = answer_key_dict[qid]
        chosen_option = response_dict.get(qid)

        if chosen_option is None:
            unattempted += 1
        elif chosen_option == correct_option:
            correct += 1
        else:
            incorrect += 1

    dropped = sum(1 for qid, ans in answer_key_dict.items() if ans == 'D')
    total_questions = len(answer_key_dict)
    score = correct * 2  # +2 for correct, 0 for others

    return {
        "Total Questions": total_questions,
        "Attempted": correct + incorrect,
        "Correct": correct,
        "Incorrect": incorrect,
        "Unattempted": unattempted,
        "Dropped": dropped,
        "Final Score": score
    }

# File paths
response_pdf = "resp.pdf"
answer_pdf = "answ.PDF"

# Process
response_text = extract_text_from_pdf(response_pdf)
answer_key_text = extract_text_from_pdf(answer_pdf)

response_data = parse_response_sheet(response_text)
answer_key_data = parse_answer_key(answer_key_text)

# Calculate result
result = calculate_marks(response_data, answer_key_data)

# Output
print("\nUGC NET Marks Calculation")
print("-" * 30)
for k, v in result.items():
    print(f"{k}: {v}")
