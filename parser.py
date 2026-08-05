"""
Resume Parser Agent
Extracts structured data from a resume (PDF or DOCX) using the Claude API,
then writes the result to a CSV file that mimics a contractor-onboarding "board."
"""

import os
import json
import csv
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
from docx import Document

# Load API key from .env
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_resume_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def parse_resume_with_claude(resume_text: str) -> dict:
    """Send resume text to Claude and get back structured JSON fields."""

    prompt = f"""Extract structured information from this resume. Return ONLY valid JSON
(no markdown, no explanation) with exactly these fields:

{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "most_recent_title": "",
  "most_recent_company": "",
  "years_experience_estimate": "",
  "top_skills": [],
  "education": ""
}}

Resume text:
{resume_text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        raise ValueError("Claude declined to process this resume. Try a different file.")

    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if Claude adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json\n", "", 1)

    return json.loads(raw_text)


def append_to_board_csv(record: dict, csv_path: str = "onboarding_board.csv"):
    """Append a parsed record to the mock onboarding board CSV."""
    file_exists = Path(csv_path).exists()

    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def process_resume(file_path: str):
    print(f"Reading resume: {file_path}")
    text = extract_resume_text(file_path)

    print("Sending to Claude for parsing...")
    parsed = parse_resume_with_claude(text)

    # top_skills is a list — join it for clean CSV storage
    parsed["top_skills"] = ", ".join(parsed.get("top_skills", []))

    append_to_board_csv(parsed)
    print("Done. Extracted data:")
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    # Change this to the path of a resume file you want to test with
    test_file = "sample_resume.pdf"
    process_resume(test_file)