# Dagster libraries to run both dagster-webserver and the dagster-daemon. Does not
# need to have access to any pipeline code.

FROM python:3.10-slim

RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker \
    pandas

ENV DAGSTER_APP=/opt/dagster/app
COPY dagster/workspace.yaml $DAGSTER_APP

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
COPY dagster/dagster.yaml $DAGSTER_HOME

WORKDIR $DAGSTER_APP

EXPOSE 3000

ENTRYPOINT ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]