import huggingface_hub
if not hasattr(huggingface_hub, "HfFolder"):
    class HfFolder:
        @classmethod
        def get_token(cls):
            return None
        @classmethod
        def save_token(cls, token):
            pass
        @classmethod
        def delete_token(cls):
            pass
    huggingface_hub.HfFolder = HfFolder

try:
    import gradio_client.utils as client_utils
    if hasattr(client_utils, "_json_schema_to_python_type"):
        _orig_json_schema = client_utils._json_schema_to_python_type

        def _safe_json_schema(schema, defs=None):
            if isinstance(schema, bool) or not isinstance(schema, dict):
                return "Any"
            return _orig_json_schema(schema, defs)

        client_utils._json_schema_to_python_type = _safe_json_schema

    if hasattr(client_utils, "get_type"):
        _orig_get_type = client_utils.get_type

        def _safe_get_type(schema):
            if isinstance(schema, bool) or not isinstance(schema, dict):
                return "Any"
            return _orig_get_type(schema)

        client_utils.get_type = _safe_get_type
except Exception:
    pass

try:
    import starlette.templating
    _orig_TemplateResponse = starlette.templating.Jinja2Templates.TemplateResponse

    def _patched_TemplateResponse(self, *args, **kwargs):
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            name = args[0]
            context = args[1]
            request = context.get("request")
            return _orig_TemplateResponse(self, request=request, name=name, context=context, **kwargs)
        elif len(args) == 1 and isinstance(args[0], str) and "context" in kwargs:
            name = args[0]
            context = kwargs.pop("context")
            request = context.get("request") if isinstance(context, dict) else kwargs.get("request")
            return _orig_TemplateResponse(self, request=request, name=name, context=context, **kwargs)
        return _orig_TemplateResponse(self, *args, **kwargs)

    starlette.templating.Jinja2Templates.TemplateResponse = _patched_TemplateResponse
except Exception:
    pass

try:
    import jinja2
    _orig_load_template = jinja2.Environment._load_template

    def _patched_load_template(self, name, globals=None):
        if self.loader is None:
            raise TypeError("no loader for this environment specified")
        cache_key = str(name)
        if self.cache is not None:
            try:
                template = self.cache.get(cache_key)
                if template is not None and (
                    not self.auto_reload or template.is_up_to_date
                ):
                    return template
            except Exception:
                pass
        template = self.loader.load(self, name, self.make_globals(globals))
        if self.cache is not None:
            try:
                self.cache[cache_key] = template
            except Exception:
                pass
        return template

    jinja2.Environment._load_template = _patched_load_template
except Exception:
    pass

import gradio as gr

from gui.content_automation_ui import GradioContentAutomationUI
from gui.ui_abstract_base import AbstractBaseUI
from gui.ui_components_html import GradioComponentsHTML
from gui.ui_tab_asset_library import AssetLibrary
from gui.ui_tab_config import ConfigUI
from shortGPT.utils.cli import CLI


class ShortGptUI(AbstractBaseUI):
    '''Class for the GUI. This class is responsible for creating the UI and launching the server.'''

    def __init__(self, colab=False):
        super().__init__(ui_name='gradio_shortgpt')
        self.colab = colab
        CLI.display_header()

    def create_interface(self):
        '''Create Gradio interface'''
        with gr.Blocks(theme=gr.themes.Default(spacing_size=gr.themes.sizes.spacing_sm), css="footer {visibility: hidden}", title="ShortGPT Demo") as shortGptUI:
            with gr.Row(variant='compact'):
                gr.HTML(GradioComponentsHTML.get_html_header())

            self.content_automation = GradioContentAutomationUI(shortGptUI).create_ui()
            self.asset_library_ui = AssetLibrary().create_ui()
            self.config_ui = ConfigUI().create_ui()
        return shortGptUI

    def launch(self):
        '''Launch the server'''
        shortGptUI = self.create_interface()
        if not getattr(self, 'colab', False):
                    print("\n\n********************* STARTING SHORGPT **********************")
                    print("\nShortGPT is running here 👉 http://localhost:31415\n")
                    print("********************* STARTING SHORGPT **********************\n\n")
        shortGptUI.queue().launch(server_port=31415, height=1000, allowed_paths=["public/","videos/","fonts/"], share=self.colab, server_name="0.0.0.0")



if __name__ == "__main__":
    app = ShortGptUI()
    app.launch()


import signal

def signal_handler(sig, frame):
    print("Closing Gradio server...")
    import gradio as gr
    gr.close_all()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)