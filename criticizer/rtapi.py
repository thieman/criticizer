""" RottenTomatoes API implementation. """

import requests

class RTAPI(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://api.rottentomatoes.com/api/public/v1.0/'

    def _get(self, endpoint, payload={}, full_url=False):
        url = endpoint if full_url else ''.join([self.base_url, endpoint])
        payload['apikey'] = self.api_key
        return requests.get(url, params=payload)

    def _post(self, endpoint, payload={}, full_url=False):
        url = endpoint if full_url else ''.join([self.base_url, endpoint])
        payload['apikey'] = self.api_key
        return requests.post(url, data=payload)

    def search(self, movie_title):
        return self._get('movies.json', {'q': movie_title}).json()

    def critics(self, movie_title):

        movie_docs = self.search(movie_title).get('movies', None)
        if not movie_docs:
            raise ValueError('could not find movie {}'.format(movie_title))
        movie_doc = movie_docs[0]

        reviews_url = movie_doc.get('links', {}).get('reviews')
        if not reviews_url:
            name = movie_doc.get('title', movie_doc.get('id', None))
            raise KeyError('no reviews for {}'.format(name))

        api_result = self._get(reviews_url, {}, True).json()

        return dict({'reviews': api_result.get('reviews', [])}.items() +
                    {'title': movie_doc.get('title', None),
                     'id': movie_doc.get('id', None)}.items())
