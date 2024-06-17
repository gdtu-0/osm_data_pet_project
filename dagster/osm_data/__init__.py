from dagster import Definitions

from .assets import ASSET_DEFINITIONS
from .resources import PROJECT_RESOURCES
from .jobs import PROJECT_JOBS

# Set dagster definitions
defs = Definitions(
    assets = [*ASSET_DEFINITIONS],
    jobs = PROJECT_JOBS,
    resources = PROJECT_RESOURCES
)