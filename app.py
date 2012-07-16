import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from twilio import twiml
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability

os.environ["TWILIO_ACCOUNT_SID"] = "ACefb267919ab7c793e889ce40b8db2506"
os.environ["TWILIO_AUTH_TOKEN"] = "6cb0a97591eaf94ca237572fe4472458"

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
  params=[]
  return render_template('index.html', params=params)


@app.route('/calls/say')
def sayTest():
	#call = client.calls.create(to="7033891424",
	#			   from_="7862458451",
	#			   url= "http://trytwilio.herokuapp.com/calls/saytwiml")
	account = "ACefb267919ab7c793e889ce40b8db2506"
	token = "6cb0a97591eaf94ca237572fe4472458"

	client = TwilioRestClient(account, token)
	#call = client.calls.create(to="7033891424",
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

