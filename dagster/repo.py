from dagster import asset, op, define_asset_job, Definitions
from xml.etree.ElementTree import XMLParser
from datetime import datetime
import pandas as pd
import requests
import time

OSM_API_URL_BASE = "https://api.openstreetmap.org/api/0.6/"

@asset
def cities_coordinates() -> pd.DataFrame:
    coord_l = [
        ['St.Petersburg', 29.65, 59.75, 30.65, 60.10],
    ]
    coord_df = pd.DataFrame(coord_l, columns=['city', 'min_lon', 'min_lat', 'max_lon', 'max_lat'])
    return coord_df

@asset
def changeset_headers(cities_coordinates: pd.DataFrame) -> pd.DataFrame:
    api_url = OSM_API_URL_BASE + "changesets"
    utc_timestamp = datetime.utcfromtimestamp(time.time())
    chst_headers_l = []
    for ind in cities_coordinates.index:
        bbox_str = "{},{},{},{}".format(
                cities_coordinates['min_lon'][ind],
                cities_coordinates['min_lat'][ind],
                cities_coordinates['max_lon'][ind],
                cities_coordinates['max_lat'][ind],
            )
        api_params = {'bbox': bbox_str, 'closed': 'true'}
        r = requests.get(api_url, params=api_params)
        if r.status_code == requests.codes.ok:
            parser = XMLParser()
            parser.feed(r.text)
            xml_root = parser.close()
            for l_changeset in xml_root.findall('changeset'):
                comment = str()
                source = str()
                for l_tag in l_changeset.iter('tag'):
                    if l_tag.get('k') == 'comment':
                        comment = l_tag.get('v')
                    if l_tag.get('k') in ['source', 'imagery_used']:
                        source = l_tag.get('v')
                chst_current_l = [
                    utc_timestamp,
                    cities_coordinates['city'][ind],
                    l_changeset.get('id'),
                    l_changeset.get('closed_at'),
                    l_changeset.get('user'),
                    comment,
                    source,
                ]
                chst_headers_l.append(chst_current_l)
    chst_headers_df = pd.DataFrame(chst_headers_l, columns=['utc_timestamp', 'city', 'changeset_id', 'closed_at', 'user', 'comment', 'source'])
    return chst_headers_df

@asset
def changeset_data(changeset_headers: pd.DataFrame) -> pd.DataFrame:
    utc_timestamp = datetime.utcfromtimestamp(time.time())
    chst_data_l = []
    for ind in changeset_headers.index:
        chst_id = changeset_headers['changeset_id'][ind]
        api_url = OSM_API_URL_BASE + "changeset/" + chst_id + "/download"
        r = requests.get(api_url)
        if r.status_code == requests.codes.ok:
            parser = XMLParser()
            parser.feed(r.text)
            xml_root = parser.close()
            for l_action in xml_root:
                action = l_action.tag
                for l_elem_type in l_action:
                    elem_type = l_elem_type.tag
                    elem_id = l_elem_type.get('id')
                    k = str()
                    v = str()
                    for l_tag in l_elem_type.iter('tag'):
                        k = l_tag.get('k')
                        v = l_tag.get('v')
                        chst_data_current_l = [
                            utc_timestamp,
                            chst_id,
                            action,
                            elem_type,
                            elem_id,
                            k,
                            v,
                        ]
                        chst_data_l.append(chst_data_current_l)
    chst_data_df = pd.DataFrame(chst_data_l, columns=['utc_timestamp', 'chst_id', 'action', 'elem_type', 'elem_id', 'k', 'v'])
    return chst_data_df

get_osm_changeset_data = define_asset_job(name='get_osm_changeset_data', selection=['cities_coordinates', 'changeset_headers', 'changeset_data'])

defs = Definitions(
    assets=[cities_coordinates, changeset_headers, changeset_data],
    jobs=[get_osm_changeset_data],
)