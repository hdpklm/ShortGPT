from shortGPT.gpt import gpt_utils
import json

def generate_title_description_dict(content):
    out = {"title": "", "description": ""}
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/yt_title_description.yaml')
    chat = chat.replace("<<CONTENT>>", f"{content}")
    
    for _ in range(5):
        try:
            result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=0.7)
            json_str = gpt_utils.extract_biggest_json(result) or result
            response = json.loads(json_str)
            if "title" in response and "description" in response:
                return response["title"], response["description"]
            if "title" in response:
                out["title"] = response["title"]
            if "description" in response:
                out["description"] = response["description"]
            if out["title"] and out["description"]:
                return out["title"], out["description"]
        except Exception:
            pass
        
    if not out["title"]:
        out["title"] = "Short Video"
    if not out["description"]:
        out["description"] = "#shorts #viral #video"
    return out['title'], out['description']
