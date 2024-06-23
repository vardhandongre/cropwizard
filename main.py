import sys
import os
import json
import time
import uuid
import random
import argparse
from prompt import generate_questions_from_topic, generate_dialog_prompt

# Cleaning up response 
def clean_response(response_text):
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove the initial "```json"
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove the ending "```"
    return response_text.strip()

# Getting just the questions from the response
def extract_questions(response_text):
    questions = []
    while "startq" in response_text and "endq" in response_text: # Instructed model to add special keywords to indicate start and end of generated text
        start_index = response_text.index("startq") + len("startq")
        end_index = response_text.index("endq")
        question = response_text[start_index:end_index].strip()
        questions.append(question)
        response_text = response_text[end_index + len("endq"):]
    return questions

def generate_questions(file_path, q_model, num_of_questions, q_output_path):
    questions = {}
    # Load the topic json file
    with open(file_path, 'r') as file:
        topics = json.load(file)
        topics = topics.get("goals", [])
        for topic in topics:
            unique_id = str(uuid.uuid4())
            print(f"Generating questions for ID: {unique_id} - topic: {topic}")
            success = False
            attempts = 0
            max_attempts = 5
            while not success and attempts < max_attempts:
                try:
                    response = generate_questions_from_topic(topic, q_model, num_of_questions=num_of_questions)
                    if response:
                        clean_text = clean_response(response[0])
                        questions_list = extract_questions(clean_text)
                        questions[unique_id] = questions_list
                        success = True
                    else:
                        print(f"No response received for topic: {topic}")
                        questions[unique_id] = ["No response received"]
                        break
                except Exception as e:
                    print(f"Attempt {attempts+1} failed for topic: {topic} with error: {e}")
                    attempts += 1
                    time.sleep(20)  # Wait for 20 seconds before retrying
            if not success:
                questions[unique_id] = [f"Failed to generate questions after {max_attempts} attempts"]
            print(f"Questions generated for ID: {unique_id} - topic: {topic}")
            time.sleep(0.5)
    # Save the questions to a json file
    print("Saving the questions to a file")
    with open(f"{q_output_path}/questions_{q_model}_{num_of_questions}.json", 'w') as file:
        json.dump(questions, file, indent=4)

def generate_dialogues(q_file, d_model, num_of_turns, d_output_path, use_personas=False, personas_file=None):
    dialogues = {}

    # Load personas from file if use_personas is True
    if use_personas and personas_file:
        with open(personas_file, 'r') as file:
            personas_data = json.load(file)
            farmer_personas = personas_data.get("personas", [])
    else:
        farmer_personas = []

    # Load the questions json file
    with open(q_file, 'r') as file:
        questions = json.load(file)
        for unique_id, q_list in questions.items():
            print(f"Generating dialogues for ID: {unique_id}")
            dialogue_texts = []
            for question in q_list:
                attempt = 0
                success = False
                while attempt < 5 and not success:
                    if use_personas and farmer_personas:
                        persona = random.choice(farmer_personas)
                        dialogue = generate_dialog_prompt(question, d_model, num_of_turns, persona)
                    else:
                        dialogue = generate_dialog_prompt(question, d_model, num_of_turns)
                    if dialogue:
                        dialogue_texts.append(dialogue)
                        success = True
                    else:
                        attempt += 1
                        time.sleep(20)  # Wait for 20 seconds before retrying
                if not success:
                    print(f"No response received for question: {question}")
                    dialogue_texts.append(f"No response received\n\nFailed to generate dialogue after {attempt} attempts")
            dialogues[unique_id] = dialogue_texts
            print(f"Dialogues generated for ID: {unique_id}")
            time.sleep(0.5)
    # Save the dialogues to a json file
    print("Saving the dialogues to a file")
    if use_personas:
        with open(f"{d_output_path}/dialogues_{d_model}_{num_of_turns}_with_personas.json", 'w') as file:
            json.dump(dialogues, file, indent=4)
    else:
        with open(f"{d_output_path}/dialogues_{d_model}_{num_of_turns}.json", 'w') as file:
            json.dump(dialogues, file, indent=4)

def setup_args():
    parser = argparse.ArgumentParser(description="Generate questions and dialogues from topics")
    parser.add_argument("--mode", type=str, required=True, help="Mode to run: 'questions' or 'dialogues'")
    parser.add_argument("--file_path", type=str, default="./topics.json", help="Path to the topics json file")
    parser.add_argument("--q_model", type=str, default="CropWizard 1.5", help="Model to use for generating questions")
    parser.add_argument("--d_model", type=str, default="CropWizard 1.5", help="Model to use for generating dialogues")
    parser.add_argument("--num_of_questions", type=int, default=10, help="Number of questions to generate for each topic")
    parser.add_argument("--num_of_turns", type=int, default=6, help="Number of turns to generate for each dialogue")
    parser.add_argument("--q_output_path", type=str, default="./", help="Path to save the generated questions")
    parser.add_argument("--d_output_path", type=str, default="./", help="Path to save the generated dialogues")
    parser.add_argument("--q_file", type=str, default=None, help="Path to the questions file for generating dialogues")
    parser.add_argument("--use_personas", action='store_true', help="Flag to use predefined farmer personas for dialogues")
    parser.add_argument("--personas_file", type=str, default="./personas.json", help="Path to the personas json file")
    return parser.parse_args()

if __name__ == "__main__":
    args = setup_args()
    if args.mode == "questions":
        generate_questions(args.file_path, args.q_model, args.num_of_questions, args.q_output_path)
    elif args.mode == "dialogues":
        if not args.q_file:
            print("Error: --q_file argument is required for 'dialogues' mode")
            sys.exit(1)
        generate_dialogues(args.q_file, args.d_model, args.num_of_turns, args.d_output_path, args.use_personas, args.personas_file)
    else:
        print("Error: Invalid mode. Use 'questions' or 'dialogues'.")
        sys.exit(1)

# Example usage:
# python3 main.py --mode questions --file_path ./topics.json --q_model "CropWizard 1.5" --num_of_questions 10 --q_output_path ./  # Generate questions
# python3 main.py --mode dialogues --q_file ./"questions_CropWizard 1.5_10.json" --d_model "CropWizard 1.5" --num_of_turns 6 --d_output_path ./ --use_personas --personas_file ./personas.json  # Generate dialogues with personas
# python3 main.py --mode dialogues --q_file ./"questions_CropWizard 1.5_10.json" --d_model "CropWizard 1.5" --num_of_turns 6 --d_output_path ./  # Generate dialogues without personas