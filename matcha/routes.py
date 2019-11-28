from matcha import db, socket, app
from functools import wraps
from datetime import datetime
from flask import render_template, redirect, request, abort, url_for, flash, session
import os, secrets, re, bcrypt
from werkzeug import secure_filename
from PIL import Image


def save_picture(form_pic):
    rand_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_pic.filename))
    pic_fn =  rand_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_fn)

    # form_pic.save(pic_path)
    i = Image.open(form_pic.stream)
    i.thumbnail((200,200))

    i.save(pic_path)
    return pic_fn



def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('username') is None:
            flash("Please login in first", 'info')
            return redirect( url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def finish_profile(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(session['username'])
        user = db.get_user({'username':session.get('username')})
        if user['completed'] == 0:
            flash("Please finish your profile first", 'info')
            return redirect( url_for('profile', next=request.url))
        return f(*args, **kwargs)
    return wrapper


# Create the route for the home page
@app.route('/')
@login_required
@finish_profile
def home():
    posts = db.get_posts()
    return render_template('home.html', logged_in=session.get('username'), posts=posts)


@app.route('/users')
@login_required
@finish_profile
def users():
    users = list(db.users())
    current_user = db.get_user({'username' : session.get('username')})
    return render_template('users.html', logged_in=session.get('username'), users=users, current_user=current_user)


# Handle the user registration
# --! DO NOT FORGET TO ADD THE PASSWORD VALIDATION FOR THE USER
@app.route('/register', methods=['GET', 'POST'])
def register():
    errors = []
    details = {
        'username' : '',
        'firstname' : '',
        'lastname' : '',
        'email' : '',
        'password' : '',
        'gender': '',
        'sex': 'bi-sexual',
        'bio': '',
        'interests': [],
        'flirts' : [],      # like
        'flirted' : [],     # liked
        'matched' : [],
        'views' : [],
        'fame-rating': 0,
        'location': [],
        'image_name': 'default.png',
        'token': secrets.token_hex(16),
        'completed': 0,
        'email_confirmed': 0

    }

    if request.method == 'POST':
        details['username'] = request.form.get('username') 
        details['firstname'] = request.form.get("firstname")
        details['lastname'] = request.form.get('lastname')
        details['email'] = request.form.get('email')
        details['password'] = request.form.get('password')
        passwd_confirm = request.form.get('password_confirm')

        # Check the users username
        if not details['username']:
            errors.append('The username cannot be empty')
        if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', details['username']):
            errors.append('The username must be an alpha numeric value')
        if db.get_user({'username': details['username']}):
            errors.append('The username is already taken')
        # Check the users email
        if db.get_user({'email' : details['email']}):
            errors.append('The email is already taken!')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$', details['email']):
            errors.append('invalid email format')
        # check the users password
        if not re.match('[A-Za-z0-9]', details['password']):
            errors.append('The password must have an uppercase, lowercase and a digit')
        if passwd_confirm != details['password']:
            errors.append('The two passwords do not match')
        # Check the users firstname
        if not re.match('^[A-Z][a-zA-Z-]{1,24}$', details['firstname']):
            errors.append('A name but start with a capital letter, and a have atlease 25 characters')
        # Check the user lastname
        if not re.match('^[A-Z][a-zA-Z-]{1,24}$', details['lastname']):
            errors.append('The lastname must start with a capital letter, and have 2-24 charaters')

        
        if not errors:
            salt = bcrypt.gensalt()
            details['password'] = bcrypt.hashpw(details['password'].encode('utf-8'), salt)
            db.register_user(details)
            flash ("Successful registration", 'success')
            return redirect( url_for('login') )

        for error in errors:
            flash(error, 'danger')

    return render_template('register.html', details=details)



@app.route('/login', methods = ['GET', 'POST'])
def login():
    errors = []
    details = {
        'username': '',
        'password': ''
    }

    if request.method == 'POST':
        details['username'] = request.form.get('username')
        details['password'] = request.form.get('password')
        user = db.get_user({'username': details['username']}, {'password': 1})
        print(user)

        if not user:
            errors.append("Incorrect username or password")            
        elif not bcrypt.checkpw(details['password'].encode('utf-8'), user['password']):
            errors.append('Incorrect username or password') 

        if not errors:
            session['username'] = details['username']
            flash('Successful login', 'success')
            return redirect( url_for('home') )
        for error in errors:
            flash(error, 'danger')
    return render_template('login.html', details=details)


# Route for the logout
@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    return redirect( url_for('home') )


# Route for the profile page.
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.get_user({'username' : session.get('username')})
    errors = []
    
    if request.method == 'POST':
        if request.form.get('submit') == 'update':
            username = request.form.get('username')
            email = request.form.get('email')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            image_file = request.files.get('image')

            if user['username'] != username and db.get_user({'username': username}):
                errors.append("The username is already taken please chose another")
            else:
                user['username'] = username
                session['username'] = username
            
            if user['email'] != email and db.get_user({'email' : email}):
                errors.append("The email is already taken please chose another one")
            else:
                user['email'] = email
            
            user['firstname'], user['lastname'] = firstname, lastname

            if image_file:
                pic_name = save_picture(image_file)
                user['image_name'] = pic_name

            if not errors:
                db.update_user(user['_id'], user)
                return redirect( url_for('profile') )
            
            for error in errors:
                flash(error, 'danger')

    return render_template('profile.html', logged_in=session.get('username'), user=user)


# Route for the user posts
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
@finish_profile
def new_post():
    user = db.get_user({'username':session.get('username')})
    post = {
        'author': user,
        'title': '',
        'content': '',
        'date_posted': ''
    }

    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')
        post['date_posted'] = datetime.utcnow()

        db.add_post(post)
        return redirect( url_for('home') )
    return render_template('create_post.html', logged_in=session.get('username'))
    

# Route for veiwing the post
@app.route('/post/<post_id>')
@login_required
def post(post_id):
    post = db.get_post(post_id)

    return render_template('post.html', post=post, logged_in=session.get('username'))


# Route for editing the post
@app.route('/post/<string:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = db.get_post(post_id)
    if session.get('username') != post['author']['username']:
        abort(403)
    
    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')

        db.update_post(post)
        return redirect( url_for('post', post_id=post_id))
    return render_template('update_post.html', logged_in=session.get('username'), post=post)

# Route for deleting a single post.
@app.route('/post/<string:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = db.get_post(post_id)
    if session.get('username') != post['author']['username']:
        abort(403)
    db.delete_post(post)
    return redirect( url_for('home') )


@app.route('/user/flirt/<string:username>', methods=['GET', 'POST'])
@login_required
def flirt(username):
    flirter = db.get_user({'username':session.get('username')}, {'flirts': 1, 'username' : 1})
    print("flirter", flirter)
    flirtee = db.get_user({'username':username}, {'flirted': True, 'username' : 1})
    print('flirtee', flirtee)

    # Flirted is used for people who have liked you.
    flirtee['flirted'].append(session.get('username'))
    print("flirtee", flirtee)
    # Flirts is for users who you have like
    flirter['flirts'].append(flirtee['username'])
    
    db.update_flirts(flirter['_id'], {'flirts': flirter['flirts']})
    db.update_flirts(flirtee['_id'], {'flirted': flirtee['flirted']})

    return redirect( url_for('users') )