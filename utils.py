# utils.py

import fitz  # PyMuPDF
import openai
import re

openai.api_key = "your-openai-key"

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    else:
        return uploaded_file.read().decode("utf-8")

def generate_summary(text):
    prompt = f"Summarize this document in under 150 words:\n{text[:3000]}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def answer_question(document, question):
    prompt = f"Based only on the following content:\n{document[:4000]}\nAnswer this question: {question}. Justify with reference to the document."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    match = re.search(r"Justification:(.*)", content, re.IGNORECASE)
    if match:
        return content.split("Justification:")[0].strip(), match.group(1).strip()
    return content, "Justification not found"

def generate_challenge_questions(document):
    prompt = f"Create 3 logic-based or comprehension questions based on this content:\n{document[:4000]}\n"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    questions = response.choices[0].message.content.strip().split("\n")

    def make_evaluator(q):
        def evaluate(answer):
            eval_prompt = f"Document:\n{document[:3000]}\n\nQuestion: {q}\nUser Answer: {answer}\n\nGive a score out of 10 and justify."
            resp = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": eval_prompt}]
            )
            content = resp.choices[0].message.content.strip()
            score_match = re.search(r"(\d+)/10", content)
            score = int(score_match.group(1)) if score_match else "?"
            return {"score": score, "justification": content}
        return evaluate

    return [{"question": q.strip(), "evaluate": make_evaluator(q.strip())} for q in questions if q.strip()]
