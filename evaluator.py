# script to evaluate synthetic dialogues using LLM
import os
import json
import random
import time
import sys
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai import OpenAI
import anthropic
import argparse

# read the txt filenames from the folder
def read_filenames(folder_path):
    filenames = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filenames.append(filename)
    return filenames

# function to evaluate synthetic dialogues using LLM
def evaluate_dialogues(dialogs, model):
    model = model
    dialogues_folder = dialogs

    # Create the evaluations folder if it doesn't exist
    evaluations_folder = os.path.join(dialogues_folder, 'evaluations')
    if not os.path.exists(evaluations_folder):
        os.makedirs(evaluations_folder)
        print(f"Created evaluations folder at: {evaluations_folder}")

    # Select the model api
    if model == "gpt4":
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(
            api_key=api_key,
        )
        
    elif model == "claude":
        api_key = os.getenv("CLAUDE_API_KEY")
        client = anthropic.Client(api_key)
        model="claude-3-opus-20240229"
    elif model == "CropWizard 1.5":
        api_key = os.getenv("OPENAI_API_KEY")
        cropwizard_api = "uc_5806ac979cae4911a920231ca15abad7"
    else:
        raise ValueError("Invalid model")

    # Evaluate the dialogues
    # Read the dialogues from the txt file 
    dialog_list = read_filenames(dialogues_folder)

    for dialogue in dialog_list:
        dialogue_pth = os.path.join(dialogues_folder, dialogue)
        print("Evaluating dialogues from: ", dialogue)
        with open(dialogue_pth, 'r') as file:
            dialogues_txt = [file.read().replace('\n', ' ')]

            # Evaluate the dialogues
            # Prompt Template
            prompt_template = """
            You are an expert in agriculture and farming practices. I will provide you with a dialogue between a farmer and an agriculture consultant, where each participant's turn is separated by a newline. Your task is to carefully analyze each turn in the dialogue and identify any instances of hallucinations (made-up or fictitious information) or factual inaccuracies related to agriculture and farming practices. For each identified issue, provide a clear explanation of why it is a hallucination or inaccuracy, and if possible, provide the correct information.

            Here is the dialogue:
            {}

            Please provide your analysis and feedback on any hallucinations or factual inaccuracies found in each turn of the dialogue.
            """

            # Generate the prompt
            prompt = prompt_template.format(dialogues_txt[0])

            if model == "gpt4":
                response = client.chat.completions.create(
                    model = "gpt-4-1106-preview",
                    messages = [
                        {
                            "role": "system",
                            "content": prompt,
                        }
                    ],
                    seed = 0,
                )
                # print(response.choices[0].message.content)
                # Save the response to a file
                dialogue_name, _ = os.path.splitext(dialogue)
                evaluation_file_path = os.path.join(evaluations_folder, f"{dialogue_name}_{model}_evaluation.txt")
                with open(evaluation_file_path, 'w') as file:
                    file.write(response.choices[0].message.content)
                    print(f"Analysis saved to: {evaluation_file_path}")

            elif model == "CropWizard 1.5":
                url = "https://www.uiuc.chat/api/chat-api/chat"
                headers = {
                    'Content-Type': 'application/json'
                }
                data = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are ChatGPT, a helpful assistant. Follow the user's instructions carefully. Respond using markdown.If the question is related to farming in ANY WAY then always answer the question even if the documents are not helpful. Give the users the most helpful response possible as best you can. Remember this: always give a reasonable answer to the users question and never refuse to answer even if you have little information to go on; give an array of helpful answers if necessary. ALWAYS respond with something helpful to answer their questions and propose solutions. ALWAYS provide citations when relevant but don't stack too many citations together.If the user asks an introductory question or greeting along the lines of hello or what can you do? or What's in here? or what is Cropwizard? or similar, then please respond with a warm welcome to Cropwizard, the AI farm assistant chatbot. Tell them that you can answer questions using the entire knowledge base of Extension. Whether you need information on crop management, pest control, or any other farming-related topic, feel free to ask!"
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "openai_key": api_key,
                    "temperature": 0.7,
                    "course_name": "cropwizard-1.5",
                    "stream": True,
                    "api_key": cropwizard_api
                }

                response = requests.post(url, headers=headers, json=data)
                # print(response.text)
                if response.status_code == 200:
                    print()
                    # save the response to a file
                    dialogue_name, _ = os.path.splitext(dialogue)
                    evaluation_file_path = os.path.join(evaluations_folder, f"{dialogue_name}_{model}_evaluation.txt")
                    with open(evaluation_file_path, 'w') as file:
                        file.write(response.text)
                        print(f"Analysis saved to: {evaluation_file_path}")
                else:
                    print(f"Failed to receive response for dialogue: {dialogue}, Status Code: {response.status_code}")
                    print(response.text)

            # Add a fixed delay to avoid rate limiting
            time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description="Evaluate synthetic dialogues using LLM")
    parser.add_argument('--dialogues_folder', type=str, required=True, help='Path to the dialogues folder.')
    parser.add_argument('--model', type=str, required=True, help='Model to use for evaluation.')
    args = parser.parse_args()

    evaluate_dialogues(args.dialogues_folder, args.model)

if __name__ == "__main__":
    main()

# Example usage:
# python evaluator.py --dialogues_folder ./dialogues --model gpt4
