import os
import json
import pyperclip

from datetime import datetime
from dotenv import load_dotenv
from ollama import chat
from textwrap import dedent


load_dotenv()

VAULT_PATH = os.getenv("VAULT_PATH")

def read_clipboard():
    content = pyperclip.paste()
    if content:
        print(f"--- Content: \n {content} \n ---")
    else:
        print("No content.")
    return content

def load_prompt():
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return f.read()
 

def call_llm(raw_text):

    print(f"--- Calling LLM --- \n")

    prompt = load_prompt()

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
        

def create_markdown(data, raw_text):

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S (UTC%z)")
    title = data.get("title", "Untitled")
    clean_text = data.get("clean_text", "")
    tags = data.get("tags", [])

    obsidian_links = " ".join([f"[[{t}]]"for t in tags])

    content = dedent(
        f"""
        created: {timestamp}
        links: {obsidian_links}


        {clean_text}
        """
    )
    return title, content

def save(title, content):
    filename = f"{title}.md"
    os.makedirs(VAULT_PATH, exist_ok=True)
    full_path = os.path.join(VAULT_PATH, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    

    




def main():

    raw_text = read_clipboard()
    
    data = call_llm(raw_text)


    # dummy = {'title': 'Europe Hits Record Russian LNG Imports Before Banning It', 'clean_text': 'Europe Just Hit Record Russian LNG Imports Right Before Banning It In January 2026 the EU imported 2.276 billion cubic meters of Russian LNG the highest volume ever recorded The twist Just weeks earlier Brussels formally approved a complete ban on Russian LNG starting January 2027 While European officials draw red lines on paper energy realities tell a different story Russia remains a critical supplier as Europe scrambles for alternatives with total LNG imports up 6 year-over-year Can Europe really quit Russian energy or is this ban just political theater that ll crash against economic reality', 'tags': ['EU', 'Russia', 'Energy']}

    title, content = create_markdown(data, raw_text)

    save(title, content)






if __name__ == "__main__":
    main()
