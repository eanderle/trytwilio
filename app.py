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

MAX_CALLS_PER_DAY = 100
FROM_NUMBER = os.environ.get('FROM_NUMBER')
APP_SID = os.environ.get('APP_SID')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
app = Flask(__name__)

client = TwilioRestClient()

connection = Connection(os.environ.get('MONGOLAB_URI'))
connection.register([OutboundCall])
db = connection['heroku_app5944498']

@app.route('/', methods=['GET', 'POST'])
def hello():
  capability = TwilioCapability(ACCOUNT_SID, AUTH_TOKEN)
  capability.allow_client_outgoing(APP_SID)
  token = capability.generate()
  params = {
    'token':token
  }
  return render_template('index.html', params=params)

@app.route('/say', methods=['GET', 'POST'])
def say():
  capability = TwilioCapability(ACCOUNT_SID, AUTH_TOKEN)
  capability.allow_client_outgoing(APP_SID)
  token = capability.generate()
  params = {
    'token':token
  }
  return render_template('say.html', params=params)

@app.route('/testClient', methods=['GET','POST'])
def testClient():
  application_sid = 'AP256035c642dcf6ad2f82119f86e4ea35'

  capability = TwilioCapability(ACCOUNT_SID, AUTH_TOKEN)
  capability.allow_client_outgoing(application_sid)
  token = capability.generate()

  return render_template("client.html", token=token)

@app.route('/demo/callback', methods=['GET','POST'])
def playCallback():
  try:
    if request.values["Digits"] == "1":
      return "<Response><Say>Welcome to Twilio, This is an example of the Say verb</Say></Response>"
    elif request.values["Digits"] == "2":
      return "<Response><Play>http://tw.spurint.org/thx/banana-phone.mp3</Play></Response>"
    else:
      return "<Response><Say>You have to either press 1 or 2</Say></Response>"
  except Exception as e:
    return "<Response><Say>Something went wrong</Say></Response>"

@app.route('/client/getTwiml', methods=['GET','POST'])
def requestTwiml():
  try:
    if request.values["DemoType"] == "Say":
      #sys.stderr.write("Say demo type reached\n")
      return "<Response><Say>Welcome to Twilio, this is an example of the Say verb</Say></Response>"
    elif request.values["DemoType"] == "Play":
      #sys.stderr.write("Play type reached\n")
      return "<Response><Play>http://tw.spurint.org/thx/banana-phone.mp3</Play></Response>"
    elif request.values["DemoType"] == "Gather":
      return "<Response><Gather action='/callback' method='GET'><Say>Enter 1 to hear banana phone</Say></Gather></Response>"
    else:
      #sys.stderr.write("Nothing reached\n")
      return "<Response><Say>Welcome to Twilio this is a test</Say></Response>"
  except Exception as e:
    #sys.stderr.write(e)
    return "<Response><Say>Welcome to Twilio this is an error </Say></Response>"

@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
  try:
    if request.method == 'GET':
      return request.values['twimlBody']

    if request.method == 'POST':
      # Clean up numbers
      # Delete any non-numeric character
      sys.stderr.write('Phone Number: ' + request.values['To'] + '\n')
      sys.stderr.write('Cleaning up phone number...\n')
      toNumber = re.sub('[^0-9]', '', request.values['To'])

      # If the number is 10 digits, it's US/Canada, so do a +1
      # Else it's some other country (we assume) so just add a plus
      toNumber = ('+1' if len(toNumber) == 10 else '+') + toNumber

      sys.stderr.write('TwimlBody: ' + request.values['twimlBody'] + '\n')
      ip = request.remote_addr
      twimlBody = request.values['twimlBody']

      # Clean up old entries and make sure this number hasn't been called too much
      d = datetime.datetime.utcnow() - datetime.timedelta(days = 1)
      connection.OutboundCall.collection.remove({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                          {'timestamp': {'$lt': d}}]})
      count = connection.OutboundCall.find({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                         {'timestamp': {'$lt': d}}]}).count()
      if count >= MAX_CALLS_PER_DAY:
        sys.stderr.write('Error: too many calls\n')
        raise Exception()

      sys.stderr.write('Making Twilio Rest Request...\n')
      client.calls.create(to=toNumber, from_=FROM_NUMBER, 
        url='http://trytwilio.herokuapp.com/requestCall?' + urlencode({'twimlBody':twimlBody}),
        method='GET')

      sys.stderr.write('Creating call in db...\n')
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
