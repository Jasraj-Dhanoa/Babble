from flask import request, jsonify, Blueprint, g, abort, make_response, render_template, current_app
from flask_restful import Resource, Api
from flaskblog.models import User, Posts, post__schema, posts__schema
import json
from flaskblog import db, ma, bcrypt
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

user_api = Blueprint('user_api', __name__)
auth = HTTPBasicAuth()
    
#providing time based authetication token based on user email and password
@user_api.route('/api_login',  methods=['POST', 'GET'])
def api_login():
    user_email = request.json['user_email']
    user_password = request.json['password']
    user = User.query.filter_by(email=user_email).first()

    if user and bcrypt.check_password_hash(user.password, user_password):
        token = user.generate_auth_token()
        return token
    else:
        return ('credentials not valid')
        
#get all posts
@user_api.route('/getPosts', methods=['POST', 'GET'])
def getPosts():
    all_posts = Posts.query.all()
    result = posts__schema.dump(all_posts)
    return jsonify(result)

#get specfic post
@user_api.route("/getPost/<int:post_num>", methods=['GET'])
def getPost(post_num):
    post = Posts.query.get(post_num)
    return post__schema.jsonify(post)

#add Post to database using token
@user_api.route("/addPost", methods = ['POST'])
def addPost():
    token = request.headers['token']
    token_validity = User.verify_auth_token(token=token)
    if token_validity:
        title = request.json['title']
        content = request.json['content']
        user_id = request.json['user_id']

        post = Posts(title=title, content=content, user_id=int(user_id))
        db.session.add(post)
        db.session.commit()

        return("Post has been created")

#delete Post from database using token
@user_api.route("/deletePost", methods = ['DELETE'])
def deletePost():
    token = request.headers['token']
    token_validity = User.verify_auth_token(token=token)
    if token_validity:
        post_id = request.json['post_id']
        post = Posts.query.get_or_404(int(post_id))
        db.session.delete(post)
        db.session.commit()
    return("Your post has been deleted")

#update Post in database using token
@user_api.route("/updatePost", methods = ['PUT'])
def updatePost():
    token = request.headers['token']
    token_validity = User.verify_auth_token(token=token)
    if token_validity:
        post_id = request.json['post_id']
        post = Posts.query.get_or_404(int(post_id))

        title = request.json['title']
        content = request.json['content']
        
        post.title = title
        post.content = content

        db.session.commit()

    return("Your post has been updated")