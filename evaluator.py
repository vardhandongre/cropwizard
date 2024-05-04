# script to evalute synthetic dialogues using LLM

import os
import json
import yaml
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
        api_key = os.getenv("CROPWIZARD_API")
    else:
        raise ValueError("Invalid model")

    # Evaluate the dialogues
    # Read the dialogues from the txt file 
    dialog_list = read_filenames(dialogues_folder)

    for dialogue in dialog_list:
        dialogue_pth = os.path.join(dialogues_folder, dialogue)
        print("Evaluating dialogues from: ", dialogue)
        with open(dialogue_pth, 'r') as file:
            # dialogues = file.readlines()
            dialogues_txt = [file.read().replace('\n', ' ')]
            # dialogues = [dialogue.strip() for dialogue in dialogues]
            # print(dialogues_txt)
            # print(len(dialogues_txt))

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
                reponse = client.chat.completions.create(
                    model = "gpt-4-1106-preview",
                    messages = [
                        {
                            "role": "system",
                            "content": prompt,
                        }
                    ],
                    seed = 0,
                )
                # print(reponse.choices[0].message.content)
                # Save the response to a file
                with open(f"{dialogues_folder}/{dialogue}_{model}_evaluation.txt", 'w') as file:
                    file.write(reponse.choices[0].message.content)
                    print(f"Analysis saved to: {dialogue}_{model}_evaluation.txt")
                break

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


