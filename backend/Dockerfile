# Backend image for AWS App Runner.
#
# Builds a self-contained container that runs the FastAPI app with uvicorn.
# The entrypoint script applies any pending Alembic migrations before the
# server starts, so a fresh deploy always ends up with an up-to-date schema.

FROM python:3.12-slim

WORKDIR /app

# Install OS packages needed to build psycopg2 and bcrypt from source, then
# remove the build tools afterward to keep the final image small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

# App Runner is configured to send traffic to this port (set as the
# service's "port" value when creating it in the console).
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
