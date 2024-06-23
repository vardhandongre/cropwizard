# Python script to generate prompts using OpenAI's GPT-3 API

from openai import AzureOpenAI 
import os
import json
import random
import time
import sys
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

# set openai api in the environment from the terminal
# export OPENAI_API_KEY="your-api-key" 

# set CropWizard 1.5 model api in the environment from the terminal
# export CROPWIZARD_API = "your-api-key"

# Load the API key from the environment
api_key = os.getenv("AZURE_OPENAI_API_KEY")
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version= "2023-12-01-preview",
    azure_endpoint = "https://gpt-4-uiuc-chat-east-us-2.openai.azure.com/"
)

# Load the CropWizard API key from the environment
cropwizard_api = os.getenv("CROPWIZARD_API")

# Function for openai chat completion using GPT
# @retry(wait_random_exponential(multiplier = 1, max = 40), stop = stop_after_attempt(3))
def chat_completion_request(messages, model):
    try:
        response = client.chat.completions.create(
            model = model,
            messages = messages
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print("Unable to generate response")
        print(f"Exception: {e}")
        return None

# Function to generate prompts for conversation goal generation from cropwizard
def generate_questions_from_topic(topic, model, num_of_questions):
    prompt = "Generate a list of {} questions that a farmer might ask on the following topic: {}. Each question should start with 'startq' and end with 'endq'.".format(num_of_questions, topic)

    if model == "CropWizard 1.5":
        url = "https://uiuc.chat/api/chat-api/chat"
        headers = {
                'Content-Type': 'application/json',
            }
        data = {
            "model": "gpt-4-04-09",
            "messages": [
                {
                    "role": "system",
                    "content": "You are ChatGPT, a helpful assistant. Follow the user's instructions carefully. Respond using markdown.If the question is related to farming in ANY WAY then always answer the question even if the documents are not helpful. Give the users the most helpful response possible as best you can. Remember this: always give a reasonable answer to the users question and never refuse to answer even if you have little information to go on; give an array of helpful answers if necessary. ALWAYS respond with something helpful to answer their questions and propose solutions. ALWAYS provide citations when relevant but don't stack too many citations together.If the user asks an introductory question or greeting along the lines of hello or what can you do? or What's in here? or what is Cropwizard? or similar, then please respond with a warm welcome to Cropwizard, the AI farm assistant chatbot. Tell them that you can answer questions using the entire knowledge base of Extension. Whether you need information on crop management, pest control, or any other farming-related topic, feel free to ask!"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "openai_key": api_key,
            "temperature": 0.7,
            "course_name": "cropwizard-1.5",
            "stream": True,
            "api_key": cropwizard_api
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # print(response.json)
            print(response.text)
            response = [response.text]
        else:
            print("Failed to fetch data. Status Code:", response.status_code)
            print("Response Text:", response.text)
            return ["Failed to fetch data. Status Code:", response.status_code, "Response Text:", response.text]

    else:
        model = "gpt-4-1106-preview"
        messages = []
        messages.append({"role": "system","content": "You are ChatGPT, a helpful assistant. Follow the user's instructions carefully. Respond using markdown.If the question is related to farming in ANY WAY then always answer the question even if the documents are not helpful. Give the users the most helpful response possible as best you can. Remember this: always give a reasonable answer to the users question and never refuse to answer even if you have little information to go on; give an array of helpful answers if necessary. ALWAYS respond with something helpful to answer their questions and propose solutions. ALWAYS provide citations when relevant but don't stack too many citations together.If the user asks an introductory question or greeting along the lines of hello or what can you do? or What's in here? or what is Cropwizard? or similar, then please respond with a warm welcome to Cropwizard, the AI farm assistant chatbot. Tell them that you can answer questions using the entire knowledge base of Extension. Whether you need information on crop management, pest control, or any other farming-related topic, feel free to ask!"})
        messages.append({"role": "user","content": prompt})

        response = chat_completion_request(messages, model)

    return response

def generate_dialog_prompt(goal, model, num_of_turns=6, persona=None):
    if persona:
        persona_desc = "For the farmer, use the following persona: Name: {}, Farm Type: {}, Location: {}, Experience Level: {}.".format(persona["name"], persona["farm_type"], persona["location"], persona["experience"])
        prompt = "Generate a conversation between a farmer and an Agriculture Specialist about the following goal: {}. The conversation must have at least {} turns. {} Only give the conversation and no other text in response.".format(goal, num_of_turns, persona_desc)    
    else:
        prompt = "Generate a conversation between a farmer and an Agriculture Specialist about the following goal: {}, the conversation must have at least {} turns. Only give the conversation and no other text in response.".format(goal, num_of_turns)

    if model == "CropWizard 1.5":
        url = "https://www.uiuc.chat/api/chat-api/chat"
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "model": "gpt-4-04-09",
            "messages": [
                {
                    "role": "system",
                    "content": "You are ChatGPT, a helpful assistant. Follow the user's instructions carefully. Respond using markdown. If the question is related to farming in ANY WAY then always answer the question even if the documents are not helpful. Give the users the most helpful response possible as best you can. Remember this: always give a reasonable answer to the user's question and never refuse to answer even if you have little information to go on; give an array of helpful answers if necessary. ALWAYS respond with something helpful to answer their questions and propose solutions. ALWAYS provide citations when relevant but don't stack too many citations together. If the user asks an introductory question or greeting along the lines of hello or what can you do? or What's in here? or what is Cropwizard? or similar, then please respond with a warm welcome to Cropwizard, the AI farm assistant chatbot. Tell them that you can answer questions using the entire knowledge base of Extension. Whether you need information on crop management, pest control, or any other farming-related topic, feel free to ask!"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "openai_key": api_key,
            "temperature": 0.7,
            "course_name": "cropwizard-1.5",
            "stream": True,
            "api_key": cropwizard_api
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(response.text)
            return [response.text]
        else:
            error_message = f"Failed to fetch data. Status Code: {response.status_code}, Response Text: {response.text}"
            print(error_message)
            return [error_message]

    else:
        model = "gpt-4-1106-preview"
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Follow the user's instructions carefully."},
            {"role": "user", "content": prompt}
        ]

        response = chat_completion_request(messages, model)

    return response