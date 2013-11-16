""" Criticizer backend using Flask. """

import json

import yaml
from flask import Flask, request, jsonify, abort
import sqlalchemy
from dateutil import parser

from rtapi import RTAPI
from model import Base, Movie, Critic, Review

app = Flask(__name__)

engine = sqlalchemy.create_engine('sqlite:////home/travis/movie.db')
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

config = yaml.load(open('criticizer/config.yml', 'r').read())
rt = RTAPI(config.get('api_key'))

@app.route('/movies', methods=['GET'])
def movies():
    """ Return JSON list of the given movies from the search API. """
    data = json.loads(request.args.get('data')).get('movies')
    return jsonify(movies=[rt.search(movie) for movie in data])

@app.route('/review', methods=['GET'])
def review():
    """ Given a movie and critic, return a review if it exists.

    Publication may also be provided as an optional match on critic. """

    title = request.args.get('movie')
    critic = request.args.get('critic')
    publication = request.args.get('publication')
    if (not title) or (not critic):
        abort(400)

    query = session.query(Review, Movie, Critic).\
        filter(Review.movie_id == Movie.id).\
        filter(Review.critic_id == Critic.id).\
        filter(Movie.title == title).\
        filter(Critic.name == critic)

    if publication:
        query = query.filter(Critic.publication == publication)

    result = query.first()
    return jsonify(review=result[0].to_json() if result else {})

@app.route('/reviews', methods=['GET'])
def reviews():
    """ Return JSON list of the reviews of the given movies. """
    data = json.loads(request.args.get('data')).get('movies')

    # TODO: we'll need our own search, solr or something
    # TODO: adding stuff to backend should be async

    for movie in data:
        if session.query(Movie).filter_by(title=movie).count() == 0:
            # TODO: handle cases when movie cannot be added to the DB
            try:
                add_movie_to_backend(movie)
            except:
                pass

    # all movies exist in the backend at this point
    movies = [session.query(Movie).filter_by(title=movie).first()
              for movie in data]
    movies = filter(lambda x: x is not None, movies)
    reviews = [[review.to_json() for review in movie.reviews] for movie in movies]
    return jsonify(reviews=reviews)

@app.route('/critic', methods=['GET'])
def critic():
    """ Return all movies reviewed by a given critic.

    Takes in name and publication as JSON parameters."""

    name = request.args.get('name')
    publication = request.args.get('publication')
    if not name:
        abort(400)
    query = session.query(Critic).filter_by(name=name)
    if publication:
        query = query.filter_by(publication=publication)

    critic = query.first()
    reviews = [review.to_json() for review in critic.reviews] if critic else []
    return jsonify(reviews=reviews)

def add_movie_to_backend(title):

    result = rt.reviews(title)
    if not result:
        raise ValueError('no movie found for {}'.format(title))

    if session.query(Movie).filter_by(id=result['id']).count() != 0:
        raise ValueError('movie ID {} already exists'.format(result['id']))

    movie = Movie(result['id'], result['title'])

    if not result.get('reviews', []):
        raise KeyError('no reviews for {}'.format(title))

    for review in result.get('reviews', []):
        dt = parser.parse(review['date']) if review.get('date', None) else None
        review_obj = Review(review['freshness'] == 'fresh',
                            review.get('original_score', None),
                            review.get('quote', None),
                            review.get('url', None),
                            dt)

        critic_query = session.query(Critic).filter_by(name=review['critic'])
        if review.get('publication', None):
            critic_query = critic_query.filter_by(publication=review['publication'])

        critic = critic_query.first()
        if not critic:
            critic = Critic(review['critic'], review.get('publication', None))

        review_obj.movie = movie
        review_obj.critic = critic

        session.add(review_obj)

    session.commit()

def init_app():
    app.debug = True
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    init_app()
