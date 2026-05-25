#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

# Class: Login
class Login(Resource): 
    def post(self): 
        # get username: request JSON
        data = request.get_json()
        print("DEBUG: Received payload from frontend ->", data)

        username = data.get('username') or list(data.values())[0]

        # find user: db by username 
        user = User.query.filter(User.username == username).first()

        if user: 
            # set session['user_id']: found user's ID
            session['user_id'] = user.id

            # return user: JSON & 200 status code 
            user_json = UserSchema().dump(user)
            return make_response(user_json, 200)

        print(f"DEBUG: Could not find user '{username}' in the database.")
        return {'error': 'Unauthorized'}, 401

# Class: Logout 
class Logout(Resource): 
    def delete(self): 
        # remove value: session['user_id']
        session['user_id'] = None

        # return: no data & 204 (No Content) status code
        return {}, 204

# Class: Check Session 
class CheckSession(Resource): 
    def get(self): 
        # Get current value: session['user_id']
        user_id = session.get('user_id')

        # Check: session has user_id
        if user_id: 
            user = User.query.filter(User.id == user_id).first()
            if user: 
                user_json = UserSchema().dump(user)
                return make_response(user_json, 200)
        # session has no user_id OR user not found 
        return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

# routes: authentication steps
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
