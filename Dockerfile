cat << 'EOF' > Dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn pydantic requests openai openenv-core
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
EOF
