import requests
import json
import os

url = "https://chatgpt-42.p.rapidapi.com/conversationllama3"

payload = {
	"messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant as a telegram bot. Your main goal is to help the user with their questions and provide them with the information they need."
        },
		{
			"role": "user",
			"content": "python code to add two numbers"
		}
	],
	"web_access": False
}
headers = {
	"x-rapidapi-key": os.getenv("RAPID_API_KEY"),
	"x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

with open("response.json", "w", encoding="utf-8") as file:
    json.dump(response.json(), file, indent=4, ensure_ascii=False)
