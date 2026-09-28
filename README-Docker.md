# To run ShortGPT docker:


First make a .env file with the API keys like this:

```bash
GEMINI_API_KEY=put_your_gemini_api_key_here
OPENAI_API_KEY=sk-_put_your_openai_api_key_here
ELEVENLABS_API_KEY=put_your_eleven_labs_api_key_here
PEXELS_API_KEY=put_your_pexels_api_key_here
```


To run Dockerfile in background (detached mode) with persistent storage:
```bash
docker build -t short_gpt_docker:latest .
docker run -d --name short_gpt -p 31415:31415 --restart unless-stopped --env-file .env -v "C:/docker/storage/ShortGPT/public:/app/public" -v "C:/docker/storage/ShortGPT/videos:/app/videos" -v "C:/docker/storage/ShortGPT/database:/app/.database" short_gpt_docker:latest
```

Or using Docker Compose:
```bash
docker compose up -d
```

Export Docker image:
```bash
docker save short_gpt_docker > short_gpt_docker.tar
```
