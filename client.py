import os
import json
import time
import requests

from errors import raise_for_view_error


class BoxViewClient(object):
    def __init__(self, api_token=None, url=None, upload_url=None):

        if not api_token:
            api_token = os.environ.get('BOX_VIEW_TOKEN')

        if not api_token:
            raise ValueError('Specify a Box View API token')

        self.url = url or 'https://view-api.box.com/1'
        self.upload_url = upload_url or 'TODO'

        headers = {'Authorization': 'Token {0}'.format(api_token)}

        self.requests = requests.session()
        self.requests.headers = headers

    @raise_for_view_error
    def get_document(self, document_id):
        """
        """

        resource = '{0}/documents/{1}'.format(
            self.url,
            document_id
        )

        response = self.requests.get(resource)

        return response

    @raise_for_view_error
    def create_session(self, document_id, expires_at=None):
        """
        """
        MAX_RETRIES = 310

        resource = '{0}/sessions'.format(self.url)
        headers = {'Content-type': 'application/json'}
        data = {'document_id': document_id}
        if expires_at:
            data['expires_at'] = expires_at

        count = 0
        while True:
            response = self.requests.post(resource, headers=headers, data=json.dumps(data))

            if response.headers.get('Retry-After') is None:
                break

            count += 1
            if count > MAX_RETRIES:
                raise Exception('Exceeded max retries')

            time.sleep(int(response.headers.get('Retry-After')))

        return response
