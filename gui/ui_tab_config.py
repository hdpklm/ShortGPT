import time
import requests
import gradio as gr

from gui.asset_components import AssetComponentsUtils
from gui.ui_abstract_component import AbstractComponentUI
from shortGPT.api_utils.eleven_api import ElevenLabsAPI
from shortGPT.config.api_db import ApiKeyManager


class ConfigUI(AbstractComponentUI):
    def __init__(self):
        self.api_key_manager = ApiKeyManager()
        eleven_key = self.api_key_manager.get_api_key('ELEVENLABS_API_KEY')
        self.eleven_labs_api = ElevenLabsAPI(eleven_key) if eleven_key else None

    def on_show(self, button_text):
        '''Show or hide the API key'''
        if button_text == "Show":
            return gr.update(type="text"), gr.update(value="Hide")
        return gr.update(type="password"), gr.update(value="Show")

    def verify_eleven_key(self, eleven_key, remaining_chars):
        '''Verify the ElevenLabs API key'''
        if (eleven_key and self.api_key_manager.get_api_key('ELEVENLABS_API_KEY') != eleven_key):
            try:
                self.eleven_labs_api = ElevenLabsAPI(eleven_key)
                return self.eleven_labs_api.get_remaining_characters()
            except Exception as e:
                raise gr.Error(e.args[0])
        return remaining_chars

    def fetch_local_models(self, base_url):
        '''Fetch models from local LM-Studio / Ollama OpenAI endpoint'''
        if not base_url:
            raise gr.Error("Please enter a Base URL first (e.g. http://host.docker.internal:1234/v1)")
        url = base_url.rstrip("/") + "/models"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                if models:
                    return gr.update(choices=models, value=models[0])
                return gr.update(choices=["local-model"], value="local-model")
            raise gr.Error(f"HTTP {res.status_code} from endpoint: {res.text[:100]}")
        except Exception as e:
            raise gr.Error(f"Could not connect to {url}. Make sure LM-Studio/Ollama is running with local server enabled: {str(e)}")

    def on_preset_change(self, preset):
        if preset == "LM-Studio":
            return "http://host.docker.internal:1234/v1", "local-model"
        elif preset == "Ollama":
            return "http://host.docker.internal:11434/v1", "llama3.2"
        elif preset == "Cloud (OpenAI / Gemini)":
            return "", "gpt-4o-mini"
        return "http://host.docker.internal:1234/v1", "local-model"

    def save_keys(self, openai_key, eleven_key, pexels_key, gemini_key, llm_base_url, llm_model):
        '''Save the keys in the database'''
        if (self.api_key_manager.get_api_key("OPENAI_API_KEY") != openai_key):
            self.api_key_manager.set_api_key("OPENAI_API_KEY", openai_key)
        if (self.api_key_manager.get_api_key("PEXELS_API_KEY") != pexels_key):
            self.api_key_manager.set_api_key("PEXELS_API_KEY", pexels_key)
        if (self.api_key_manager.get_api_key("GEMINI_API_KEY") != gemini_key):
            self.api_key_manager.set_api_key("GEMINI_API_KEY", gemini_key)
        if (self.api_key_manager.get_api_key("LLM_BASE_URL") != llm_base_url):
            self.api_key_manager.set_api_key("LLM_BASE_URL", llm_base_url)
        if (self.api_key_manager.get_api_key("LLM_MODEL") != llm_model):
            self.api_key_manager.set_api_key("LLM_MODEL", llm_model)
        if (self.api_key_manager.get_api_key('ELEVENLABS_API_KEY') != eleven_key):
            self.api_key_manager.set_api_key("ELEVENLABS_API_KEY", eleven_key)
            new_eleven_voices = AssetComponentsUtils.getElevenlabsVoices()
            return gr.update(value=openai_key),\
                gr.update(value=eleven_key),\
                gr.update(value=pexels_key),\
                gr.update(value=gemini_key),\
                gr.update(value=llm_base_url),\
                gr.update(value=llm_model),\
                gr.update(choices=new_eleven_voices),\
                gr.update(choices=new_eleven_voices)

        return gr.update(value=openai_key),\
            gr.update(value=eleven_key),\
            gr.update(value=pexels_key),\
            gr.update(value=gemini_key),\
            gr.update(value=llm_base_url),\
            gr.update(value=llm_model),\
            gr.update(visible=True),\
            gr.update(visible=True)

    def get_eleven_remaining(self):
        '''Get the remaining characters from ElevenLabs API'''
        if (self.eleven_labs_api):
            try:
                return self.eleven_labs_api.get_remaining_characters()
            except Exception as e:
                return e.args[0]
        return ""

    def back_to_normal(self):
        '''Back to normal after 3 seconds'''
        time.sleep(3)
        return gr.update(value="save")

    def create_ui(self):
        '''Create the config UI'''
        with gr.Tab("Config") as config_ui:
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🏠 Local LLM Configuration (LM-Studio / Ollama / LocalAI)")
                    preset_radio = gr.Radio(["LM-Studio", "Ollama", "Cloud (OpenAI / Gemini)", "Custom"], value="LM-Studio" if "1234" in self.api_key_manager.get_api_key("LLM_BASE_URL") else ("Ollama" if "11434" in self.api_key_manager.get_api_key("LLM_BASE_URL") else "LM-Studio"), label="Select LLM Provider Preset")
                    with gr.Row():
                        llm_base_url_textbox = gr.Textbox(value=self.api_key_manager.get_api_key("LLM_BASE_URL") or "http://host.docker.internal:1234/v1", label="LOCAL LLM BASE URL", show_label=True, interactive=True, scale=35)
                        fetch_models_btn = gr.Button("🔄 Fetch Models", size="sm", scale=5)
                    with gr.Row():
                        current_model = self.api_key_manager.get_api_key("LLM_MODEL") or "local-model"
                        llm_model_dropdown = gr.Dropdown(choices=[current_model], value=current_model, label="LOCAL LLM MODEL NAME", allow_custom_value=True, interactive=True)
                    
                    fetch_models_btn.click(self.fetch_local_models, [llm_base_url_textbox], [llm_model_dropdown])
                    preset_radio.change(self.on_preset_change, [preset_radio], [llm_base_url_textbox, llm_model_dropdown])

                    gr.Markdown("### 🔑 Cloud API Keys (Optional if using Local LLM)")
                    with gr.Row():
                        openai_textbox = gr.Textbox(value=self.api_key_manager.get_api_key("OPENAI_API_KEY"), label="OPENAI API KEY", show_label=True, interactive=True, show_copy_button=True, type="password", scale=40)
                        show_openai_key = gr.Button("Show", size="sm", scale=1)
                        show_openai_key.click(self.on_show, [show_openai_key], [openai_textbox, show_openai_key])
                    with gr.Row():
                        gemini_textbox = gr.Textbox(value=self.api_key_manager.get_api_key("GEMINI_API_KEY"), label="GEMINI API KEY", show_label=True, interactive=True, show_copy_button=True, type="password", scale=40)
                        show_gemini_key = gr.Button("Show", size="sm", scale=1)
                        show_gemini_key.click(self.on_show, [show_gemini_key], [gemini_textbox, show_gemini_key])
                    with gr.Row():
                        pexels_textbox = gr.Textbox(value=self.api_key_manager.get_api_key("PEXELS_API_KEY"), label="PEXELS KEY (for stock footage/images)", show_label=True, interactive=True, show_copy_button=True, type="password", scale=40)
                        show_pexels_key = gr.Button("Show", size="sm", scale=1)
                        show_pexels_key.click(self.on_show, [show_pexels_key], [pexels_textbox, show_pexels_key])
                    with gr.Row():
                        eleven_labs_textbox = gr.Textbox(value=self.api_key_manager.get_api_key("ELEVENLABS_API_KEY"), label="ELEVENLABS_API_KEY (optional, EdgeTTS is free)", show_label=True, interactive=True, show_copy_button=True, type="password", scale=40)
                        eleven_characters_remaining = gr.Textbox(value=self.get_eleven_remaining(), label="CHARACTERS REMAINING", show_label=True, interactive=False, type="text", scale=40)
                        show_eleven_key = gr.Button("Show", size="sm", scale=1)
                        show_eleven_key.click(self.on_show, [show_eleven_key], [eleven_labs_textbox, show_eleven_key])

                    save_button = gr.Button("save", size="sm", scale=1)
                    save_button.click(self.verify_eleven_key, [eleven_labs_textbox, eleven_characters_remaining], [eleven_characters_remaining]).success(
                        self.save_keys, [openai_textbox, eleven_labs_textbox, pexels_textbox, gemini_textbox, llm_base_url_textbox, llm_model_dropdown], [openai_textbox, eleven_labs_textbox, pexels_textbox, gemini_textbox, llm_base_url_textbox, llm_model_dropdown, AssetComponentsUtils.voiceChoice(), AssetComponentsUtils.voiceChoiceTranslation()])
                    save_button.click(lambda: gr.update(value="Keys Saved !"), [], [save_button])
                    save_button.click(self.back_to_normal, [], [save_button])
        return config_ui