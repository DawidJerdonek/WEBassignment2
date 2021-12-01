from flask import Flask, request

import datetime

from flask.templating import render_template

app = Flask(__name__)

@app.get("/")  # register the / URL with the Flask web server.
def home_page():
   return render_template("home.html", the_title = "Welcome to the word game!")

@app.route("/play")
def aboutme_page():
    return render_template("play.html", the_title = "Play Game")

@app.route("/top10")
def cv_page():
    return render_template("top10.html", the_title = "Highscores")

@app.route("/log")
def favgames_page():
    return render_template("log.html", the_title = "Log")



if __name__ == "__main__":
    app.run(debug=True)