from ReadingApp import app
from flask import render_template, redirect, url_for, flash, request
from ReadingApp.models import User, Books
from ReadingApp.forms import RegisterForm, LoginForm, BookForm
from ReadingApp import db
from flask_login import login_user, logout_user, current_user, login_required

@app.route("/")
def home_page():
    return render_template('index.html')

@app.route("/input", methods=['GET','POST'])
def input_page():
    form = BookForm()
    if request.method == "POST":
        add_to_bookshelf = Books(title=form.title.data,
                                  subject=form.subject.data,
                                  hours=form.hours.data,
                                 input_user=current_user.id)
        db.session.add(add_to_bookshelf)
        db.session.commit()
        flash(f"Book added successfully! {add_to_bookshelf.title}, is on your bookshelf", category='success')



        return redirect(url_for('input_page'))

    return render_template('input.html',form=form)

@app.route("/dashboard")
def dashboard_page():
    return render_template('dashboard.html')

@app.route("/profile")
def profile_page():
    return render_template('profile.html')

@app.route("/register", methods=['GET','POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))

    if form.errors != {}: #If there are not errors from the validator
        for err_msg in form.errors.values():
            print(f'There was an error: {err_msg}')

    return render_template('register.html',form=form)

@app.route("/login", methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'You are now logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username or password does not match!', category='danger')
            flash('Username or password does not match!', category='danger')


    return render_template('login.html', form=form)


@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home_page'))



