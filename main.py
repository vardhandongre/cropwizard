# main.py

import sys
import os
import json
import yaml
import random
import time
import requests
import uuid
import argparse

from openai import OpenAI


from prompt import generate_questions_from_topic, generate_dialog_prompt

# First we need to generate a list of questions from a list of topics
# Once the questions are generated, we can use the questions to generate a dialog
def main(args):
    print("Generating questions for the dialog")
    file_path = args.file_path
    num_of_questions = args.num_of_questions
    q_model = args.q_model
    d_model = args.d_model
    num_of_turns = args.num_of_turns
    q_output_path = args.q_output_path
    d_output_path = args.d_output_path

    questions = {}
    # Load the topic json file
    with open(file_path, 'r') as file:
        topics = json.load(file)
        topics = topics.get("goals", [])
        for topic in topics:
            unique_id = str(uuid.uuid4())
            print(f"Generating questions for ID: {unique_id} - topic: {topic}")
            response = generate_questions_from_topic(topic, q_model, num_of_questions=num_of_questions)
            questions[unique_id] = [response]
            print(f"Questions generated for ID: {unique_id} - topic: {topic}")
            time.sleep(0.5)
        # save the questions to a json file
        print("Saving the questions to a json file")
        print(questions)
        # with open(f"./questions_{}.yaml".format(q_model), 'w') as file:
        #     yaml.dump(questions, file)
        with open(f"{q_output_path}/questions_{q_model}_{num_of_questions}.json", 'w') as file:
            yaml.dump(questions, file)

            

def setup_args():
    parser = argparse.ArgumentParser(description = "Generate conversational data")
    parser.add_argument("--file_path", type = str, default = "./topics.json", help = "Path to the topics json file")
    parser.add_argument("--q_model", type = str, default = "CropWizard 1.5", help = "Model to use for generating questions")
    parser.add_argument("--d_model", type = str, default= "CropWizard 1.5", help = "Model to use for generating dialog")
    parser.add_argument("--num_of_questions", type = int, default = 10, help = "Number of questions to generate for each topic")
    parser.add_argument("--num_of_turns", type = int, default = 6, help = "Number of turns to generate for each dialog")
    parser.add_argument("--q_output_path", type = str, default = "./", help = "Path to save the generated questions")
    parser.add_argument("--d_output_path", type = str, default = "./", help = "Path to save the generated dialog")
    return parser.parse_args()

if __name__ == "__main__":
    args = setup_args()
    main(args)

# Example usage:
# python main.py --file_path ./topics.json --q_model "CropWizard 1.5" --d_model "CropWizard 1.5" --num_of_questions 10 --num_of_turns 6 --q_output_path ./ --d_output_path ./