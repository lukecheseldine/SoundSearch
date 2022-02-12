from crypt import methods
from flask import Flask, render_template, redirect, request
import config
from forms import RegistrationForm, LoginForm
from requests import get, post
from base64 import urlsafe_b64encode

app = Flask(__name__)
app.config.from_object("config")


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
        return "POST"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        form = RegistrationForm()
        return render_template('register.html', form=form)
    else:
        return "POST"

@app.route("/home")
def home():
    return render_template("home.html")


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
        return redirect('/home')