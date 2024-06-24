from decimal import Decimal
from .schema.location import LocationSpec

# ============= Setup tables and initial data =============

# Initial locations
INITIAL_LOCATIONS = {
    0:  LocationSpec({
            'location_name': 'St.Petersburg',
            'min_lon': Decimal('30.1245'),
            'min_lat': Decimal('59.8086'),
            'max_lon': Decimal('30.5653'),
            'max_lat': Decimal('60.0926'),
    }),
    1:  LocationSpec({
            'location_name': 'Moscow',
            'min_lon': Decimal('37.3260'),
            'min_lat': Decimal('55.5752'),
            'max_lon': Decimal('37.8754'),
            'max_lat': Decimal('55.9207'),
    }),
    2:  LocationSpec({
            'location_name': 'Kazan',
            'min_lon': Decimal('49.0007'),
            'min_lat': Decimal('55.6805'),
            'max_lon': Decimal('49.3358'),
            'max_lat': Decimal('55.8940'),
    }),
    3:  LocationSpec({
            'location_name': 'Yekaterinburg',
            'min_lon': Decimal('60.4866'),
            'min_lat': Decimal('56.7365'),
            'max_lon': Decimal('60.7139'),
            'max_lat': Decimal('56.9191'),
    }),
    4:  LocationSpec({
            'location_name': 'Krasnodar',
            'min_lon': Decimal('38.8744'),
            'min_lat': Decimal('44.9573'),
            'max_lon': Decimal('39.1587'),
            'max_lat': Decimal('45.1443'),
    }),
    5:  LocationSpec({
            'location_name': 'Ufa',
            'min_lon': Decimal('55.8720'),
            'min_lat': Decimal('54.6691'),
            'max_lon': Decimal('56.1607'),
            'max_lat': Decimal('54.8460'),
    }),
    6:  LocationSpec({
            'location_name': 'Novosibirsk',
            'min_lon': Decimal('82.7016'),
            'min_lat': Decimal('54.9212'),
            'max_lon': Decimal('83.0862'),
            'max_lat': Decimal('55.1600'),
    }),
    7:  LocationSpec({
            'location_name': 'Vladivostok',
            'min_lon': Decimal('131.8328'),
            'min_lat': Decimal('43.0546'),
            'max_lon': Decimal('132.0011'),
            'max_lat': Decimal('43.1954'),
    }),
}