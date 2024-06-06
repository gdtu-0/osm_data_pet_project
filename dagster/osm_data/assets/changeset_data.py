from dagster import asset
from pandas import DataFrame

import time
import requests
from datetime import datetime
from xml.etree.ElementTree import XMLParser

from . import OSM_API_URL_BASE

@asset
def changeset_data(changeset_headers: DataFrame) -> DataFrame:
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
    col_names = [
        'utc_timestamp',
        'chst_id',
        'action',
        'elem_type',
        'elem_id',
        'k',
        'v',
    ]
    chst_data_df = DataFrame(chst_data_l, columns=col_names)
    return chst_data_df