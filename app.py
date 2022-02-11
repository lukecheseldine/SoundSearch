from crypt import methods
from flask import Flask, render_template, redirect, request
import config
from forms import RegistrationForm, LoginForm

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


@app.route('/authorize', methods=['POST'])
def authorize():
    url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={SPOTIFY_SCOPES}'
    return redirect(url)


@app.route('/callback', methods=['GET'])
def callback():
    return f"{request.text}"