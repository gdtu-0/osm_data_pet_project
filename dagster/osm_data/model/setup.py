from .schema import LocationSpec

from decimal import Decimal

# Setup tables and data

# Initial locations
INITIAL_LOCATIONS = (
    LocationSpec(
        location_name = 'St.Petersburg',
        min_lon = Decimal('30.1245'),
        min_lat = Decimal('59.8086'),
        max_lon = Decimal('30.5653'),
        max_lat = Decimal('60.0926'),
    ),
    LocationSpec(
        location_name = 'Moscow',
        min_lon = Decimal('37.3260'),
        min_lat = Decimal('55.5752'),
        max_lon = Decimal('37.8754'),
        max_lat = Decimal('55.9207'),
    ),
    LocationSpec(
        location_name = 'Yekaterinburg',
        min_lon = Decimal('60.4866'),
        min_lat = Decimal('56.7365'),
        max_lon = Decimal('60.7139'),
        max_lat = Decimal('56.9191'),
    ),
)