from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:eska@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def all_entries():
    
    all_entries = Blog.query.all()
    return render_template('all-entries.html', all_entries = all_entries) 

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body)

        if blog_title == "" or blog_body == "":
            flash('Please enter a title and blog entry', 'error')
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body)
    
        else:    
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')
    else:
        return render_template('add-a-new-post.html')


if __name__ == '__main__':
    app.run()