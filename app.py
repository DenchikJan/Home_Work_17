# app.py
# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        if request.args.get('director_id') and request.args.get('genre_id') and request.args.get('page'):
            director_id = request.args.get('director_id')
            genre_id = request.args.get('genre_id')
            page = int(request.args.get('page'))
            offset_ = 10 * (page - 1)
            director_movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).limit(10).offset(offset_)
            response = movies_schema.dump(director_movies)
            return response, 201
        elif request.args.get('director_id') and request.args.get('page'):
            director_id = request.args.get('director_id')
            page = int(request.args.get('page'))
            offset_ = 10 * (page - 1)
            director_movies = db.session.query(Movie).filter(Movie.director_id == director_id).limit(10).offset(offset_)
            response = movies_schema.dump(director_movies)
            return response, 201
        elif request.args.get('genre_id') and request.args.get('page'):
            genre_id = request.args.get('genre_id')
            page = int(request.args.get('page'))
            offset_ = 10 * (page - 1)
            director_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).limit(10).offset(offset_)
            response = movies_schema.dump(director_movies)
            return response, 201
        elif request.args.get('page'):
            page = int(request.args.get('page'))
            offset_ = 10 * (page - 1)
            movies = db.session.query(Movie).limit(10).offset(offset_)
            response = movies_schema.dump(movies)
            return response, 200
        else:
            movies = db.session.query(Movie).all()
            response = movies_schema.dump(movies)
            return response, 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie).filter(Movie.id == mid).one()
        response = movie_schema.dump(movie)

        return response, 200

    def put(self, mid: int):
        movie = db.session.query(Movie).filter(Movie.id == mid).one()
        req_json = request.json

        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "", 204

    def patch(self, mid: int):
        movie = db.session.query(Movie).filter(Movie.id == mid).one()
        req_json = request.json

        if 'title' in req_json:
            movie.title = req_json.get('title')
        if 'description' in req_json:
            movie.description = req_json.get('description')
        if 'trailer' in req_json:
            movie.trailer = req_json.get('trailer')
        if 'year' in req_json:
            movie.year = req_json.get('year')
        if 'rating' in req_json:
            movie.rating = req_json.get('rating')
        if 'genre_id' in req_json:
            movie.genre_id = req_json.get('genre_id')
        if 'director_id' in req_json:
            movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "", 204

    def delete(self, mid: int):
        movie = db.session.query(Movie).filter(Movie.id == mid).one()
        db.session.delete(movie)
        db.session.commit()

        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        response = directors_schema.dump(directors)

        return response, 201

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        db.session.add(new_director)
        db.session.commit()

        return "", 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        director = db.session.query(Director).filter(Director.id == did).one()
        response = director_schema.dump(director)

        return response, 201

    def put(self, did: int):
        req_json = request.json
        director = db.session.query(Director).filter(Director.id == did).one()

        director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, did: int):
        director = db.session.query(Director).filter(Director.id == did).one()

        db.session.delete(director)
        db.session.commit()

        return "", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        response = genres_schema.dump(genres)

        return response, 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        db.session.add(new_genre)
        db.session.commit()

        return "", 201


@genre_ns.route('/<int:git>')
class GenreView(Resource):
    def get(self, git: int):
        genre = db.session.query(Genre).filter(Genre.id == git).one()
        response = genre_schema.dump(genre)

        return response, 200

    def put(self, git: int):
        req_json = request.json
        genre = db.session.query(Genre).filter(Genre.id == git).one()

        genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return "", 204

    def delete(self, did: int):
        genre = db.session.query(Genre).filter(Genre.id == did).one()

        db.session.delete(genre)
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
