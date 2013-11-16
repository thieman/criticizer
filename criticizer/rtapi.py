""" RottenTomatoes API implementation. """

import requests

class RTAPI(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://api.rottentomatoes.com/api/public/v1.0/'

    def _get_url(self, endpoint, full_url):
        return endpoint if full_url else ''.join([self.base_url, endpoint])

    def _get(self, endpoint, payload={}, full_url=False):
        url = self._get_url(endpoint, full_url)
        payload['apikey'] = self.api_key
        return requests.get(url, params=payload)

    def _post(self, endpoint, payload={}, full_url=False):
        url = self._get_url(endpoint, full_url)
        payload['apikey'] = self.api_key
        return requests.post(url, data=payload)

    def _get_all_pages(self, endpoint, extract_key, payload={}, full_url=False):
        """ Return the concatenated value of extract_key over all pages. """

        url = self._get_url(endpoint, full_url)
        payload['page'] = 1
        payload['page_limit'] = 50
        first_result = self._get(url, payload, full_url).json()

        extracted = first_result.get(extract_key, [])
        total = first_result.get('total', 0)
        page = 2

        while total >= 50:
            payload['page'] = page
            api_result = self._get(url, payload, full_url).json()
            extracted.extend(api_result.get(extract_key, []))
            page += 1
            total -= 50

        return extracted

    def search(self, movie_title):
        return self._get('movies.json', {'q': movie_title}).json()

    def reviews(self, movie_title):

        movie_docs = self.search(movie_title).get('movies', None)
        if not movie_docs:
            raise ValueError('could not find movie {}'.format(movie_title))
        movie_doc = movie_docs[0]

        reviews_url = movie_doc.get('links', {}).get('reviews')
        if not reviews_url:
            name = movie_doc.get('title', movie_doc.get('id', None))
            raise KeyError('no reviews for {}'.format(name))

        reviews = self._get_all_pages(reviews_url, 'reviews',
                                      {"review_type": "all"}, True)
        return dict({'reviews': reviews}.items() +
                    {'id': movie_doc.get('id', None),
                     'title': movie_doc.get('title', None)}.items())
