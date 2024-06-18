FROM python:3.12.3-slim
WORKDIR /app
COPY hatchet-worker-requirements.txt .
RUN pip install --no-cache-dir -r hatchet-worker-requirements.txt
COPY . .
CMD ["python", "-m", "src.main"]