from dagster import asset
from xml.etree.ElementTree import XMLParser
import pandas as pd
import requests

@asset
def get_cities_coordinates() -> pd.DataFrame:
    coord_l = [
        ['St.Petersburg', 29.65, 59.75, 30.65, 60.10],
    ]
    coord_df = pd.DataFrame(coord_l, columns=['city', 'min_lon', 'min_lat', 'max_lon', 'max_lat'])
    print(coord_df)
    return coord_df

@asset(deps=[get_cities_coordinates])
def test_osm_get() -> None:
    api_url = "https://api.openstreetmap.org/api/0.6/changesets"
    cities_df = get_cities_coordinates()
    for ind in cities_df.index:
        bbox_str = "{},{},{},{}".format(
                cities_df['min_lon'][ind],
                cities_df['min_lat'][ind],
                cities_df['max_lon'][ind],
                cities_df['max_lat'][ind],
            )
        api_params = {'bbox': bbox_str, 'closed': 'true'}
        print(api_params)
        r = requests.get(api_url, params=api_params)
        print(r.status_code)
        if r.status_code == requests.codes.ok:
            parser = XMLParser()
            parser.feed(r.text)
            xml_root = parser.close()
            for changeset in xml_root.findall('changeset'):
                #print("ID: " + changeset.get('id'))
                print(changeset.items())
                continue