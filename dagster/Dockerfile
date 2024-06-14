# Dagster libraries to run both dagster-webserver and the dagster-daemon.

FROM python:3.10-slim

# Install base dagster modules
RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker \
    dagster-dbt

# Create dagster home dir and copy dagster.yaml config file
ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME
COPY dagster/dagster.yaml $DAGSTER_HOME

# Create dagster app dir and copy workspace.yaml config file
ENV DAGSTER_APP=/opt/dagster/app
RUN mkdir -p $DAGSTER_APP
COPY dagster/workspace.yaml $DAGSTER_APP
WORKDIR $DAGSTER_APP

# Install additional packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -qy gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

# Install requirements
COPY dagster/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Expose dagster webserver port
EXPOSE 3000

# Start everything
ENTRYPOINT ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]