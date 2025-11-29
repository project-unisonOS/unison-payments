FROM ghcr.io/project-unisonos/unison-common-wheel:latest AS common_wheel
FROM python:3.12-slim

WORKDIR /app
COPY constraints.txt requirements.txt ./
COPY --from=common_wheel /tmp/wheels /tmp/wheels
RUN pip install --no-cache-dir -c constraints.txt /tmp/wheels/unison_common-*.whl \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY README.md LICENSE ./

ENV PYTHONPATH=/app/src
EXPOSE 8089

CMD ["uvicorn", "payments.server:app", "--host", "0.0.0.0", "--port", "8089"]
