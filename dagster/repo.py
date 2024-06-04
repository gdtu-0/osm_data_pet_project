from dagster import asset
from xml.etree.ElementTree import XMLParser
import requests

@asset
def test_osm_get() -> None:
    api_url = "https://api.openstreetmap.org/api/0.6/changesets"
    api_params = {'bbox': '29.6562,59.7163,30.6711,60.1757', 'closed': 'true'}
    r = requests.get(api_url, params=api_params)
    if r.status_code == requests.codes.ok:
        parser = XMLParser()
        parser.feed(r.text)
        xml_root = parser.close()
        for changeset in xml_root.findall('changeset'):
            print("ID: " + changeset.get('id'))
            print(changeset.items())
            continue