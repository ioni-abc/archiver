import os
import logging
import re
import pyperclip
from datetime import datetime
from dotenv import load_dotenv
from ollama import chat, RequestError, ResponseError
from textwrap import dedent
from json import loads, JSONDecodeError


load_dotenv()
VAULT_PATH = os.getenv("VAULT_PATH")
logging.basicConfig(level=logging.INFO, format="%(message)s")

def read_clipboard():
    content = pyperclip.paste()
    if content:
        logging.info(f"--- Content: \n\n {content} \n")
    else:
        logging.info("No content.")
    return content


def load_prompt():
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return f.read()
 

def call_llm(raw_text):

    logging.info("--- Calling LLM. \n")
    result = {"title": "Untitled", "tags": []}
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
        json_string = response["message"]["content"]
        result = loads(json_string)
    except RequestError as e:
        logging.error(e)
    except ResponseError as e:
        logging.error(e)
    except JSONDecodeError as e:
        logging.error(e)
    return result

def create_markdown(data, raw_text: str):

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S (UTC%z)")
    title = data.get("title", "Untitled")
    clean_text = data.get("clean_text", "")

    tags = data.get("tags", [])
    obsidian_links = " ".join([f"[[{t}]]"for t in tags])
    content = f"\n created: {timestamp} \n links: {obsidian_links} \n\n\n {raw_text}"

    # content = dedent(
    #     f"""
    #     created: {timestamp.lstrip()}
    #     links: {obsidian_links.lstrip()}


    #     {raw_text.lstrip()}
    #     """
    # )
    
    return title, content


def save(title, content):

    logging.info("\n --- Saving file. \n")
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    filename = f"{safe_title}.md"
    try:
        os.makedirs(VAULT_PATH, exist_ok=True)
        full_path = os.path.join(VAULT_PATH, filename)
        logging.info(f"Saving to: {full_path}")
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("File saved.")
    except OSError as e:
        logging.error(f"Could not save file: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    

def main():
    raw_text = read_clipboard()
    if raw_text:
        data = call_llm(raw_text)
        title, content = create_markdown(data, raw_text)
        save(title, content)
    else:
        logging.warning("\n No content provided.")


if __name__ == "__main__":
    main()
