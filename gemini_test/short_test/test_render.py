import sys
sys.path.insert(0, '/app')
import traceback
from shortGPT.engine.reddit_short_engine import RedditShortEngine
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
from shortGPT.config.languages import Language

try:
	print("Starting complete Short pipeline test...")
	engine = RedditShortEngine(
		voiceModule=EdgeTTSVoiceModule('es-ES-AlvaroNeural'),
		short_id='',
		background_video_name='Video-1',
		background_music_name='Music-1',
		num_images=0,
		watermark=None,
		language=Language.SPANISH
	)
	print(f"Initialized Short ID: {engine.id}")
	for step_num, step_info in engine.makeContent():
		print(f"Step {step_num} finished: {step_info}")
	print("SUCCESS: Full video generated and ready at:", engine._db_video_path)
except Exception as e:
	print("ERROR OCCURRED IN PIPELINE:")
	traceback.print_exc()
