from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'DS785HOsdf754KNm'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash= make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username_error = ''
    password_error = ''
    verify_password_error = ''


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        existing_user = User.query.filter_by(username=username).first()

        if username == "":
            username_error = "Invalid Username. Please choose a username!"
        if password == "":
            password_error = "Invalid Password. Please choose a password!"
        if verify_password == "":
            verify_password_error = "Passwords Do Not Match!"

        if verify_password != password:
            verify_password_error = "Passwords Do Not Match!" 

        if len(username) > 20 or len(username) < 3:
            username_error = "Invalid Username. Username must be between 3 and 20 characters long."
        if len(password) > 20 or len(password) < 3:
            password_error = "Invalid Password. Password must be between 3 and 20 characters long."
       
        if existing_user:
            username_error = "Username already exsit!"

        if not existing_user and not password_error and not username_error and not verify_password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")

    return render_template('signup.html', username_error=username_error, password_error=password_error,
                            verify_password_error=verify_password_error, username=username)

@app.route('/login', methods=['POST', 'GET'])
def login():

    username_error = ''
    password_error = ''
    username = ''


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            username_error = "Username does not exsit!"
        else:
            password_error = "Password incorrect!"
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html', username=username, username_error=username_error,
                            password_error=password_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog')
def blog():
    
    post_id = request.args.get('id')
    user_id = request.args.get('userid')
    
    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html', blog=single_post )
    if user_id:
        users_post = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user.html', users_post=users_post)
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    blog_title = ''
    blog_body = ''
    title_error = ''
    body_error = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if blog_title == "":
            title_error = "Please enter a title"
        if blog_body == "":
            body_error = "Please enter some text"

        if not title_error and not body_error:
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            post = new_post.id
            return redirect('/blog?id={0}'.format(post))

    return render_template('newpost.html', title_error=title_error, body_error=body_error,
                            blog_title=blog_title, blog_body=blog_body)


if __name__ == "__main__":
    app.run()