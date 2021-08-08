from dataclasses import is_dataclass, asdict
from flask import Flask
from injector import inject
from requests import Request, Session
from requests.exceptions import RequestException
from typing import List, Union, Dict
from urllib.parse import urljoin

from vc.exception import ThirdPartyException


class ApiProvider:
    session: Session
    base_uri: str
    token: str

    @inject
    def __init__(self, app: Flask):
        self.session = Session()
        self.base_uri = app.config.get('API_URL')
        self.token = app.config.get('API_TOKEN')

    def get(self, url) -> Union[Dict, List]:
        return self.request('GET', url)

    def put(self, url, data=None) -> Union[Dict, List]:
        return self.request('PUT', url, data)

    def request(self, method, url, data=None) -> Union[Dict, List]:
        headers = {
            "Authorization": "Bearer %s" % self.token
        }

        data = self.marshall(data) if data else {}

        request = Request(
            method,
            urljoin(self.base_uri, url),
            json=data,
            headers=headers
        )

        prepared_request = self.session.prepare_request(request)
        try:
            response = self.session.send(prepared_request)
            if response.status_code > 400:
                print("Error response from API: [%s] %s" % (
                    response.status_code,
                    response.text[:1024]
                ))
                raise ThirdPartyException(response.text[:1024])
        except RequestException as e:
            print("Error from API: %s" % e)
            raise ThirdPartyException.for_exception(e)
        return response.json()

    def marshall(self, data) -> Union[Dict, List, str]:
        if isinstance(data, list):
            return list(map(self.marshall, data))
        if is_dataclass(data):
            return asdict(data)
        return data
