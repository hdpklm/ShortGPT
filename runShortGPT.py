import os
from gui.gui_gradio import ShortGptUI

os.makedirs("public", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs(".database", exist_ok=True)

app = ShortGptUI(colab=False)
app.launch()