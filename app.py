import os
from flask import Flask
from twilio.rest import TwilioRestClient
from twilio import twiml

os.environ['TWILIO_ACCOUNT_SID'] = "ACefb267919ab7c793e889ce40b8db2506"
os.environ["TWILIO_AUTH_TOKEN"] = "6cb0a97591eaf94ca237572fe4472458"

#client = TwilioRestClient()

app = Flask(__name__)

@app.route('/')
def hello():
	return 'Test'


@app.route('/calls/say')
def sayTest():
	#call = client.calls.create(to="7033891424",
	#			   from_="7862458451",
	#			   url= "http://trytwilio.herokuapp.com/calls/saytwiml")
	client = TwilioRestClient()
	call = client.calls.create(to="7033891424",
				   from_="7862458451",
				   url="http://trytwilio.herokuapp.com/calls/saytwiml")
	return 'test'

@app.route('/calls/saytwiml')
def sayTwiml():
	r = twiml.Response()
	r.say("Fuck you DK")
	return str(r)


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)

