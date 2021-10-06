from ReadingApp import app
from flask import render_template, redirect, url_for, flash, request
from ReadingApp.models import User, Books
from ReadingApp.forms import RegisterForm, LoginForm, BookForm
from ReadingApp import db
from flask_login import login_user, logout_user, current_user, login_required
import pandas as pd
from datetime import date
import json
import plotly
import plotly.express as px

@app.route("/")
def home_page():

    return render_template('index.html')

@app.route("/bookshelf", methods=['GET'])
def bookshelf_page():
    df1 = pd.read_csv('/Users/Evan/PycharmProjects/ReadingApp/ReadingApp/static/books.csv')
    df1 = df1.loc[df1['input_user'] == current_user.id]
    # df = df.drop(['input_user', 'hours','date'], axis=1)
    # df = df.drop_duplicates(subset='title')
    df2 = df1.groupby(['title'], as_index=False).min()
    df2 = df2.drop(['input_user', 'hours', 'input_user'], axis=1)
    df2 = df2.rename(columns={'date': 'Start date', 'title': 'Title', 'subject': 'Subject'})
    df3 = df1.groupby(['title'], as_index=False).max()
    df3 = df3.drop(['input_user', 'hours', 'input_user', 'subject','title'], axis=1)
    df3 = df3.rename(columns={'date': 'Finished date'})
    df4 = pd.concat([df2,df3], axis=1)



    return render_template('bookshelf.html',column_names=df4.columns.values, row_data=list(df4.values.tolist()),
                           link_column="Patient ID", zip=zip)

@app.route("/input", methods=['GET','POST'])
def input_page():
    form = BookForm()
    if request.method == "POST":
        add_to_bookshelf = Books(title=form.title.data,
                                  subject=form.subject.data,
                                  hours=form.hours.data,
                                 input_user=current_user.id,
                                 date=date.today())
        db.session.add(add_to_bookshelf)
        db.session.commit()
        title_df = pd.DataFrame(Books.query.with_entities(Books.title), columns=['title'])
        subject_df = pd.DataFrame(Books.query.with_entities(Books.subject), columns=['subject'])
        hours_df = pd.DataFrame(Books.query.with_entities(Books.hours), columns=['hours'])
        date_df = pd.DataFrame(Books.query.with_entities(Books.date), columns=['date'])
        user_df = pd.DataFrame(Books.query.with_entities(Books.input_user), columns=['input_user'])
        books_df = pd.concat([title_df, subject_df, hours_df, date_df, user_df], axis=1)
        books_df.to_csv('/Users/Evan/PycharmProjects/ReadingApp/ReadingApp/static/books.csv', index=False)
        flash(f"Book added successfully! {add_to_bookshelf.title}, is on your bookshelf", category='success')



        return redirect(url_for('input_page'))

    return render_template('input.html',form=form)

@app.route("/titles",methods=['GET'])
def titles_page():
    if request.method == "GET":
        df = pd.read_csv('/Users/Evan/PycharmProjects/ReadingApp/ReadingApp/static/books.csv')
        bookshelf_df = df.loc[df['input_user'] == current_user.id]
        fig = px.bar(bookshelf_df, x='title', y='hours', color ='subject', barmode ='group', title='Titles Read')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('titles.html', graphJSON=graphJSON)

@app.route("/hours",methods=['GET'])
def hours_page():
    if request.method == "GET":
        df = pd.read_csv('/Users/Evan/PycharmProjects/ReadingApp/ReadingApp/static/books.csv')
        bookshelf_df = df.loc[df['input_user'] == current_user.id]
        df = bookshelf_df.drop(['title','input_user', 'hours', 'subject'], axis=1)
        df1 = bookshelf_df.drop(['title','input_user', 'date', 'subject'], axis=1)
        df1 = df1.cumsum()
        df2 = pd.concat([df1, df], axis=1)
        fig = px.line(df2, x="date", y="hours", title='Hours Read')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('hours.html', graphJSON=graphJSON)

@app.route("/subjects",methods=['GET'])
def subjects_page():
    if request.method == "GET":
        df = pd.read_csv('/Users/Evan/PycharmProjects/ReadingApp/ReadingApp/static/books.csv')
        bookshelf_df = df.loc[df['input_user'] == current_user.id]
        fig = px.pie(bookshelf_df, values='hours', names='subject', title='Subjects Read')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('subjects.html', graphJSON=graphJSON)

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



