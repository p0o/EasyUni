

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

import logging
import bson
import time
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

	for programme in university['programs']:
		logging.warning('hhhh=>' + str(programme['programmeId']))
		if (str(programme['programmeId']) == str(programmeId)):
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
		return redirect(url_for('login_applicant'))
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
		return redirect(url_for('recordProgramme'))
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

@app.route("/admin/registerUni/addUni", methods = ['POST'])   #addding  to db from modal
def registerUniversity():
	getUniName = request.form['uniName']

	addToDB = {
            "uniName": getUniName
        }
	db.universities.insert_one(addToDB)
	return redirect(url_for('registerUni'))

@app.route("/admin/registerUni/addUniAdmin", methods = ['POST'])   #addding  to db from modal
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

@app.route("/admin/reviewApps")
def reviewApps():
	uniName = session.get('uniNameForAdmin')
	programs = db.universities.find_one({"uniName": uniName})["programs"]

	for program in programs:
		apps = list(db.universities.application.find({"programmeId": str(program['programmeId'])}))
		logging.warning('this V')
		logging.warning(apps)
		program["appsNum"] = 0
		if apps:
			program["appsNum"] = len(apps)
		program["apps"] = apps;
	return render_template('reviewApps.html', programs=programs)

#addProgramme.html
@app.route("/admin/recordProgramme") #loading programmes from db
def recordProgramme():
	uniName = session.get('uniNameForAdmin')
	uniItself = db.universities.find_one({"uniName": uniName})
	return render_template('addProgramme.html', uni=uniItself)

@app.route("/admin/recordProgramme/addProgram", methods = ['POST'])   #addding Program for University to db from modal
def addProgramme():
	uniName = session.get('uniNameForAdmin')
	foundUni = {"uniName": uniName}
	uniItself = db.universities.find_one = (foundUni)

	programName = request.form['progName']
	programDescription = request.form['progDescription']
	programDate = request.form['closingDate']

	addToDB = {
		"$push":
			{"programs":
				{
				    "programmeId": time.time(),
					"programName": programName,
					"programDescription": programDescription,
					"closingDate": programDate,
				}

			}
	}

	db.universities.update(uniItself, addToDB)
	return redirect(url_for('recordProgramme'))


# only to create sample data in database
# to support use cases that are not covered yet
@app.route('/init')
def addSampleData():
	db.universities.insert_one({
		'uniName': 'Help University',
		'uniAdmins': [{'name': 'The Uni Admin', 'email': 'uniadmin@easyuni.com', 'username': 'myuniadmin', 'password': 'myuniadmin'}],
	
	});
	
	return 'Sample collections created!'

if __name__ == '__main__':
	app.run(debug=True)