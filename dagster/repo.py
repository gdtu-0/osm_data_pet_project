from dagster import asset
from xml.etree.ElementTree import XMLParser
from datetime import datetime
import pandas as pd
import requests
import time

@asset
def get_cities_coordinates() -> pd.DataFrame:
    coord_l = [
        ['St.Petersburg', 29.65, 59.75, 30.65, 60.10],
    ]
    coord_df = pd.DataFrame(coord_l, columns=['city', 'min_lon', 'min_lat', 'max_lon', 'max_lat'])
    return coord_df

@asset
def get_changeset_headers(get_cities_coordinates: pd.DataFrame) -> pd.DataFrame:
    api_url = "https://api.openstreetmap.org/api/0.6/changesets"
    cities_df = get_cities_coordinates
    utc_timestamp = datetime.utcfromtimestamp(time.time())
    chst_data_l = []
    for ind in cities_df.index:
        bbox_str = "{},{},{},{}".format(
                cities_df['min_lon'][ind],
                cities_df['min_lat'][ind],
                cities_df['max_lon'][ind],
                cities_df['max_lat'][ind],
            )
        api_params = {'bbox': bbox_str, 'closed': 'true'}
        r = requests.get(api_url, params=api_params)
        if r.status_code == requests.codes.ok:
            parser = XMLParser()
            parser.feed(r.text)
            xml_root = parser.close()
            for changeset in xml_root.findall('changeset'):
                comment = str()
                source = str()
                for tag in changeset.iter('tag'):
                    if tag.get('k') == 'comment':
                        comment = tag.get('v')
                    if tag.get('k') in ['source', 'imagery_used']:
                        source = tag.get('v')
                chst_current_l = [
                    utc_timestamp,
                    cities_df['city'][ind],
                    changeset.get('id'),
                    changeset.get('closed_at'),
                    changeset.get('user'),
                    comment,
                    source,
                ]
                chst_data_l.append(chst_current_l)
    chst_data_df = pd.DataFrame(chst_data_l, columns=['utc_timestamp', 'city', 'id', 'closed_at', 'user', 'comment', 'source'])
    return chst_data_df

@asset
def get_changeset_data(get_changeset_headers: pd.DataFrame) -> None:
    changeset_headers = get_changeset_headers
    pass