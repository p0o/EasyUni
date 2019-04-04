

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

import logging
import bson
from bson.son import SON

app = Flask(__name__)
app.secret_key = 'This is a secret key for us!!'

client = MongoClient()
db = client.easyuni_db
#collections
users = db.users
admins = db.admins
universities = db.universities

@app.route('/')
def home():
	return render_template('select_programme.html', unis=universities.find())

#pooriya
@app.route('/logout')
def logout():
	if session.get('logged_in'):
		session['logged_in'] = False
		session['fullname'] = None
		session['username'] = None
		session['password'] = None
	return redirect(url_for('home'));


@app.route('/login', methods=['POST', 'GET'])
def login_applicant():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		try :
			user = users.find_one({'username': request.form['username']});
			if request.form['password'] == user['password']:
				session['logged_in'] = True
				session['fullname'] = user['fullname']
				session['username'] = user['username']
				return redirect(url_for('home'))
		except:
			return redirect(url_for('login_applicant'))

@app.route('/programme')
def show_programme():
	programmeId = request.args.get('id')
	universityId = request.args.get('universityId')
	university = universities.find_one({'_id': bson.objectid.ObjectId(universityId)})
	myProgramme = {}

	for programme in university['programmes']:
		if (programme['_id'] == bson.objectid.ObjectId(programmeId)):
			myProgramme = programme
	return render_template('programme.html', programme=myProgramme, university=university)
	
@app.route('/apply')
def apply():
	programmeId = request.args.get('id')
	universityId = request.args.get('universityId')
	if session.get('logged_in') :
		university = universities.find_one({'_id': bson.objectid.ObjectId(universityId)})
		universities.application.insert_one({
			'applicantId': session['username'],
			'programmeId': programmeId
		})
		return 'Successfully applied'
	else :
		return redirect(url_for('login_applicant'))

@app.route('/signup', methods=['POST', 'GET'])
def signup_applicant():
	if request.method == 'POST':
		logging.warning('here' + str(session['signup_step']))
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
			session['logged_in'] = True
			return redirect(url_for('home'));
	if request.method == 'GET':
		session['signup_step'] = 1
		return render_template('signup_step1.html')

#Rasul
@app.route('/admin/logoutAdmin', methods=['POST', 'GET'])
def adminLogout(): #Check if admin is logged in
	if session.get('admin_logged_in') or session.get('uniAdmin_logged_in'):
		session['admin_logged_in'] = False
		session['adminLoginError'] = False
		session['uniAdmin_logged_in'] = False
		return redirect(url_for('adminHome'))

#login for admin part1
@app.route('/admin', methods=['POST', 'GET'])
def adminHome():#this is needed for handling error
	if session.get('admin_logged_in'):
		return redirect(url_for('setupQual'))
	elif session.get('uniAdmin_logged_in'):
		return redirect(url_for('addProgramme'))
	else:
		if session.get('adminLoginError'): #if admin entered wrong credentials
			error = "Invalid credentials, try again!"
			return render_template('loginAdmin.html', error=error)
		else:
			return render_template('loginAdmin.html') #if first time

#login for admin part2
@app.route('/admin/login', methods=['POST', 'GET'])
def login_admin():

	if request.form['adminRBtn'] == "adminRadio": #if admin radio is selected(not uniAdmin)
		theAdmin = admins.find_one({
			'username': request.form['adminUsername'],
			'password': request.form['adminPassword']
		});
		if theAdmin != None:
			session['admin_logged_in'] = True
			return redirect(url_for('adminHome'))
		else:
			session['adminLoginError'] = True
			return redirect(url_for('adminHome'))
	else:#find(match) uniAdmin from universities db
		uni = universities.find_one({
			"uniAdmins": {"$elemMatch": {
					'username': request.form['adminUsername'],
					'password': request.form['adminPassword']
			}}
		})
		if uni != None:
			session['uniAdmin_logged_in'] = True
			session['uniNameForAdmin'] = uni["uniName"] #storing name of uni to display
			uniAdminList = uni["uniAdmins"]
			uniAdminName = ""
			uniAdminEmail = ""
			uniAdminUsername = ""
			for uniAdmin in uniAdminList:
				if uniAdmin["username"] == request.form['adminUsername']:
					uniAdminName = uniAdmin["name"]
					uniAdminEmail = uniAdmin["email"]
					uniAdminUsername = uniAdmin["username"]
			session['adminNameForAdmin'] = uniAdminName #storing name of admin
			session['adminEmailForAdmin'] = uniAdminEmail  # storing name of admin
			session['adminUsernameForAdmin'] = uniAdminUsername  # storing name of admin
			return redirect(url_for('adminHome'))
		else:
			session['adminLoginError'] = True
			return redirect(url_for('adminHome'))

#addProgramme.html
@app.route("/admin/addProgramme") #loading from db for adding
def addProgramme():
    return render_template('addProgramme.html')


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


#RegisterUniverisity.html
@app.route("/admin/registerUni") #loading from db for adding
def registerUni():
	universities = db.universities.find()
	return render_template('registerUni.html', universities=universities)

@app.route("/admin/registerUni/addUni", methods = ['POST'])   #addding Qualification to db from modal
def registerUniversity():
	getUniName = request.form['uniName']

	addToDB = {
            "uniName": getUniName
        }
	db.universities.insert_one(addToDB)
	return redirect(url_for('registerUni'))

@app.route("/admin/registerUni/addUniAdmin", methods = ['POST'])   #addding Qualification to db from modal
def addUniAdmin():
	addUniAdminBtn = request.form['uniId']
	foundUni = {"_id": ObjectId(addUniAdminBtn)}
	addUniAdminId = db.universities.find_one = (foundUni)

	getAdminName = request.form['name']
	getAdminUsername = request.form['username']
	getAdminEmail = request.form['email']
	getAdminPassword = request.form['password']

	addToDB = {
		"$push":
			{"uniAdmins":
				{
					"name": getAdminName,
					"email": getAdminEmail,
					"username": getAdminUsername,
					"password": getAdminPassword
				}

			}
	}

	db.universities.update(addUniAdminId, addToDB)
	return redirect(url_for('registerUni'))


# only to create sample data in database
# to support use cases that are not covered yet
@app.route('/init')
def addSampleData():
	db.universities.insert_one({
		'universityName': 'Help University',
		'uniAdmins': [],
		'programmes': [
			{
				'_id': bson.objectid.ObjectId(),
				'programmeName': 'Bachelor of IT',
				'description': 'Bachelor of IT is a great academic opportunity for students interested in computer science and career opportunities in programming and e-commerce.',
				'closingDate': '12/03/2020'
			},
			{
				'_id': bson.objectid.ObjectId(),
				'programmeName': 'Bachelor of Business',
				'description': 'Bachelor of Business is a great academic opportunity for students interested in learning business and career opportunities in executive positions and office admin.',
				'closingDate': '12/05/2020'
			},
			{
				'_id': bson.objectid.ObjectId(),
				'programmeName': 'Bachelor of Marketing',
				'description': 'Bachelor of Marketing is a great academic opportunity for students interested in markets, selling products and career opportunities in marketing and e-commerce.',
				'closingDate': '12/01/2020'
			},
		]
	});
	db.universities.insert_one({
		'universityName': 'Taylor University',
		'uniAdmins': [],
		'programmes': [
			{
				'_id': bson.objectid.ObjectId(),
				'programmeName': 'Bachelor of Business',
				'description': 'Bachelor of Business is a great academic opportunity for students interested in learning business and career opportunities in executive positions and office admin.',
				'closingDate': '04/06/2020'
			},
			{
				'_id': bson.objectid.ObjectId(),
				'programmeName': 'Bachelor of Marketing',
				'description': 'Bachelor of Marketing is a great academic opportunity for students interested in markets, selling products and career opportunities in marketing and e-commerce.',
				'closingDate': '04/02/2020'
			},
		]
	});
	return 'Sample collections created!'

if __name__ == '__main__':
	app.run(debug=True)