from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:eska@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id =db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def entries():
    entry_id = request.args.get('id')
    if entry_id:
        entry = Blog.query.filter_by(id=entry_id).first()
        return render_template('display.html', title= entry.title, body= entry.body)
    
    else:
        entries = Blog.query.all()
        return render_template('all-entries.html', all_entries = entries)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body, owner)
        two_errors = ""
        title_error = ""
        body_error = ""

        if blog_title == "" and blog_body == "":
            two_errors = 'Please enter a title and content for the blog entry'
            #flash('Please enter a title and content for the blog entry', 'error')
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, two_errors=two_errors)

        if blog_title == "":
            title_error = "Please enter a title"
            #flash('Please enter a title', 'error') 
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, title_error = title_error) 
            
        if blog_body == "":
            body_error = "Please enter content for the blog entry"
            #flash('Please enter content for the blog entry', 'error')
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, body_error= body_error)
    
        else:    
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))
    else:
        return render_template('add-a-new-post.html')


if __name__ == '__main__':
    app.run()