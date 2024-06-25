# osm_data_pet_project

This is a project work for [OTUS](https://otus.ru/) 'Data Warehouse Analyst' course.

## Overview

This project builds data pipeline over data from [Open Street Map](https://www.openstreetmap.org/), 
a free, open geographic database updated and maintained by a community of volunteers([wiki](https://en.wikipedia.org/wiki/OpenStreetMap)).

Basic data element for analysis in this model is 'changeset'. A changeset is transactional data record that stores all map elements 
created or modified during user's edit session and additional metadata entities.

Changeset data is fetched from [OSM API](https://wiki.openstreetmap.org/wiki/API_v0.6), transformed and stored in [PostgreSQL](https://www.postgresql.org/) database. 
Simple data warehousee model is built nn top of that raw changeset data using [dbt](https://www.getdbt.com/) and [cube](https://cube.dev/). 
ETL procces and orchestration is implemented in [Dagster](https://dagster.io/).

Basic functionality:
- fetch data from OSM public API
- store changeset data into PostgreSQL database
- build data warehouse model with dbt
- add semantics layer with cube

## Usage

**Prerequisites**

To run this project you need to insall [Docker](https://www.docker.com/)

**Download**

Create new empty folder for the project `mkdir osm_data && cd osm_data`

Clone this repo `git clone https://github.com/gdtu-0/osm_data_pet_project.git && cd osm_data_pet_project`

**Startup and shutdown**

To start the project run `docker compose up -d`

This command runs containers in background. Containers keep running even if you restart the system.

To stop containers run `docker compose down`

## Next steps

This project is an MVP built in short time and lack of Python programming experience.
Backlog for further development:
- use [NamedTuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) for defining a LocationSpec
- use [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) istead of basic OSM API