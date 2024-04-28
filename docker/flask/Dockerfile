FROM python:3.11-slim-buster AS base

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
  && chown python:python -R /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED="true" \
    PYTHONIOENCODING="utf-8" \
    PYTHONDONTWRITEBYTECODE="true" \
    PATH="${PATH}:/home/python/.local/bin"

# COPY --chown=python:python /root/.local /home/python/.local

ARG APP_HOST="0.0.0.0"
ARG APP_PORT="8000"
ARG DEBUG="True"

ENV APP_HOST=${APP_HOST}
ENV APP_PORT=${APP_PORT}
ENV DEBUG=${DEBUG}

EXPOSE $APP_PORT

CMD python application.py --host $APP_HOST --port $APP_PORT --debug $DEBUG

USER python
