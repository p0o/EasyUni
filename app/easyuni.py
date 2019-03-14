

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

import logging

app = Flask(__name__)
app.secret_key = 'This is a secret key for us!!'

client = MongoClient()
db = client.easyuni_db
#collections
users = db.users
qualifications = db.qualifications
admins = db.admins

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('dashboard.html')

#pooriya
@app.route('/logout')
def logout():
	if session.get('logged_in'):
		session['logged_in'] = False
		session['fullname'] = None
		session['username'] = None
		session['password'] = None
	return 'Logged out!'

@app.route('/login', methods=['POST'])
def login_applicant():
	try :
		user = users.find_one({'username': request.form['username']});
		if request.form['password'] == user['password']:
			session['logged_in'] = True
			session['fullname'] = user['fullname']
			return redirect(url_for('home'))
	except:
		return redirect(url_for('home'))



@app.route('/signup', methods=['POST', 'GET'])
def signup_applicant():
	if request.method == 'POST':
		logging.warning('herer' + str(session['signup_step']))
		if session['signup_step'] == 1:
			# put all the fields data in session
			session['username'] = request.form['username'];
			session['password'] = request.form['password'];
			session['fullname'] = request.form['fullname'];
			session['signup_step'] = 2
			return render_template('signup_step2.html')
		if session['signup_step'] == 2:
			users.insert_one({
				'username': session['username'],
				'password': session['password'],
				'fullname': session['fullname'],
				'email':  request.form['email'],
				'idType': request.form['idtype'],
				'idNo': request.form['idno'],
				'mobileNo': request.form['mobileno'],
				'dateOfBirth': request.form['date_of_birth']	
			});
			return redirect(url_for('home'));
	if request.method == 'GET':
		session['signup_step'] = 1
		return render_template('signup_step1.html')


#Rasul
@app.route('/admin/logoutAdmin')
def adminLogout():
	if session.get('admin_logged_in'):
		session['admin_logged_in'] = False
		session['adminLoginError'] = False
		return redirect(url_for('adminHome'))


#setupQualification.html
@app.route("/admin/setupQual") #loading from db for adding
def setupQual():
    qualifications = db.qualifications.find()
    return render_template('setupQualification.html', qualifications=qualifications)

@app.route("/admin/setupQual/update" , methods = ['POST']) #Updating Qualification after "save" button
def loadQualToUpdate():
    updateBtnId = request.form['id']
    foundQual = {"_id": ObjectId(updateBtnId)}
    updateQualifications = db.qualifications.find_one=(foundQual)

    qualName = request.form['qualNameUpdate']
    calc = request.form['calculationUpdate']
    minScore = request.form['minScoreUpdate']
    maxScore = request.form['maxScoreUpdate']

    updateDB = {
        "$set": {
            "qualificationName": qualName,
            "calculation": calc,
            "minimumScore": minScore,
            "maximumScore": maxScore
        }
    }
    db.qualifications.update(updateQualifications, updateDB)
    return redirect(url_for('setupQual'))

@app.route("/admin/setupQual/add", methods = ['POST'])   #addding Qualification to db from modal
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

#login for admin
@app.route('/admin')
def adminHome():
	if session.get('admin_logged_in'):
		return redirect(url_for('setupQual'))
	else:
		if session.get('adminLoginError'):
			error = "Invalid credentials, try again!"
			return render_template('loginAdmin.html', error=error)
		else:
			return render_template('loginAdmin.html')

@app.route('/admin/login', methods=['POST'])
def login_admin():
	try:
		theAdmin = admins.find_one({'username': request.form['adminUsername']});
		if request.form['adminPassword'] == theAdmin['password']:
			session['admin_logged_in'] = True
			return redirect(url_for('adminHome'))
		else:
			session['adminLoginError'] = True
			return redirect(url_for('adminHome'))

	except:
		session['adminLoginError'] = True
		return redirect(url_for('adminHome'))

#RegisterUniverisity.html
"""@app.route("/registerUni") #loading from db for adding
def registerUni():
    university = db.universities.find()
    return render_template('registerUniversity.html', university=university)

@app.route("/setupQual/add", methods = ['POST'])   #addding Qualification to db from modal
def addUniversity():

    uniName = request.form['qualName']
    numOfAdmins = 0
    uniAdmins = 0

    addToDB = {
            "qualificationName": qualName,
        }
    db.qualifications.insert_one(addToDB)
    return redirect(url_for('setupQual'))
"""