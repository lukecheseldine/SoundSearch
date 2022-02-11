from crypt import methods
from flask import Flask, render_template, redirect
import config

app = Flask(__name__)
app.config.from_object("config")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/landing", methods=["GET", "POST"])
def landing():
    return render_template("landing.html")


@app.route("/login")
def login():
    return "Log in"


@app.route("/register")
def register():
    return "Register"


@app.route('/authorize', methods=['POST'])
def authorize():
    url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={SPOTIFY_SCOPES}'
    return redirect(url)


@app.route('/callback', methods=['GET'])
def callback():
    return f"{request.text}"