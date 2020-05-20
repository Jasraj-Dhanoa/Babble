from flask import render_template, request, Blueprint
from flaskblog.models import Posts

#creating instance of blueprint
main = Blueprint('main', __name__)

#home page routing
@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Explore Blogs', posts=posts)

#about page routing
@main.route('/about')
def about():
    return render_template('about.html', title='About')