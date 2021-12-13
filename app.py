from flask import Flask, request

import datetime

from flask.templating import render_template

import DBcm
import random
from collections import Counter

app = Flask(__name__)


@app.get("/")  # register the / URL with the Flask web server.
def home_page():
   return render_template("home.html", the_title = "Welcome to the word game!")

def currentGivenWord(given):
    givenWord = given
    return givenWord

@app.route("/play")
def play_page():
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
    global givenWord
    givenWord = (random.choice(givenWords.split()))
    
    return render_template("play.html", the_title = "Play Game", given_word = givenWord)

with open ("finalWords.txt") as fullList:
    wordList = fullList.read()
    ##print(wordList)

@app.route("/processwords")
def score_page():

    playerWords = request.args.get("words").split()

    duplicateCounter = 0 ##Counter used for checking duplicates
    wordCounter = 0 ##Counter used for counting how many words are input

    for word in playerWords:
        wordCounter = wordCounter + 1
        if word.lower() not in wordList: ##Check if word exists in full word list
            print("Not a real word!")
            wordExist = "One or more words does not exist"
        if word.lower() == givenWord: ##Check if input word is not the same as given word
            print("Player input the given word!")
            wordExist = "Player has input the given word"
        if len(word) < 4 : ##Check if word is longer than 3 characters
            print ("One or more words are shorter than 4 characters!")
            wordExist = "Player has input the given word"
            
            
    ##Check if player input 7 words
    if wordCounter > 7:  
        print("Too many words input")
    if wordCounter < 7:
        print("Not enough words input")
    else:     
        for word in playerWords:
            for secondWord in playerWords:
                if word.lower() == secondWord.lower(): ##Check if duplicates exist, if counter is more than 7 then duplicates exist
                    duplicateCounter = duplicateCounter + 1

        if duplicateCounter > 7:
            print("Duplicate Words detected! : ", playerWords) 
        
        print(duplicateCounter)

        
    lettersInGiven = Counter(givenWord) ##Count letters in given word
    print(lettersInGiven)
    for word in playerWords:
        lettersInPlayer = Counter(word.lower()) ##Count letters in each user word
        print("Player", lettersInPlayer)
        for i in lettersInPlayer:
            if(lettersInPlayer[i] <= lettersInGiven[i]):
                print("Word is valid")
                wordExist = "Word is valid"
            else:
                print("Word is not valid")
                wordExist = "One or more words not valid"
                break

    return render_template("processwords.html", the_title = "Check Words", given_word = givenWord , input_words = playerWords , validity = wordExist )

@app.route("/top10")
def leaderboard_page():
    return render_template("top10.html", the_title = "Highscores")

@app.route("/log")
def log_page():
    return render_template("log.html", the_title = "Log")



if __name__ == "__main__":
    app.run(debug=True)