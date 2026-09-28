import os
import platform
import random
import subprocess

import gradio as gr

from shortGPT.api_utils.eleven_api import ElevenLabsAPI
from shortGPT.config.api_db import ApiKeyManager
from shortGPT.config.asset_db import AssetDatabase


class AssetComponentsUtils:
    EDGE_TTS = "Free EdgeTTS (lower quality)"
    ELEVEN_TTS = "ElevenLabs(Very High Quality)"


    instance_background_video_checkbox = None
    instance_background_music_checkbox = None
    instance_voiceChoice: dict[gr.Radio] = {}
    instance_voiceChoiceTranslation: dict[gr.Radio] = {}

    @classmethod
    def getBackgroundVideoChoices(cls):
        df = AssetDatabase.get_df()
        if df.empty or "type" not in df.columns or "name" not in df.columns:
            return []
        choices = list(df.loc[df["type"].astype(str).str.lower().isin(["background video", "video", "visual"])]["name"])[:20]
        return choices

    @classmethod
    def getBackgroundMusicChoices(cls):
        df = AssetDatabase.get_df()
        if df.empty or "type" not in df.columns or "name" not in df.columns:
            return []
        choices = list(df.loc[df["type"].astype(str).str.lower().isin(["background music", "music", "audio", "sound"])]["name"])[:20]
        return choices

    @classmethod
    def getElevenlabsVoices(cls):
        api_key = ApiKeyManager.get_api_key("ELEVENLABS_API_KEY")
        if not api_key:
            return []
        try:
            return list(reversed(ElevenLabsAPI(api_key).get_voices().keys()))
        except Exception:
            return []

    @classmethod
    def start_file(cls, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                if shutil.which("xdg-open"):
                    subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    @classmethod
    def background_video_checkbox(cls):
        if cls.instance_background_video_checkbox is None:
            choices = cls.getBackgroundVideoChoices()
            cls.instance_background_video_checkbox = gr.CheckboxGroup(
                choices=choices,
                interactive=True,
                label="Choose background video",
                value=[choices[0]] if choices else []
            )
        return cls.instance_background_video_checkbox

    @classmethod
    def background_music_checkbox(cls):
        if cls.instance_background_music_checkbox is None:
            choices = cls.getBackgroundMusicChoices()
            cls.instance_background_music_checkbox = gr.CheckboxGroup(
                choices=choices,
                interactive=True,
                label="Choose background music",
                value=[choices[0]] if choices else []
            )
        return cls.instance_background_music_checkbox

    @classmethod
    def voiceChoice(cls, provider: str = None):
        if provider == None:
            provider = cls.ELEVEN_TTS
        if cls.instance_voiceChoice.get(provider, None) is None:
            if provider == cls.ELEVEN_TTS:
                voices = cls.getElevenlabsVoices()
                value = "Chris" if "Chris" in voices else (voices[0] if voices else None)
                cls.instance_voiceChoice[provider] = gr.Radio(
                    choices=voices,
                    label="Elevenlabs voice",
                    value=value,
                    interactive=True,
                )
        return cls.instance_voiceChoice[provider]

    @classmethod
    def voiceChoiceTranslation(cls, provider: str = None):
        if provider == None:
            provider = cls.ELEVEN_TTS
        if cls.instance_voiceChoiceTranslation.get(provider, None) is None:
            if provider == cls.ELEVEN_TTS:
                voices = cls.getElevenlabsVoices()
                value = "Chris" if "Chris" in voices else (voices[0] if voices else None)
                cls.instance_voiceChoiceTranslation[provider] = gr.Radio(
                    choices=voices,
                    label="Elevenlabs voice",
                    value=value,
                    interactive=True,
                )
        return cls.instance_voiceChoiceTranslation[provider]
