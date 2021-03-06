from flask import Flask, request, session

import datetime
import time
from flask.templating import render_template

import DBcm
import random
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'IDK anymore I guess, good luck man'

config = {
    'host' : '127.0.0.1',
    'database': 'highscoreDB',
    'user' : 'highscoreuser',
    'password' : 'pathfinder',
}



@app.get("/")  # register the / URL with the Flask web server.
def home_page():
   return render_template("home.html", the_title = "Welcome to the word game!")

@app.route("/play")
def play_page():
    ##global startTime
    startTime = datetime.datetime.now()
    session["startTime"] = startTime

    with open("small.txt" , "w") as sf:
        with open("big.txt" , "w") as bf:
            with open("words.txt") as wf:
              with open ("finalwords.txt" , "w") as ff:
                 for w in wf:
                     if "'s" not in w: 
                        print(w.lower().strip(),file = ff)
                       
                        if len(w) > 7: 
                            print(w.lower().strip(),file = bf)
                        else:
                            print(w.lower().strip(),file = sf)

    with open ("big.txt") as bigWordsList:
        givenWords = bigWordsList.read()
        #print(givenWords)
    givenWord = (random.choice(givenWords.split()))
    session["givenWord"] = givenWord
    
    
    return render_template("play.html", the_title = "Play Game", given_word = givenWord)

with open ("finalWords.txt") as fullList:
    wordList = fullList.read()
    ##print(wordList)

@app.route("/processwords")
def score_page():

    startTime = session["startTime"]
    givenWord = session.get("givenWord")


    playerWords = request.args.get("words").split()
    session["playerWords"] = playerWords
    
    ##global endTime
    endTime = datetime.datetime.now()
    endTime = endTime.timestamp() - startTime.timestamp()
    session["endTime"] = endTime

    duplicateCounter = 0 ##Counter used for checking duplicates
    wordCounter = 0 ##Counter used for counting how many words are input
    valid = True
    session["valid"] = valid
    sevenWords = True
    acceptedWords = True

    for word in playerWords:
        wordCounter = wordCounter + 1
        if word.lower() not in wordList: ##Check if word exists in full word list
            print("Not a real word!")
            outputMessage = "One or more words does not exist"
            acceptedWords = False
            sevenWords = False
        if word.lower() == givenWord: ##Check if input word is not the same as given word
            print("Player input the given word!")
            outputMessage = "Player has input the given word"
            acceptedWords = False
            sevenWords = False
        if len(word) < 4 : ##Check if word is longer than 3 characters
            print ("One or more words are shorter than 4 characters!")
            outputMessage = "One or more words are shorter than 4 characters!"
            acceptedWords = False
            sevenWords = False
            

           
    ##Check if player input 7 words
    if acceptedWords == True:
        if wordCounter > 7:  
            print("Too many words input")
            outputMessage = "Too many words input"
            sevenWords = False
        if wordCounter < 7:
            print("Not enough words input")
            outputMessage = "Not enough words input"
            sevenWords = False
        else:     
            for word in playerWords:
                for secondWord in playerWords:
                    if word.lower() == secondWord.lower(): ##Check if duplicates exist, if counter is more than 7 then duplicates exist
                        duplicateCounter = duplicateCounter + 1

            if duplicateCounter > 7:
                print("Duplicate Words detected! : ", playerWords) 
                outputMessage = "Duplicate Words detected!"
                sevenWords = False

    
    ##givenWord = session.get("givenWord")
    lettersInGiven = Counter(givenWord) ##Count letters in given word
    print(lettersInGiven)

    if sevenWords == True:
        for word in playerWords:
            lettersInPlayer = Counter(word.lower()) ##Count letters in each user word
            print("Player", lettersInPlayer)
            for i in lettersInPlayer:
                if(lettersInPlayer[i] <= lettersInGiven[i]):
                    print("Word is valid")
                    outputMessage = "Word is valid"
                else:
                    print("Word is not valid")
                    valid = False
                    session["valid"] = valid
                    break
                   
    playerBrowser = request.user_agent.string
    playerIP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    converted = " ".join(playerWords)

    session["DataSave"] = False

    if valid == False or sevenWords == False:
        outputMessage = "One or more words not valid" 
        status = "LOST"
        save_logs(status, givenWord, converted, playerBrowser, playerIP)
        return render_template("gameLost.html", the_title = "YOU LOSE", given_word = givenWord , input_words = playerWords , validity = outputMessage)
    else:
        status = "WON" 
        save_logs(status, givenWord, converted, playerBrowser, playerIP)
        return render_template("processwords.html", the_title = "YOU WIN", given_word = givenWord , input_words = playerWords ,
         validity = outputMessage, time_score = endTime, date_joined = datetime.datetime.now())

@app.route("/top10")
def leaderboard_page():
    givenWord = session.get("givenWord")
    endTime = session.get("endTime")
    playerWords = session.get("playerWords")

    username = request.args.get("username")
    playerBrowser = request.user_agent.string
    playerIP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    converted = " ".join(playerWords)
    print(username)
    print(playerBrowser)
    print(playerIP)
    print(converted)


    if session.get("DataSave") == False and session.get("valid") == True:
        save_data(username, givenWord, converted, endTime)
        session["DataSave"] = True



    data = process_data()

    return render_template("top10.html", the_title = "Highscores", table = data)

@app.route("/log")
def log_page():

    logs = process_logs()
    return render_template("log.html", the_title = "Log", table = logs)

def save_data(username, givenWord, converted, endTime):
    with DBcm.UseDatabase(config) as db:
        SQL = """insert into players(username, word, wordsinput, time_score) values (%s,%s,%s,%s) """
        db.execute(SQL,(username, givenWord, converted, endTime))

        data = db.fetchall()
    return data

def save_logs(status, givenWord, converted, browser, ip):
    with DBcm.UseDatabase(config) as db:
        SQL = """insert into playerlogs(status, word, wordsinput, player_browser, player_ip) values (%s,%s,%s,%s,%s) """
        db.execute(SQL,(status, givenWord, converted, browser, ip))

        logs = db.fetchall()
    return logs


def process_data():
    with DBcm.UseDatabase(config) as db:
        SQL = """select * from players order by time_score"""
        db.execute(SQL)
        scores =[]
        scores = db.fetchall()

    non_null = lambda x:"*"

    for row in SQL:
        mylist = map(non_null, row)

        next = tuple(mylist)
        scores.append(next)

    return scores[:10]

def process_logs():
    with DBcm.UseDatabase(config) as db:
        SQL = """select * from playerlogs order by date_played desc"""
        db.execute(SQL)
        logs =[]
        logs = db.fetchall()

    return logs


if __name__ == "__main__":
    app.run(debug=True)