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


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'entries', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        
        if not user:
            username_error ="User does not exist"
            return render_template('login.html', username_error = username_error)
        
        if user and user.password != password:
            password_error ="User password incorrect"
            return render_template('login.html', username=username, password_error = password_error)
    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error =""
    password_error =""
    verify_password_error=""
    existing_user_error=""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            existing_user_error ="Username already exists"
            return render_template('signup.html', existing_user_error=existing_user_error)

        if " " in username or len(username) < 3:
            username_error = "Not a valid username; must be 3 or more characters in length with no spaces"
            return render_template('signup.html', username_error = username_error)

        if " " in password or len(password) < 3:
            password_error = "Not a valid password; must be 3 or more characters in length with no spaces"
            password =""
            return render_template('signup.html', username = username, 
            password_error = password_error)

        if password != verify:
            verify_password_error = "Passwords do not match"
            verify = ""
            return render_template('signup.html', username = username,
            password=password, verify_password_error = verify_password_error)


        if not existing_user and not username_error and not password_error and not verify_password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username 
            return redirect('/newpost')
    
    else:
        return render_template('signup.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')
    

@app.route('/')
def index():
    blog_users = User.query.all()
    return render_template('index.html', blog_users= blog_users)

@app.route('/blog', methods=['POST', 'GET'])
def entries():
    user_entries = request.args.get('user')
    if user_entries:
        indiv_entries = Blog.query.filter_by(owner_id = user_entries).all()
        return render_template('indiv-user-posts.html', indiv_entries=indiv_entries)
    
    entry_id = request.args.get('id')
    if entry_id:
        entry = Blog.query.get(entry_id)
        return render_template('display.html', entry=entry )
    
    else:
        entries = Blog.query.all()
        return render_template('all-entries.html', all_entries = entries)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body, owner)
        two_errors = ""
        title_error = ""
        body_error = ""

        if blog_title == "" and blog_body == "":
            two_errors = 'Please enter a title and content for the blog entry'
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, two_errors=two_errors)

        if blog_title == "":
            title_error = "Please enter a title" 
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, title_error = title_error) 
            
        if blog_body == "":
            body_error = "Please enter content for the blog entry"
            return render_template ('add-a-new-post.html', title= blog_title, body= blog_body, body_error= body_error)
    
        else:    
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))
    else:
        return render_template('add-a-new-post.html')


if __name__ == '__main__':
    app.run()