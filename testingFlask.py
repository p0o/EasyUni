from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
client = MongoClient('localhost', 27017) #setting up with localhost

db = client.easyUniDB #connecting to my database

collection = db.qualifications  #connecting to my collection


@app.route("/")
def index():
    return "here we go!"

@app.route("/setupQual", methods = ['GET'])
def setupQual():
    qualifications = db.qualifications.find()
    return render_template('setupQualification.html', qualifications=qualifications)

@app.route("/setupQual", methods = ['POST'])
def addQualification():

    qualName = request.form['qualName']
    calc = request.form['calculation']
    minScore = request.form['minScore']
    maxScore = request.form['maxScore']

    addToDB = {
            "qualificationName": qualName,
            "calculation": calc,
            "minimumScore": minScore,
            "maximumScore": maxScore
        }
    db.qualifications.insert_one(addToDB)
    return redirect(url_for('setupQual'))

if __name__ == "__main__":
    app.run(debug=True)

