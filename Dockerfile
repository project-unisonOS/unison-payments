FROM ghcr.io/project-unisonos/unison-common-wheel:latest AS common_wheel
FROM python:3.12-slim@sha256:fdab368dc2e04fab3180d04508b41732756cc442586f708021560ee1341f3d29

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
