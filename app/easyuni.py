
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)
app.secret_key = 'This is a secret key for us!!'
 
@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return "Welcome to your applicant dashboard"
 
@app.route('/login', methods=['POST'])
def do_applicant_login():
	if request.form['password'] == 'password' and request.form['username'] == 'admin':
		session['logged_in'] = True
	else:
		flash('wrong password!')
	return home()


