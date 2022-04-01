import email
from email.policy import default
from flask import Flask, render_template, redirect, request, session, url_for, abort, flash 
import config
from forms import RegistrationForm, LoginForm
from requests import get, post
from base64 import urlsafe_b64encode
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from is_safe_url import is_safe_url
from pprint import pprint
import calendar



app = Flask(__name__)
app.config.from_object("config")


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    linked = db.Column(db.Boolean, default=False, nullable=False)
    spotify_refresh_token = db.Column(db.String(), default=None)
    zipcode = db.Column(db.Integer(), default=90210)

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/landing", methods=["GET"])
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        form = LoginForm()
        return render_template('login.html', form=form)
    else:
        form = LoginForm(request.form)
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()

            # check user validity
            if not user or not bcrypt.check_password_hash(user.password, form.password.data):
                form.email.errors.append('Incorrect email or password')
                return render_template('login.html', form=form)

            if user.linked:
                user.linked = 0
                db.session.commit()
            login_user(user)
            
            next = request.args.get('next')
            # TODO: figure out how to implement this...
            # if not is_safe_url(next, {"localhost"}):
            #     return abort(400)
            flash("Login successful!", "success")
            return redirect(next or url_for('home'))


@app.route("/logout")
@login_required
def logout():
    current_user.linked = 0
    db.session.commit()
    logout_user()
    flash("Log out successful!", "success")
    return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        form = RegistrationForm()
        return render_template('register.html', form=form)
    else:
        form = RegistrationForm(request.form)
        if form.validate():
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(email=form.email.data, password=hashed_pass)
            # check that email isn't already taken
            if User.query.filter_by(email=form.email.data).first():
                form.email.errors.append('This email is already taken')
                return render_template('register.html', form=form)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Registration successful! You are now logged in.", "success")
            return redirect(url_for('home'))
        else:
            print(f'{form.errors}')
            return render_template('register.html', form=form)


@app.route("/home")
@login_required
def home():
    if current_user.linked:
        url = 'https://api.spotify.com/v1/me'
        headers = {'Authorization' : f'Bearer {session.get("spotify_access_token")}'}
        response = get(url=url, headers=headers).json()
        return render_template('home.html', name=response['display_name'])
    else:
        return render_template('home.html')


@app.route("/followed_artists")
@login_required
def followed_artists():

    if not current_user.linked:
        flash('Please link your Spotify first', 'danger')
        return redirect(url_for('home'))
    
    # get followed artists
    url = 'https://api.spotify.com/v1/me/following'
    params = {
        'type': 'artist',
    }
    headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {session.get("spotify_access_token")}',
            'Content-Type': 'application/json'
        }
    response = get(url=url, headers=headers, params=params).json()
    artists = response['artists']['items']
    
    return render_template('home.html', current_user=current_user, artists=artists)
    


@app.route('/recommendations/artist/<string:artist>/<int:zipcode>')
def get_artist_recommendations(artist, zipcode):

    url = 'https://api.seatgeek.com/2/performers'
    params = {
        'q': artist,
        'client_id': app.config['SEATGEEK_CLIENT_ID']
    }
    response = get(url, params=params).json()

    performer_id = None
    for performer in response['performers']:
        if performer['name'].lower() == artist.lower():
            performer_id = str(performer['id'])
    
    if not performer_id:
        return "Recommendations not available"
    
    url = 'https://api.seatgeek.com/2/recommendations'
    params = {
        'performers.id': performer_id,
        'postal_code': str(zipcode),
        'client_id': app.config['SEATGEEK_CLIENT_ID']
    }
    response = get(url, params=params).json()

    recommendations = []
    for event in response['recommendations']:
        event = event['event']
        
        performers = []
        for performer in event['performers']:
            # api can have repeats sometimes, filter these out
            if performer['name'] not in performers:
                performers.append(performer['name'])
        
        image = None
        if event['performers'][0]['images']:
            image = event['performers'][0]['images']['huge']

        year = event['datetime_local'][:4]
        month = calendar.month_name[int(event['datetime_local'][5:7])]
        day = event['datetime_local'][8:10]
        date = f'{month} {day}, {year}'

        performance = {
            'performers': performers,
            'date': date,
            'venue': event['venue']['name'],
            'image': image,
            'url': event['url']
        }
        recommendations.append(performance)
        
    return render_template('recommendations.html', seed=artist, recommendations=recommendations)


@app.route("/authorize", methods=["POST", "GET"])
def authorize():
    client_id = app.config["SPOTIFY_CLIENT_ID"]
    redirect_uri = app.config["SPOTIFY_REDIRECT_URI"]
    scopes = app.config["SPOTIFY_SCOPES"]
    url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}'
    return redirect(url)


@app.route('/callback', methods=['GET'])
def callback():
    # TODO: what happens when the user doesn't end up logging into spotify page?
    # TODO: refresh access token
    if request.args.get('error'):
        return 'error'
    else:
        client_id = app.config["SPOTIFY_CLIENT_ID"]
        secret = app.config["SPOTIFY_CLIENT_SECRET"]
        code = request.args.get("code")
        redirect_uri = app.config["SPOTIFY_REDIRECT_URI"]
        url = f'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + (urlsafe_b64encode(str.encode(client_id + ':' + secret)).decode()),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = post(url, headers=headers, data=data)
        response_data = response.json()
        access_token = response_data['access_token']

        current_user.linked = 1
        db.session.commit()

        session['spotify_access_token'] = access_token

        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)