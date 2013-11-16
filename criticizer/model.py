""" SQLAlchemy model definitions. """

from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)

    reviews = relationship('Review', backref='movie')

    def __init__(self, id, title):
        self.id = id
        self.title = title


class Critic(Base):
    __tablename__ = 'critic'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    publication = Column(String(255))

    reviews = relationship('Review', backref='critic')

    def __init__(self, name, publication=None):
        self.name = name
        self.publication = publication


class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movie.id'), index=True)
    critic_id = Column(Integer, ForeignKey('critic.id'), index=True)

    fresh = Column(Boolean, nullable=False)
    original_score = Column(String(50))
    quote = Column(String(500))
    url = Column(String(500))
    date = Column(DateTime)

    def __init__(self, fresh, original_score, quote, url, date):
        self.fresh = fresh
        self.original_score = original_score
        self.quote = quote
        self.url = url
        self.date = date

    def to_json(self):
        return {'movie': self.movie.title,
                'critic': self.critic.name,
                'publication': self.critic.publication,
                'fresh': self.fresh,
                'original_score': self.original_score,
                'quote': self.quote,
                'url': self.url,
                'date': self.date}
