import os
import openai
import json
import re
from PyPDF2 import PdfReader

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.Client()

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file without skipping any pages.
    """
    text = ""
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        for i in range(num_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text
        # Replace multiple newlines and tabs with a single space
        text = re.sub(r'[\n\t]+', ' ', text)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def extract_items(text, item_type):
    """
    Use OpenAI's GPT-4 to extract questions or answers from text without filtering.
    """
    items = []
    prompt = (
        f"Extract all the {item_type} from the following text, including their associated numbering "
        f"(e.g., Q1a, Q1b, etc.):\n\n{text}\n\n"
        f"Provide each {item_type[:-1]} separated by '<END>'."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    'role': 'system',
                    'content': f'You are an assistant that extracts {item_type} from text.',
                },
                {'role': 'user', 'content': prompt},
            ],
            temperature=0,
            n=1,
            stop=None,
        )
        content = response.choices[0].message.content.strip()
        extracted_items = content.split('<END>')
        items.extend([item.strip() for item in extracted_items if item.strip()])
    except Exception as e:
        print(f"Error extracting {item_type}: {e}")

    return items

def main():
    base_path = r'C:\Users\OKH20\OneDrive - University of Canterbury\Projects\KORA\KORAedu\KORAQuestionGrabber\PapersPDF\NCEAL3CALC'  # Update this path to your actual path
    topics = ['91577_CMPLX', '91578_DIFF', '91579_INT']
    data = []

    for topic in topics:
        exams_path = os.path.join(base_path, topic, 'exams')
        schedules_path = os.path.join(base_path, topic, 'schedules')

        exam_files = sorted([f for f in os.listdir(exams_path) if f.endswith('.pdf')])
        schedule_files = sorted([f for f in os.listdir(schedules_path) if f.endswith('.pdf')])

        for exam_file, schedule_file in zip(exam_files, schedule_files):
            exam_pdf_path = os.path.join(exams_path, exam_file)
            schedule_pdf_path = os.path.join(schedules_path, schedule_file)

            print(f"Processing {exam_file} and {schedule_file}")

            exam_text = extract_text_from_pdf(exam_pdf_path)
            schedule_text = extract_text_from_pdf(schedule_pdf_path)

            if not exam_text or not schedule_text:
                print(f"Skipping {exam_file} due to empty text.")
                continue

            questions = extract_items(exam_text, 'questions')
            answers = extract_items(schedule_text, 'answers')

            if len(questions) != len(answers):
                print(f"Warning: Number of questions and answers do not match for {exam_file}.")
                min_length = min(len(questions), len(answers))
                questions = questions[:min_length]
                answers = answers[:min_length]

            for idx, (q, a) in enumerate(zip(questions, answers), start=1):
                # Extract the question number if present
                q_number_match = re.match(r'(Q\d+[a-zA-Z]?[:.)]?)', q)
                a_number_match = re.match(r'(A\d+[a-zA-Z]?[:.)]?)', a)

                q_number = q_number_match.group(1) if q_number_match else f'Q{idx}'
                a_number = a_number_match.group(1) if a_number_match else f'A{idx}'

                print(f"Reading question {q_number}: {q}")
                print(f"Reading answer {a_number}: {a}")

                data.append({
                    "query": q,
                    "type": "NCEA",
                    "answer": a
                })

    # Save to JSON
    with open('exam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Data extraction complete. Output saved to exam_data.json.")

if __name__ == "__main__":
    main()
