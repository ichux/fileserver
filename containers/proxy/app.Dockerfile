FROM python:3.12.9-slim-bookworm AS builder

WORKDIR /home
COPY requirements.txt .

RUN python3 -m venv .env && . .env/bin/activate && \
	pip install -U pip setuptools wheel && pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt && pip install --no-cache-dir ipython && \
	find . -name '__pycache__' -type d -print0 | xargs -0 /bin/rm -rf '{}' && \
	find . -iname '*.pyc' -delete

FROM python:3.12.9-slim-bookworm

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ARG PC_USER

COPY --from=builder /home/ /home/
ENV PATH="/home/.env/bin:$PATH"

# Create a new user and set the UID/GID to match the host user
RUN adduser --uid 1000 --disabled-password --gecos "" $PC_USER

USER $PC_USER
WORKDIR /apps
