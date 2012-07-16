import os
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from urllib import urlencode
from twilio import twiml
from twilio.util import TwilioCapability
from twilio.rest import TwilioRestClient

app = Flask(__name__)
client = TwilioRestClient()

@app.route('/', methods=['GET', 'POST'])
def hello():
  params=[]
  return render_template('index.html', params=params)

@app.route('/test', methods=['GET', 'POST'])
def xmlcheck():
  return render_template('test.html')

@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
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
		
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
