import os
import sys
import re
import datetime
from flask import Flask, request, render_template
from urllib import urlencode
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability
from twilio import twiml
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
    r = twiml.Response()
    if request.values["Digits"] == "1":
      r.say("Welcome to Twilio, this is an example of the say verb")
      return str(r)
    elif request.values["Digits"] == "2":
      r.play("http://tw.spurint.org/thx/banana-phone.mp3")
      return str(r)
    else:
      r.say("Let's try again, you have to press either 1 or 2")
      r.gather(action='/callback')
      return str(r)
  except Exception as e:
      r.say("Something went wrong")
      return str(r)

@app.route('/client/getTwiml', methods=['GET','POST'])
def requestTwiml():
  try:
    r = twiml.Response()
    if request.values["DemoType"] == "Say":
      #sys.stderr.write("Say demo type reached\n")
      r.say("Welcome to Twilio, this is an example of the say verb")
      return str(r)
    elif request.values["DemoType"] == "Play":
      #sys.stderr.write("Play type reached\n")
      r.say("You are about to hear the one and only banana phone")
      r.play(url="http://tw.spurint.org/thx/banana-phone.mp3")
      return str(r)
    elif request.values["DemoType"] == "Gather":
      r.say("Enter 1 to hear the previous say message, press 2 to hear banana phone again")
      r.gather(action='http://trytwilio.herokuapp.com/demo/callback')
      return str(r)
    else:
      #sys.stderr.write("Nothing reached\n")
      return request.values['twimlBody']
  except Exception as e:
    #sys.stderr.write(e)
      r.say("Something went wrong")
      return str(r)

@app.route('/handleInput')
def requestTwimlForGather():
  s = request.values['twimlBody' + request.values['Digits']]
  sys.stderr.write(s + '\n')
  return s

@app.route('/demo/requestDemoCall', methods=['GET', 'POST'])
def requestDemoCall():
  try:
    url = 'http://trytwilio.herokuapp.com/client/getTwiml?' + urlencode({'DemoType':"Gather"})
    call = client.calls.create(to="+17033891424", from_="+17862458451", url=url, method='GET')
    return call.sid
  except:
    return "Shit failed"

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

      url = 'http://trytwilio.herokuapp.com/requestCall?' + urlencode({'twimlBody':twimlBody})

      # If this is a gather, re-write the url to contain all of the twiml
      # of each digit provided and give it to handleInput
      if 'verb' in request.values:
        if request.values['verb'].lower() == 'gather':
          url = 'http://trytwilio.herokuapp.com/handleInput?'
          twimlBodies = {}
          # Go through each digit, and if it was provided, add it to the url
          for c in '0123456789#*':
            s = 'twimlBody' + c
            if s in request.values:
              twimlBodies.update({s:request.values[s]})

          url += urlencode(twimlBodies)

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
        url=url, method='GET')

      sys.stderr.write('Creating call in db...\n')
      call = connection.OutboundCall()
      call['number'] = toNumber
      call['ip'] = ip
      call.validate()
      call.save()

      return 'success'
  except Exception as e:
    sys.stderr.write('Got exception: ' + e)
    return 'failure'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
