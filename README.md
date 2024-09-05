# OPMI Research Server ETL
Loading data into OPMI AWS Research Server

# Developer Usage

[asdf](https://asdf-vm.com/) is used to mange runtime versions using the command line. Once installed, run the following in the root project directory:

```sh
# add project plugins
asdf plugin-add python
asdf plugin-add direnv
asdf plugin-add poetry

# install versions of plugins specified in .tool-versions
asdf install
```

`poetry` is used to manage dependencies. 

`docker` and  `docker-compose` are required to run containerized versions of application for local development. Follow instructions from docker to the Docker engine and docker-compose for your local environment.

## Environmental Variables

Project environmental variables are stored in `.env` and managed for command line usage with `direnv`.

This project includes a [.env.template](.env.template) that can be copied to a `.env` file to get started.

Using `direnv`, whenever a shell moves into any project directory, the environmental variables defined in `.env` are loaded automagically. 

Additionally, [docker-compose.yml](docker-compose.yml) is configured to use `.env`, so that running containerized applications will load the same environmental variables.

## AWS Credentials

Some ETL jobs require permissions to access MBTA/TID AWS resources. 

Running these jobs without expected permissions will result in AWS (boto3) errors

## Continuous Integration

To ensure code quality, linting, type checking, static analysis and unit tests are automatically run via github actions when pull requests are opened. 

CI can be run locally, in the root project directory, with the following `poetry` commands:
```sh
# black for Formatting
poetry run black .

# mypy for Type Checking
poetry run mypy .

# pylint for Static Analysis
poetry run pylint src tests

# pytest for Unit Tests
poetry run pytest
```

## Using Docker

The included [Dockerfile](Dockerfile) is used for local testing and AWS deployment. 

The [docker-compose.yml](docker-compose.yml) file, found in the project root directory, describes a local environment for testing the application. This environment includes a local PostgreSQL database and `research_etl` application that can be used to test some parts of the application locally. 

To build application images run the following in the project root directory:
```sh
docker-compose build
```

The local PostgreSQL database is configured to automatically load an [SQL](tests/files/init_schema.sql) file that will create schemas and tables that the `research_etl` application expects to exist in the database.


To start a local version of the application run the following in the project root directory:
```sh
docker-compose up research_etl
```
The `research_etl` application will begin running ETL jobs defined in [pipeline.py](src/research_etl/pipeline.py).