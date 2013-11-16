""" Criticizer backend using Flask. """

import json

import yaml
from flask import Flask, request, jsonify

from rtapi import RTAPI

app = Flask(__name__)

config = yaml.load(open('criticizer/config.yml', 'r').read())
rt = RTAPI(config.get('api_key'))

@app.route('/movies', methods=['GET'])
def movies():
    """ Return JSON list of the given movies from the search API. """
    data = json.loads(request.args.get('data')).get('movies')
    return jsonify(movies=[rt.search(movie) for movie in data])

@app.route('/reviews', methods=['GET'])
def reviews():
    """ Return JSON list of the reviews of the given movies. """
    data = json.loads(request.args.get('data')).get('movies')
    result = [rt.reviews(movie) for movie in data]
    return jsonify(reviews=result)

def init_app():
    app.debug = True
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    init_app()
