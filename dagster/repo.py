from dagster import asset
from xml.etree.ElementTree import XMLParser
from datetime import datetime
import pandas as pd
import requests
import time

OSM_API_URL_BASE = "https://api.openstreetmap.org/api/0.6/"

@asset
def get_cities_coordinates() -> pd.DataFrame:
    coord_l = [
        ['St.Petersburg', 29.65, 59.75, 30.65, 60.10],
    ]
    coord_df = pd.DataFrame(coord_l, columns=['city', 'min_lon', 'min_lat', 'max_lon', 'max_lat'])
    return coord_df

@asset
def get_changeset_headers(get_cities_coordinates: pd.DataFrame) -> pd.DataFrame:
    api_url = OSM_API_URL_BASE + "changesets"
    cities_df = get_cities_coordinates
    utc_timestamp = datetime.utcfromtimestamp(time.time())
    chst_headers_l = []
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
                    cities_df['city'][ind],
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
def get_changeset_data(get_changeset_headers: pd.DataFrame) -> None:
    chst_headers = get_changeset_headers
    for ind in chst_headers.index:
        # print(chst_headers['changeset_id'][ind])
        chst_id = chst_headers['changeset_id'][ind]
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
                        print(chst_id, action, elem_type, elem_id, k, v)