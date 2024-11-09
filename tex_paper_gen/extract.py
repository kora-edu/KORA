from marker.convert import convert_single_pdf
from marker.models import load_all_models
import re
import json

# Paths for question and answer PDFs
question_pdf_path = './pdfs/questions.pdf'
answer_pdf_path = './pdfs/answers.pdf'

# Regular expression to match question numbers like "1a", "1b", etc.
question_pattern = re.compile(r"(\d+[a-z]*)")

# Load Marker models
models = load_all_models()

# Function to process the PDF with Marker and extract structured text
def extract_text_from_pdf_with_marker(pdf_path):
    full_text, images, out_meta = convert_single_pdf(pdf_path, models)
    return full_text

# Extract structured text from questions and answers PDFs using Marker
question_text_data = extract_text_from_pdf_with_marker(question_pdf_path)
answer_text_data = extract_text_from_pdf_with_marker(answer_pdf_path)

# Function to parse answers and format with LaTeX for mathematical expressions
def parse_answers(text_data):
    answers = {}
    current_question = None
    current_level = None

    # Split the markdown text by lines
    for line in text_data.splitlines():
        # Match question numbers like "1a", "2b" to assign answers
        question_match = question_pattern.match(line)
        if question_match:
            current_question = question_match.group(1)
            answers[current_question] = {
                "achievement": "",
                "merit": "",
                "excellence": ""
            }
        elif "Achievement" in line:
            current_level = "achievement"
        elif "Merit" in line:
            current_level = "merit"
        elif "Excellence" in line:
            current_level = "excellence"
        elif current_question and current_level:
            # Append answer content with LaTeX formatting where applicable
            answers[current_question][current_level] += f"{line} "

    # Convert mathematical expressions to LaTeX format for JSON output
    for question, levels in answers.items():
        for level, answer in levels.items():
            # Replace mathematical expressions with LaTeX expressions
            answers[question][level] = answer.replace("^", r"^{\circ}") \
                                              .replace("sqrt", r"\sqrt{}") \
                                              .replace("pi", r"\pi")
    return answers

# Extract and format answers from the markdown text output of Marker
extracted_answers = parse_answers(answer_text_data)

# Build the JSON structure with questions and answers
questions_json = {}
for question_id, answer_data in extracted_answers.items():
    questions_json[question_id] = {
        "question": "",  # Leave question blank as requested
        "answer": answer_data  # Answer with LaTeX formatted strings
    }

# Save the output JSON file
output_json_path = 'questions_with_answers.json'
with open(output_json_path, 'w') as f:
    json.dump(questions_json, f, indent=4)

print(f"JSON file saved at: {output_json_path}")
