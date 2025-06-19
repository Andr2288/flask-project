from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:1234567890@localhost/flask_crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def index():
    users = User.query.all()
    posts = Post.query.all()
    return render_template('index.html', users=users, posts=posts)

# User CRUD
@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        flash('User created!')
        return redirect(url_for('users'))
    return render_template('create_user.html')

@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('User updated!')
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!')
    return redirect(url_for('users'))

# Post CRUD
@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@app.route('/posts/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = request.form['user_id']
        
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created!')
        return redirect(url_for('posts'))
    
    users = User.query.all()
    return render_template('create_post.html', users=users)

@app.route('/posts/<int:id>')
def view_post(id):
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).all()
    users = User.query.all()
    return render_template('view_post.html', post=post, comments=comments, users=users)

@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.user_id = request.form['user_id']
        db.session.commit()
        flash('Post updated!')
        return redirect(url_for('posts'))
    
    users = User.query.all()
    return render_template('edit_post.html', post=post, users=users)

@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!')
    return redirect(url_for('posts'))

# Comment CRUD
@app.route('/comments/create/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    content = request.form['content']
    user_id = request.form['user_id']
    
    comment = Comment(content=content, post_id=post_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()
    flash('Comment added!')
    return redirect(url_for('view_post', id=post_id))

@app.route('/comments/<int:id>/delete', methods=['POST'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted!')
    return redirect(url_for('view_post', id=post_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)