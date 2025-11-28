FROM python:3.12-slim

WORKDIR /app
COPY constraints.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY README.md LICENSE ./

ENV PYTHONPATH=/app/src
EXPOSE 8089

CMD ["uvicorn", "payments.server:app", "--host", "0.0.0.0", "--port", "8089"]
