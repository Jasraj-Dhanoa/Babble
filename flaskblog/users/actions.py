import os
import secrets
from PIL import Image
from flask import url_for, current_app, flash
from flask_mail import Message
from flaskblog import mail
from flaskblog.models import User

def save_picture(form_picture):
    #randomize the name of the image
    random_hex = secrets.token_hex(8)
    # os module for file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # use root path attribute, gives full path to pkg directory
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    #resize
    output_size = (125,123)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #save in file folder, not in database
    i.save(picture_path)
    return picture_fn

def send_reset_email(user, token):
    #token = user.get_reset_token()
    # user message class to make email, external=true is to get absolute url not relative (we need full domain)
    msg = Message("Password Reset Request", sender="dhanoajazzy@gmail.com", recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_abc', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)