
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from pymongo import MongoClient
import os
import logging

app = Flask(__name__)
app.secret_key = 'This is a secret key for us!!'

client = MongoClient()
db = client.easyuni_db
users = db.users

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('dashboard.html')

@app.route('/logout')
def logout():
	if session.get('logged_in'):
		del session['logged_in']
		del session['fullname']
		del session['username']
		del session['password']
	return 'Logged out!'
 
@app.route('/login', methods=['POST'])
def login_applicant():
	user = users.find_one({'username': request.form['username']});
	if request.form['password'] == user['password']:
		session['logged_in'] = True
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
