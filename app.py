import os
import requests as restRequests
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def hello():
	return 'Test'

@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
	if request.method == 'GET':
		return request.values['twimlBody']
	
	if request.method == 'POST':
		toNumber = request.values['To']
		fromNumber = request.values['From']
		twimlBody = request.values['twimlBody']
		
		params = {'To': toNumber, 'From': fromNumber,
				'url':'http://trytwilio.herokuapp.com/requestCall',
				'twimlBody': twimlBody}
		
		restRequests.post('http://api.twilio.com/2010-04-01/Accounts/ \
		ACefb267919ab7c793e889ce40b8db2506/Calls', params=params)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)

