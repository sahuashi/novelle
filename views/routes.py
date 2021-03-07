from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app
from flask_login import login_required, logout_user, login_user, current_user
from sqlalchemy import exc
import os, sys, requests

router = Blueprint('route', __name__)

# amend path to prevent circular imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


# no home page atm, redirects to search page
@router.route("/")
def index():
    return redirect(url_for('route.search'))


# allow user to search query
@router.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        q = request.form["query"]
        return redirect(url_for('route.retrieve', query=q))
    else:
        return render_template('search.html')


# retrieve book results from Google Books API
@router.route("/search/<query>")
def retrieve(query):
    api_key = os.environ.get('BOOKS_API_KEY')
    search_query = query
    # build url for api request
    search_url = f'https://www.googleapis.com/books/v1/volumes?q={search_query}&projection=full&maxResults=15&key={api_key}'
    # send request to api
    resp = requests.get(search_url)
    # save relevant book info from api response
    responses = resp.json()['items']
    books = []
    from models import Book
    from main import db
    # add retrieved books to search results list
    for book in responses:
        book_info = {
            'id': book['id'],
            'title': book['volumeInfo']['title'] if 'title' in book['volumeInfo'] else 'No title available.',
            'subtitle': book['volumeInfo']['subtitle'] if 'subtitle' in book['volumeInfo'] else '',
            'desc': book['volumeInfo']['description'] if 'description' in book[
                'volumeInfo'] else 'No description available.',
            'author': book['volumeInfo']['authors'][0] if 'authors' in book['volumeInfo'] else 'No authors available.',
            'date': book['volumeInfo']['publishedDate'] if 'publishedDate' in book[
                'volumeInfo'] else 'No published date available.',
            'publisher': book['volumeInfo']['publisher'] if 'publisher' in book[
                'volumeInfo'] else ' No publisher available.',
            'thumbnail': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book[
                'volumeInfo'] else 'https://islandpress.org/sites/default/files/default_book_cover_2015.jpg',
            'pages': book['volumeInfo']['pageCount'] if 'pageCount' in book[
                'volumeInfo'] else 'No page count available.',
            'rating': f"{book['volumeInfo']['averageRating']}/5 based on {book['volumeInfo']['ratingsCount']} review(s)"
            if 'averageRating' in book['volumeInfo'] else 'No rating available.',
            'infoLink': book['volumeInfo']['infoLink'] if 'infoLink' in book['volumeInfo'] else ' '
        }
        # add current book to list of books
        books.append(book_info)
        # add current book to book db table
        try:
            book = Book(id=book_info.get('id'),
                        title=book_info.get('title'),
                        subtitle=book_info.get('subtitle'),
                        thumbnail=book_info.get('thumbnail'),
                        googlebooks=book_info.get('infoLink')
                        )
            db.session.add(book)
            db.session.flush()
        # if current book info already in db, abort
        except exc.SQLAlchemyError:
            db.session.rollback()
        # save updated db
        else:
            db.session.commit()
    return render_template('results.html', books=books, query=query)


# allow user to login to view and edit list
@router.route("/login", methods=['GET', 'POST'])
def login():
    from forms import Form
    from models import User
    form = Form()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                flash(f'Welcome back, {current_user.username}!')
                return redirect(url_for('route.list'))
        # return to login page to try again
        flash('Invalid username/password. Please try again.')
        return redirect(url_for('route.login'))
    return render_template('login.html', form=form)


# allow user to create account
@router.route("/register", methods=['GET', 'POST'])
def register():
    from models import User
    from main import db
    from forms import Form
    form = Form()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        try:
            db.session.add(user)
            db.session.flush()
        except exc.SQLAlchemyError:
            db.session.rollback()
            flash('Username already taken! Please try again.')
            return redirect(url_for('route.register'))
        else:
            db.session.commit()
            flash('Account created! Please login to continue.')
            return redirect(url_for('route.login'))

    return render_template('register.html', form=form)


# protected route: allow user to logout
@router.route("/logout")
@login_required
def logout():
    flash(f'You were successfully logged out, {current_user.username}!')
    logout_user()
    return redirect(url_for('route.index'))


# display user's reading list
@router.route("/mylist")
def list():
    if current_user.is_authenticated:
        return render_template('list.html', user=current_user)
    else:
        flash('You must login to see your reading list.')
        return redirect(url_for('route.login'))


# add book to user's reading list
@router.route("/save", methods=['POST', 'GET'])
def save():
    if current_user.is_authenticated:
        if request.method == "POST":
            from models import User, Book
            from main import db
            bookid = request.form['bookid']
            book = Book.query.filter_by(id=bookid).first()
            user = current_user
            user.list.append(book)
            db.session.commit()
            return redirect(url_for('route.list'))
    else:
        flash('You must login to save to your reading list.')
        return redirect(url_for('route.login'))


@router.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')
