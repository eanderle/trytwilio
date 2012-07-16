import os
import re
import sys
from twilio.rest import TwilioRestClient
from flask import Flask
from flask import request
from flask import render_template
from urllib import urlencode
from mongokit import Document, Connection

app = Flask(__name__)
client = TwilioRestClient()

mongoHost = re.match('.*@(.*):', os.environ.get('MONGOLAB_URI')).group(1)
mongoPort = int(re.match('.*@.*:(.*)/', os.environ.get('MONGOLAB_URI')).group(1))
connection = Connection(mongoHost, mongoPort)

@app.route('/', methods=['GET', 'POST'])
def hello():
	params=[]
	return render_template('index.html', params=params)

@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
	try:
		if request.method == 'GET':
			return request.values['twimlBody']
		
		if request.method == 'POST':
			toNumber = request.values['To']
			fromNumber = request.values['From']
			twimlBody = request.values['twimlBody']

			client.calls.create(to=toNumber, from_=fromNumber, 
				url='http://trytwilio.herokuapp.com/requestCall?' + urlencode({'twimlBody':twimlBody}),
				method='GET')
			return 'success'
	except:
		return 'failure'
		

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.debug = True
	app.run(host='0.0.0.0', port=port)