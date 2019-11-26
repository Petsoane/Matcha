from matcha import db, socket, app
from flask import render_template, redirect, request, abort, url_for, flash, session



# Create the route for the home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/users')
def users():
    users = list(db.users())
    return render_template('users.html', users=users)
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