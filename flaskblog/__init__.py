#package, app initialization, ties everything together
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
from flask_marshmallow import Marshmallow

#instance of database
db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
# intilaize out extension
mail = Mail()



def create_app(Config_class=Config):
    # app var setting to instance of this flask class
    # __name__ indicates the name of module, __name__ can be equal to __main__
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize instances
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
      
    #importing blueprints
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    from flaskblog.api.users_api import user_api
    
    # register blueprints
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(user_api)
    
    # return the configured application
    return app
