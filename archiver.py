import os
import datetime
import json
import pyperclip
import re

from dotenv import load_dotenv
from ollama import chat


load_dotenv()

VAULT_PATH = os.getenv("VAULT_PATH")

def read_clipboard():
    content = pyperclip.paste()
    if content:
        print(content)
    else:
        print("NOT")
    return content

def edit_text(raw_text):
    print("-> Calling LLM")
    prompt = """
        You are an expert archiver.
        1. TITLE: Create a factual, concise title (max 8 words).
        2. CLEAN: Remove emojis and hashtags (#Tag) from the text. Fix spacing. Keep punctuation and meaning identical.        
        3. TAGS: Analyze the content to generate 3-5 high-level conceptual tags. Could be countries, organizations, people or general subjects (e.g. 'EU', 'Trump', 'Covid', 'War').
            - CRITICAL: DO NOT copy the hashtags found in the text.
        
        Output strictly valid JSON:
        {
        "title": "The Title",
        "clean_text": "The text...",
        "tags": ["Tag1", "Tag2"]
        }
    """
    try:
        response = chat(
            model = "llama3",
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Analyze this: \n {raw_text[:4000]}"}
            ],
            format = "json",
            options = {"temperature": 0.3}
        )
        json_string = response.message.content
        return json.loads(json_string)
    except Exception as e:
        print(f"*** Error: {e}")
        





def main():

    raw_text = read_clipboard()
    test = edit_text(raw_text)
    print("--- Result: ")
    print(test)



    


if __name__ == "__main__":
    main()
