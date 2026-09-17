FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/ data/
COPY models/ models/
COPY assets/ assets/
COPY docs/ docs/

ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "src/northstar/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
