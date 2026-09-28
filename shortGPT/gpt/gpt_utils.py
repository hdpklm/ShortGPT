import json
import os
import re
from time import sleep, time

import openai
import tiktoken
import yaml

from shortGPT.config.api_db import ApiKeyManager


def num_tokens_from_messages(texts, model="gpt-4o-mini"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-4o-mini":  # note: future models may deviate from this
        if isinstance(texts, str):
            texts = [texts]
        score = 0
        for text in texts:
            score += 4 + len(encoding.encode(text))
        return score
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information""")


def extract_biggest_json(string):
    if not string or not isinstance(string, str):
        return None
    candidates = []
    stack = []
    start_idx = None
    for idx, char in enumerate(string):
        if char == '{':
            if not stack:
                start_idx = idx
            stack.append(char)
        elif char == '}' and stack:
            stack.pop()
            if not stack and start_idx is not None:
                candidates.append(string[start_idx:idx+1])
                start_idx = None
    if candidates:
        return max(candidates, key=len)
    return None


def get_first_number(string):
    pattern = r'\b(0|[1-9]|10)\b'
    match = re.search(pattern, string)
    if match:
        return int(match.group())
    else:
        return None


def load_yaml_file(file_path: str) -> dict:
    """Reads and returns the contents of a YAML file as dictionary"""
    return yaml.safe_load(open_file(file_path))


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data

from pathlib import Path

def load_local_yaml_prompt(file_path):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
from openai import OpenAI

def llm_completion(chat_prompt="", system="", temp=0.7, max_tokens=2000, remove_nl=True, conversation=None):
    openai_key = ApiKeyManager.get_api_key("OPENAI_API_KEY")
    gemini_key = ApiKeyManager.get_api_key("GEMINI_API_KEY")
    llm_base_url = ApiKeyManager.get_api_key("LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or os.environ.get("LLM_BASE_URL")
    llm_model = ApiKeyManager.get_api_key("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or os.environ.get("LLM_MODEL")

    if llm_base_url:
        client = OpenAI(
            api_key=openai_key or "lm-studio",
            base_url=llm_base_url
        )
        model = llm_model or "local-model"
    elif gemini_key:
        client = OpenAI( 
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = llm_model or "gemini-2.0-flash-lite-preview-02-05"
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = llm_model or "gpt-4o-mini"
    else:
        client = OpenAI(
            api_key="lm-studio",
            base_url="http://host.docker.internal:1234/v1"
        )
        model = "local-model"
    max_retry = 3
    retry = 0
    error = ""
    for i in range(max_retry):
        try:
            if conversation:
                messages = conversation
            else:
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                if chat_prompt:
                    messages.append({"role": "user", "content": chat_prompt})
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temp,
                timeout=60
                )
            text = response.choices[0].message.content.strip()
            if remove_nl:
                text = re.sub(r'\s+', ' ', text)
            filename = '%s_llm_completion.txt' % time()
            if not os.path.exists('.logs/gpt_logs'):
                os.makedirs('.logs/gpt_logs')
            with open('.logs/gpt_logs/%s' % filename, 'w', encoding='utf-8') as outfile:
                outfile.write(f"System prompt: ===\n{system}\n===\n"+f"Chat prompt: ===\n{chat_prompt}\n===\n" + f'RESPONSE:\n====\n{text}\n===\n')
            return text
        except Exception as oops:
            retry += 1
            print('Error communicating with OpenAI:', oops)
            error = str(oops)
            sleep(1)
    raise Exception(f"Error communicating with LLM Endpoint Completion errored more than error: {error}")