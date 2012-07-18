import os
import sys
import re
import datetime
from flask import Flask, request, render_template
from urllib import urlencode
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability
from mongokit import Document, Connection

class OutboundCall(Document):
  __collection__ = 'outboundCalls'
  __database__ = 'heroku_app5944498'
  structure = { 'number': basestring,
                'ip': basestring,
                'timestamp': datetime.datetime
  }
  required_fields = ['number', 'ip', 'timestamp']
  default_values = { 'timestamp': datetime.datetime.utcnow()}

MAX_CALLS_PER_DAY = 10
FROM_NUMBER = os.environ.get('FROM_NUMBER')
app = Flask(__name__)

client = TwilioRestClient()

connection = Connection(os.environ.get('MONGOLAB_URI'))
connection.register([OutboundCall])
db = connection['heroku_app5944498']

@app.route('/', methods=['GET', 'POST'])
def hello():
  params=[]
  return render_template('index.html', params=params)

@app.route('/test', methods=['GET', 'POST'])
def test():
  return render_template('test.html')

@app.route('/testXml', methods=['GET', 'POST'])
def xmlcheck():
  return render_template('firstpage.html')

@app.route('/testClient', methods=['GET','POST'])
def testClient():
  application_sid = "AP256035c642dcf6ad2f82119f86e4ea35"

  capability = TwilioCapability("ACefb267919ab7c793e889ce40b8db2506", "6cb0a97591eaf94ca237572fe4472458")
  capability.allow_client_outgoing(application_sid)
  token = capability.generate()

  return render_template("client.html", token=token)


@app.route('/client/getTwiml/', methods=['GET','POST'])
def requestTwiml():
  try:
		if request.values["DemoType"] == "Say":
			sys.stderr.write("Say demo type reached\n")
			return "<Response><Say>Welcome to Twilio, this is an example of the Say verb</Say></Response>"
		elif request.values["DemoType"] == "Play":
			sys.stderr.write("Play type reached\n")
			return "<Response><Play></Play><Response>"
		else:
			sys.stderr.write("Nothing reached\n")
			return "<Response><Say>Welcome to Twilio </Say></Response>"
  except:
    sys.stderr.write("Execption\n")
	  return "<Response><Say>Welcome to Twilio </Say></Response>"
@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
  try:
    if request.method == 'GET':
      return request.values['twimlBody']

    if request.method == 'POST':
      # Clean up numbers
      # Delete any non-numeric character
      toNumber = re.sub('[^0-9]', '', request.values['To'])

      # If the number is 10 digits, it's US/Canada, so do a +1
      # Else it's some other country (we assume) so just add a plus
      toNumber = ('+1' if len(toNumber) == 10 else '+') + toNumber

      ip = request.remote_addr
      twimlBody = request.values['twimlBody']

      # Clean up old entries and make sure this number hasn't been called too much
      d = datetime.datetime.utcnow() - datetime.timedelta(days = 1)
      connection.OutboundCall.collection.remove({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                          {'timestamp': {'$lt': d}}]})
      if connection.OutboundCall.find({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                         {'timestamp': {'$lt': d}}]}).count() >= MAX_CALLS_PER_DAY:
        raise Exception()

      client.calls.create(to=toNumber, from_=FROM_NUMBER, 
        url='http://trytwilio.herokuapp.com/requestCall?' + urlencode({'twimlBody':twimlBody}),
        method='GET')

      call = connection.OutboundCall()
      call['number'] = toNumber
      call['ip'] = ip
      call.validate()
      call.save()

      return 'success'
  except:
    return 'failure'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
