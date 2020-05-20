from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Posts
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.actions import save_picture, send_reset_email
from flask import Blueprint
from flask_mail import Message


#creating instance of blueprint
users = Blueprint('users', __name__)

#not using global at variable and register them will application seprature time

@users.route('/testTask', methods=['GET'])
def testTask():
    return render_template('tasks.html')

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_passsword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_passsword)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #check is user exists and pass verfies
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            #log them in using our login extension
            login_user(user, remember=form.remember.data)
            #args is a dictionary, get method returns none if next doesn't exsist
            # getting the next page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    flash('Your have been logged out!', 'success')
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        #use sqlalchemy to easily change
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account information has been updated', 'success')
        # redirect due to post, get redirect pattern
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    #in models, image_file is name of stored image
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Posts.query.filter_by(author=user)\
        .order_by(Posts.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # user login check
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.get_reset_token()
        send_reset_email(user, token)
        flash('An email has been sent with instructions to reset you password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


#make sure token given is activate
@users.route("/reset_abc/<token>", methods=['GET', 'POST'])
def reset_abc(token):
    # user login check
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    #if valid, return user with its id(payload we passed to intial tokn)
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_passsword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_passsword
        db.session.commit()
        flash('Your password has been updated! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)