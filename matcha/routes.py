from matcha import db, socket, app
from functools import wraps
from flask import render_template, redirect, request, abort, url_for, flash, session
import os, secrets
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


# Create the route for the home page
@app.route('/')
def home():
    return render_template('home.html', logged_in=session.get('username'))

@app.route('/users')
def users():
    users = list(db.users())
    return render_template('users.html', logged_in=session.get('username'), users=users)


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
        'sex': 'bi-sexual',
        'interests': [],
        'flirts' : [],
        'flirted' : [],
        'matched' : [],
        'image_name': 'default.png'
    }

    if request.method == 'POST':
        details['username'] = request.form.get('username') 
        details['firstname'] = request.form.get("firstname")
        details['lastname'] = request.form.get('lastname')
        details['email'] = request.form.get('email')
        details['password'] = request.form.get('password')

        if not details['username']:
            errors.append('The username cannot be empty')
        if db.get_user({'username': details['username']}):
            errors.append('The username is already taken')
        if db.get_user({'email' : details['email']}):
            errors.append('The email is already taken!')
        
        if not errors:
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
        query = [ 
            { 'username': details['username'] },
            {'password' : details['password']} 
        ]

        if not (db.get_user({'$and': query})):
            errors.append('Incorrect username and email combo')
        
        if not errors:
            session['username'] = details['username']
            flash('Successful login', 'success')
            return redirect( url_for('home') )
        for error in errors:
            flash(error, 'danger')
    return render_template('login.html', details=details)



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