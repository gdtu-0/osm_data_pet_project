# osm_data_pet_project

This is a project work for [OTUS](https://otus.ru/) 'Data Warehouse Analyst' course.

## Overview

Basic functionality:
- fetch data from OSM public API
- store changeset data into PostgreSQL database
- build data warehouse model with dbt
- add semantics layer with Cobe

## Usage

**Prerequisites**

To run this project you need to insall [Docker](https://www.docker.com/)

**Download**

Create new empty folder for the project `mkdir osm_data && cd osm_data`

Clone this repo `git clone https://github.com/gdtu-0/osm_data_pet_project.git && cd osm_data_pet_project`

**Startup and shutdown**

To start the project run `docker compose up -d`

To stop containers run `docker compose down`

## Next steps

This project is an MVP built in short time and lack of Python programming experience.
Backlog for further development:
- use [NamedTuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) for defining a LocationSpec
- use [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) istead of basic OSM API