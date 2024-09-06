import json
import openai
import os
import asyncio
from openai import AsyncOpenAI

openai.api_key = os.getenv("OPENAI_KEY")
client = AsyncOpenAI(api_key=openai.api_key)

async def get_response(prompt):
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {'role': 'system', 'content': 'You are a helpful and knowledgeable assistant.'},
                    {'role': 'user', 'content': prompt},
                ]
            ),
            timeout=20
        )
        return response.choices[0].message.content
    except asyncio.TimeoutError:
        print("Request timed out")
        return None
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def load_reference_questions(reference_file):
    with open(reference_file, 'r') as file:
        reference_questions = file.readlines()
    reference_questions = [q.strip() for q in reference_questions if q.strip()]
    return reference_questions

def load_dataset(jsonl_file):
    dataset = []
    with open(jsonl_file, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                dataset.append(data)
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSONDecodeError: {e}")
    return dataset

async def get_similar_questions(reference_questions, target_questions):
    similar_questions = []
    
    for idx, item in enumerate(target_questions):
        question = item.get("instruction", "")
        print(f"Processing question {idx + 1}/{len(target_questions)}: {question}")
        
        for ref_idx, reference_question in enumerate(reference_questions):
            prompt = (
                f"Compare the following target question to a reference question and determine if it has a similar "
                f"sentence structure and style. If similar, respond with 'Yes', otherwise 'No'.\n\n"
                f"Reference Question:\n{reference_question}\n\n"
                f"Target Question:\n{question}\n\n"
            )
            
            response_text = await get_response(prompt)
            if response_text:
                print(f"Response for question {idx + 1}, reference {ref_idx + 1}: {response_text.strip()}")
                if 'Yes' in response_text:
                    similar_questions.append(item)
                    print(f"Match found: {question}")
                    break
            else:
                print(f"No response for question {idx + 1}, reference {ref_idx + 1}")
    
    return similar_questions

async def filter_questions(reference_file, json_file, output_file):
    reference_questions = load_reference_questions(reference_file)
    target_questions = load_dataset(json_file)
    similar_questions = await get_similar_questions(reference_questions, target_questions)
    with open(output_file, 'w') as file:
        json.dump(similar_questions, file, indent=4)
    return similar_questions

def run_async(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func(*args))

reference_file_path = "D:\\KORA\\KORA_REPO_KAHU\\KORA_parser\\returned_questions\\ncea\\nceaDemo.txt"
json_file_path = "D:\\KORA\\KORA_REPO_KAHU\\KORA_downloader\\downloads\\mathsInstruct\\FormattedTrainMathInstruct500.jsonl"
output_file_path = "filtered_similar_questions.json"

similar_questions = run_async(filter_questions, reference_file_path, json_file_path, output_file_path)

if similar_questions:
    print(f"Filtered similar questions saved to {output_file_path}.")
else:
    print("No similar questions found.")
