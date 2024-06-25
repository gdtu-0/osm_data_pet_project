# osm_data_pet_project
This is a pet project for OTUS Data Warehouse Analyst course.
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
Create new empty folder for the project
····mkdir osm_data && cd osm_data
Clone this repo
....git clone https://github.com/gdtu-0/osm_data_pet_project.git && cd osm_data_pet_project
**Run**
....docker compose up -d
## Next steps
- use NamedTuple for defining a LocationSpec
- use Overpass API istead of basic OSM API