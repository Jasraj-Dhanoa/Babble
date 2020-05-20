from datetime import datetime
from flaskblog import db, login_manager, ma
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app, url_for, abort, flash
from flask_script import Manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='defualt.jpg')
    password = db.Column(db.String(60), nullable=False)
     # adding token so can search for it through database and make it unique
    token = db.Column(db.String(32), index=True, unique=True)
    # has date and time when the token expires, security purposes
    token_expiration = db.Column(db.DateTime)
    # backref allows to use author attribute to get who created post
    # lazy means sqlachemy will load the data as neccesary in one go, will get all posts
    posts = db.relationship('Posts', backref='author', lazy=True)
    
    # password reset token sent within email
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    #static method: telling python not to except self argument
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # how our object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    #token generation for api
    def generate_auth_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'user_id': self.id })

    #user will only be able to access certain api endpoints if token is valid
    @staticmethod
    def verify_auth_token(token):
    # token is supposed to be in argument
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False # valid token, but expired, none
        except BadSignature:
            return False # invalid token
        #user = User.query.get(data['user_id'])
        return True

# Posts database
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # referecing table/column name (lower case user name)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # how object is printed
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
    
    #Defining output format using marshmallow
class PostsSchema(ma.Schema):
    class Meta:
        fields = ("title", "content", "user_id")

post__schema = PostsSchema()
posts__schema = PostsSchema(many=True)