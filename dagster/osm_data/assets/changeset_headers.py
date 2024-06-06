from dagster import asset
from pandas import DataFrame

import time
import requests
from datetime import datetime
from xml.etree.ElementTree import XMLParser

from . import OSM_API_URL_BASE

@asset
def changeset_headers(cities_coordinates: DataFrame) -> DataFrame:
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
    col_names = [
        'utc_timestamp',
        'city',
        'changeset_id',
        'closed_at',
        'user',
        'comment',
        'source',
    ]
    chst_headers_df = DataFrame(chst_headers_l, columns=col_names)
    return chst_headers_df