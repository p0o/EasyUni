
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from pymongo import MongoClient
import os
import logging
import bson

app = Flask(__name__)
app.secret_key = 'This is a secret key for us!!'

client = MongoClient()
db = client.easyuni_db
users = db.users
universities = db.universities

@app.route('/')
def home():
	return render_template('select_programme.html', unis=universities.find())

@app.route('/logout')
def logout():
	if session.get('logged_in'):
		session['logged_in'] = False
		session['fullname'] = None
		session['username'] = None
		session['password'] = None
	return 'Logged out!'

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