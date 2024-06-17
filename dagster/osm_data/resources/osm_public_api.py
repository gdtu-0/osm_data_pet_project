from dagster import ConfigurableResource

import requests
from requests import Response

from xml.etree.ElementTree import XMLParser
from pandas import DataFrame # type: ignore

OSM_API_URL_BASE = "https://api.openstreetmap.org/api/0.6"

class OsmPublicApi(ConfigurableResource):
	"""Dagster resource definition for OSM Public API at
	https://api.openstreetmap.org/api/0.6/"""

	def get_closed_changesets_by_bbox(self, min_lon, min_lat, max_lon, max_lat) -> DataFrame:
		"""Returns pandas DataFrame with changeset header info at given coordinates of a bounding box

		min_lon (left) - is the longitude of the left (westernmost) side of the bounding box
		min_lat (bottom) - is the latitude of the bottom (southernmost) side of the bounding box
		max_lon (right) - is the longitude of the right (easternmost) side of the bounding box
		max_lat (top) - is the latitude of the top (northernmost) side of the bounding box
		"""

		api_url = f"{OSM_API_URL_BASE}/changesets"
		bbox_str = f"{min_lon},{min_lat},{max_lon},{max_lat}"
		api_params = {'bbox': bbox_str, 'closed': 'true'}
		r = requests.get(api_url, params = api_params)
		if r.status_code != requests.codes.ok:
			raise Exception('No connection to OSM Api')
		else:
			return DataFrame.from_dict(self._parse_xml_changeset_headers(xml_data = r))


	def _parse_xml_changeset_headers(self, xml_data: Response) -> list:
		"""Helper function for 'get_closed_changesets_by_bbox'
		to parse API xml output into pandas Dataframe"""

		parser = XMLParser()
		parser.feed(xml_data.text)
		xml_root = parser.close()
		chst_headers_l = []
		for l_changeset in xml_root.findall('changeset'):
			comment = str()		# comment and source are optional fields
			source = str()		# so we use empty strings as placeholdres
			for l_tag in l_changeset.iter('tag'):
				if l_tag.get('k') == 'comment':
					comment = l_tag.get('v')
				if l_tag.get('k') in ['source', 'imagery_used']:
					source = l_tag.get('v')
			chst_headers_l.append({
				'changeset_id':l_changeset.get('id'),
				'closed_at': l_changeset.get('closed_at'),
				'uid': l_changeset.get('uid'),
				'username': l_changeset.get('user'),
				'comment': comment,
				'source': source,
				'min_lat': float(l_changeset.get('min_lat')),
				'min_lon': float(l_changeset.get('min_lon')),
				'max_lat': float(l_changeset.get('max_lat')),
				'max_lon': float(l_changeset.get('max_lon')),
			})
		return chst_headers_l


	def get_changeset_data(self, changeset_ids) -> DataFrame:
		"""Returns pandas DataFrame with changeset data by changeset_id"""

		changeset_data_l =[]
		for changeset_id in changeset_ids:
			api_url = f"{OSM_API_URL_BASE}/changeset/{changeset_id}/download"
			r = requests.get(api_url)
			if r.status_code != requests.codes.ok:
				raise Exception('No connection to OSM Api')
			else:
				changeset_data_l.extend(self._parse_xml_cgangeset_data(xml_data = r))
		return DataFrame.from_dict(changeset_data_l)


	def _parse_xml_cgangeset_data(self, xml_data: Response) -> list:
		"""Helper function for 'get_changeset_data'
		to parse API xml output into pandas Dataframe"""

		parser = XMLParser()
		parser.feed(xml_data.text)
		xml_root = parser.close()
		chst_data_l = []
		for l_action in xml_root:
			action = l_action.tag
			for l_elem_type in l_action:
				elem_type = l_elem_type.tag
				elem_id = l_elem_type.get('id')
				chst_id = l_elem_type.get('changeset')
				k = str()		# All attributes of an element are stored
				v = str()		# as list of key-value pairs
				for l_tag in l_elem_type.iter('tag'):
					k = l_tag.get('k')
					v = l_tag.get('v')
					chst_data_l.append({
						'changeset_id': chst_id,
						'action': action,
						'elem_type': elem_type,
						'elem_id': elem_id,
						'k': k,
						'v': v,
					})
		return chst_data_l