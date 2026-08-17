FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY src/ ./src/

# config.yaml and profiles/ (which includes profiles/output/) are meant to
# be bind-mounted at runtime, not baked into the image.
#
# Two entrypoints share this image (picked in docker-compose.yml):
#   - `python main.py`                                    -> one-off scan
#   - `uvicorn job_search.api:app --host 0.0.0.0 --port 8000` -> API server
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "job_search.api:app", "--host", "0.0.0.0", "--port", "8000"]
