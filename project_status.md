### 📝 Descripción
ShortGPT es un framework automatizado de creación y edición de videos cortos (Shorts, TikToks, Reels) impulsado por inteligencia artificial. Permite generar guiones, sintetizar locuciones (TTS), transcribir y alinear subtítulos dinámicos con Whisper, obtener recursos visuales contextuales y componer/renderizar videos verticales con MoviePy y FFmpeg, con soporte para modelos locales (LM Studio/Ollama), Gemini y OpenAI.

### 🏗️ Arquitectura
- `runShortGPT.py` : Punto de entrada para iniciar la aplicación web en Gradio con configuración de host/puerto.
- `gui/` : Interfaz de usuario Gradio 4.x modularizada con pestañas para automatización de shorts, biblioteca de activos, traducción y configuración de APIs/LLMs.
- `shortGPT/engine/` : Motores orquestadores de contenido (`ContentShortEngine`, `FactsShortEngine`, `RedditShortEngine`, `ContentVideoEngine`, `ContentTranslationEngine`, `MultiLanguageTranslationEngine`).
- `shortGPT/gpt/` : Módulos de interacción con LLMs (OpenAI, Gemini, LM Studio, endpoints compatibles), parseo balanceado de JSON y extracción de metadatos.
- `shortGPT/audio/` : Módulos de síntesis de voz (`EdgeTTSVoiceModule`, `ElevenLabsVoiceModule`) y utilidades de audio (duración, aceleración de tempo, Whisper).
- `shortGPT/editing_framework/` : Motor de edición basado en pasos (`EditingEngine`, `CoreEditingEngine`, `EditingStep`) compatible con MoviePy 2.x.
- `shortGPT/editing_utils/` : Utilidades de sincronización de subtítulos (`whisper-timestamped`), descarga/procesamiento de imágenes (`Pillow`) y extracción segura de clips de fondo con FFmpeg.
- `shortGPT/config/` : Gestión de base de datos de activos locales y remotos (`AssetDatabase`), llaves de API (`ApiKeyManager`) y configuración de idiomas.
- `docker-compose.yml` / `Dockerfile` : Entorno de despliegue contenedorizado con soporte para montaje de volúmenes de assets y salida de videos.

### 🛠️ Tecnologías
- Python 3.10+
- OpenAI API / Gemini API (Google AI) / Local LLMs (LM Studio, Ollama, vLLM vía OpenAI-compatible API)
- Whisper-timestamped (Torch / Torchaudio)
- Edge-TTS (Microsoft TTS gratuito)
- ElevenLabs API
- MoviePy 2.1.2+ & FFmpeg
- Pillow (PIL) 10.4+
- yt-dlp
- Gradio 4.44+
- TinyDB / TinyMongo
- Docker & Docker Compose

### 🛠️ Módulos y Funciones
- `shortGPT/gpt/gpt_utils.py`
	- (v0.1.33) `extract_biggest_json(string: str) -> str` : Extrae el objeto JSON más externo utilizando conteo balanceado de llaves `{}`.
	- (v0.1.33) `llm_completion(chat_prompt: str, system: str, temp: float, max_tokens: int, remove_nl: bool, conversation: list) -> str` : Ejecuta llamadas al LLM con soporte para `LLM_BASE_URL`, `LLM_MODEL`, Gemini API, OpenAI y fallback a LM Studio local.
	- (v0.1.33) `load_local_yaml_prompt(yaml_path: str) -> tuple[str, str]` : Carga un template YAML y retorna (chat_prompt, system_prompt).
- `shortGPT/gpt/gpt_yt.py`
	- (v0.1.33) `generate_title_description_dict(content: str) -> tuple[str, str]` : Genera título y descripción de YouTube con reintentos y valores por defecto de seguridad.
- `shortGPT/gpt/reddit_gpt.py`
	- (v0.1.33) `getRealisticness(text: str) -> float` : Evalúa la plausibilidad de una historia de Reddit con fallback numérico seguro (8.0).
	- (v0.1.33) `create_reddit_story(question: str) -> str` : Genera una historia en primera persona a partir de una pregunta.
	- (v0.1.33) `getQuestionFromThread(text: str) -> str` : Extrae o valida el formato de pregunta de Reddit.
- `shortGPT/config/asset_db.py`
	- (v0.1.33) `get_asset_link(key: str) -> str` : Obtiene la ruta o URL de un activo local o remoto con resolución automática de rutas de fallback.
	- (v0.1.33) `get_asset_duration(key: str) -> float` : Obtiene la duración del activo con soporte para videos locales y animaciones de suscripción.
	- (v0.1.33) `get_df(source: str) -> pd.DataFrame` : Genera un DataFrame de activos locales y remotos con validación de tipos.
	- (v0.1.33) `sync_local_assets() -> None` : Sincroniza archivos de la carpeta `public/` en la base de datos de TinyMongo.
- `shortGPT/config/api_db.py`
	- (v0.1.33) `get_api_key(key: str) -> str` : Obtiene claves de API desde TinyDB o variables de entorno, filtrando placeholders vacíos (`put_your_...`).
- `shortGPT/editing_utils/handle_videos.py`
	- (v0.1.33) `extract_random_clip_from_video(video_url: str, video_duration: float, clip_duration: float, output_file: str) -> str` : Extrae un subclip aleatorio con FFmpeg; si el video es más corto que la duración requerida, aplica `-stream_loop -1` automáticamente.
- `shortGPT/editing_framework/core_editing_engine.py`
	- (v0.1.33) `generate_image_clip(image_path: str, duration: float, position: tuple) -> ImageClip` : Genera clips de imagen optimizados para MoviePy 2.x.
	- (v0.1.33) `crop_to_vertical(clip: VideoClip) -> VideoClip` : Ajusta relaciones de aspecto horizontales a formato vertical 9:16.
- `shortGPT/audio/audio_utils.py`
	- (v0.1.33) `audioToText(audio_path: str) -> dict` : Transcribe audio y genera marcas de tiempo por palabra usando `whisper-timestamped`.
	- (v0.1.33) `speedUpAudio(audio_path: str, output_path: str, speed_factor: float) -> str` : Acelera pistas de voz mediante filtros de audio.
- `shortGPT/engine/content_short_engine.py`
	- (v0.1.33) `_generateScript() -> None` : Genera el guión base del video.
	- (v0.1.33) `_generateTempAudio() -> None` : Sintetiza la locución de voz con el módulo TTS configurado.
	- (v0.1.33) `_speedUpAudio() -> None` : Acelera el audio para mantener el ritmo de video corto.
	- (v0.1.33) `_timeCaptions() -> None` : Calcula timestamps de subtítulos mediante Whisper.
	- (v0.1.33) `_generateImageSearchTerms() -> None` : Obtiene términos de búsqueda de imágenes asociados al tiempo.
	- (v0.1.33) `_prepareBackgroundAssets() -> None` : Prepara y recorta el video de fondo con soporte de bucle.
	- (v0.1.33) `_editAndRenderShort() -> None` : Compone pistas visuales, subtítulos, audio y renderiza el MP4 final.
	- (v0.1.33) `_addYoutubeMetadata() -> None` : Genera título y descripción SEO y almacena en `videos/`.
- `gui/gui_gradio.py`
	- (v0.1.33) `ShortGptUI.launch(server_name: str, server_port: int) -> None` : Inicia el servidor Gradio con colas (`queue`), control de concurrencia y tema personalizado.
- `gui/ui_tab_config.py`
	- (v0.1.33) `save_api_key(key_name: str, key_value: str) -> None` : Guarda llaves de API y configuración de endpoint local (`LLM_BASE_URL`, `LLM_MODEL`).

### 🛠️ Endpoints
```js
api = {
	"UI_Gradio": {
		Version: "v0.1.33",
		Interface: "Web GUI",
		Tabs: [
			"Automated Short Engine (Facts, Reddit, Custom)",
			"Video Automation (Full B-roll Video)",
			"Video Translation & Dubbing Engine",
			"Asset Library (Local & YouTube)",
			"Config & API Keys (OpenAI, Gemini, Local LLMs, ElevenLabs, Pexels)"
		]
	}
}
```

## Backup
### 🛠️ Módulos y Funciones
- `shortGPT/gpt/gpt_utils.py`
	- (v0.1.32) `extract_biggest_json(string: str) -> str` : Extracción básica por regex susceptible a fallos con JSONs anidados.
	- (v0.1.32) `llm_completion(chat_prompt: str, system: str, model: str, temp: float, max_tokens: int) -> str` : Soporte limitado exclusivamente a OpenAI API oficial.
- `shortGPT/editing_utils/handle_videos.py`
	- (v0.1.32) `extract_random_clip_from_video(video_url: str, video_duration: float, clip_duration: float, output_file: str) -> str` : Fallaba cuando la duración del video de fondo era inferior a la duración del audio.
