from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def blog():

    post_id = request.args.get('id')
    
    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html', blog=single_post )

    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if blog_title == "":
            title_error = "Please enter a title"
        if blog_body == "":
            body_error = "Please enter some text"

        if not title_error and not body_error:
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            post = new_post.id
            return redirect('/blog?id={0}'.format(post))

    return render_template('newpost.html', title_error=title_error, body_error=body_error)


if __name__ == "__main__":
    app.run()