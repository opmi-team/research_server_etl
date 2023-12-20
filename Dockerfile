FROM python:3.11-slim

# Prevents buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install non python dependencies
RUN apt-get update
RUN apt-get install -y libpq-dev gcc curl gzip zip postgresql-client

# Fetch Amazon RDS certificate chain
RUN curl https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /usr/local/share/amazon-certs.pem
RUN chmod a=r /usr/local/share/amazon-certs.pem

# Install poetry
RUN pip install -U pip
RUN pip install "poetry==1.7.1"

# copy poetry and pyproject files and install dependencies
WORKDIR /research_server_etl/
COPY pyproject.toml pyproject.toml
RUN poetry install --only main --no-interaction --no-ansi --no-root -v

# Copy src directory to run against and build app
COPY src src
RUN poetry install --only main --no-interaction --no-ansi -v