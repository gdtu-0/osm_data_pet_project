# osm_data_pet_project

This is a project work for [OTUS](https://otus.ru/) 'Data Warehouse Analyst' course.

## Overview

This project builds data pipeline over data from [Open Street Map](https://www.openstreetmap.org/) ([wiki](https://en.wikipedia.org/wiki/OpenStreetMap)), 
a free, open geographic database updated and maintained by a community of volunteers.

Basic data element for analysis in this model is 'changeset'. A changeset is transactional data record that stores all map elements 
created or modified during user's edit session and some additional metadata entities.

Changeset data is fetched from [OSM API](https://wiki.openstreetmap.org/wiki/API_v0.6), transformed and stored in [PostgreSQL](https://www.postgresql.org/) database. 
Simple data warehouse model is built on top of that raw data using [dbt](https://www.getdbt.com/) and [cube](https://cube.dev/). 
ETL procces and orchestration is implemented in [Dagster](https://dagster.io/).

Basic functionality:
- fetch changeset records from OSM public API
- store data into PostgreSQL database
- build data warehouse model with dbt
- add semantics layer with cube

## Installation

**Prerequisites**

To run this project you need to have [docker](https://www.docker.com/) insalled.

**Download**

Clone this repo: `git clone https://github.com/gdtu-0/osm_data_pet_project.git && cd osm_data_pet_project`.

**Startup and shutdown**

To start the project run: `docker compose up -d`. 
This command runs containers in background. Containers keep running even if you restart the system.

To stop containers run: `docker compose down`. PostgreSQL is configured to store database outside the container so 
you will not loose dowloaded data on shutdown. Dagster run history and statistics will be lost on shutdown but it 
does not affect project functionality.

## Usage

**Location specification**

To get changeset information for specific location of the map you have to define a bounding box for your request to OSM API.

A bounding box consists of four parameters:
- **min_lon** - longitude of the left (westernmost) side of the bounding box
- **min_lat** - latitude of the bottom (southernmost) side of the bounding box
- **max_lon** - longitude of the right (easternmost) side of the bounding box
- **max_lat** - latitude of the top (northernmost) side of the bounding box

This project has a set of pre-defined initial locations at `dagster/model/initial_locations.py` to load data for. 
After startup dagster will automaically insert them into setup table and start initial data load.

**Time slice**

OSM API returns a most 100 changesets per request. In order to not overload API server, data is fetched in 15 
minutes slices (this can be changed by setting `OSM_DATA_UPDATE_INTERVAL_MINUTES` constant in `dagster/model/seettings.py`). 
So basically we get 100 changesets per time slice. IMPORTANT: If no changes have been made during the slice API will 
return the same 100 changesets as in previous request.

**Load modes**

Data pipeline supports three types of loading process:
- **initial load** - if there are no statistics records for specified location dagster will automatically trigger 
initial load. By default it loads data for 7 days before current date (this can be changed by setting `INITIAL_LOAD_NUM_DAYS` 
constant in `dagster/model/seettings.py`). Initial load is considered finished when next timestamp to load data from is 
greater than or equal to current timestamp.
- **interval load** - this is default automatic load mode. If initial load is not required for location dagster checks 
location last load timestamp, adds timedelta for time slice to it, and if result timestamp is less than current time 
triggers the job.
- **manual load** - get recent (top 100) changesets for all locations, ignoring last update timestamp and initial 
load flag.

**Dagster**

By default dagster user interface is available at [http://localhost:3000](http://localhost:3000).

**dbt**

This project has no sepatare dbt service, it uses `dagster-dbt` module instead. All dbt models are exposed as dagster Assets. 
You can find them in 'Assets' tab in dagster UI. For better visualization click 'View global asset lineage'.

Dagster also handles dbt orchestration. You can build dbt models and run tests by selecting an Asset and clicking 
'Materiallize selected'. To build all models use 'Materiallize all' or run **run_dbt_modles** job.

Source code for dbt models is located at `dbt/` directory. You can make changes in models and import them into Dagster. 
On Assets tab click 'Reload definitions'. No restart required.

**cube**

By default cube user interface is available at [http://localhost:4000](http://localhost:4000).

**PostgreSQL**

If you need to connect to PostgreSQL database use 'localhost' for host and default 5432 port. Credentials can be found in 
`.env` file in 'TARGET_DB*' section.

## Next steps

This project is an MVP built in short time and lack of Python programming experience.
Backlog for further development:
- use [NamedTuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) for defining a LocationSpec
- use [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) istead of basic OSM API