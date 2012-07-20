import os
import sys
import re
import datetime
import traceback
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

lessons = ['say', 'play', 'gather', 'record', 'dial', 'sms']

@app.route('/', methods=['GET', 'POST'])
def hello():
  return render_template('index.html')

@app.route('/lesson/<page>', methods=['GET', 'POST'])
def getPage(page):
  if page in lessons:
    capability = TwilioCapability(ACCOUNT_SID, AUTH_TOKEN)
    capability.allow_client_outgoing(APP_SID)
    token = capability.generate()
    params = {
      'token':token
    }
    return render_template(page + '.html', params=params)
  else:
    return render_template('notFound.html')

@app.route('/demo/callback', methods=['GET','POST'])
def callback():
  try:
    r = twiml.Response()
    if request.values['Digits'] == '1':
      r.say('Welcome to Twilio. This is an example of the Say verb.')
      return str(r)
    elif request.values['Digits'] == '2':
      r.play(url='http://tw.spurint.org/thx/banana-phone.mp3')
      return str(r)
    else:
      with r.gather(action='http://trytwilio.herokuapp.com/demo/callback', numDigits=1, timeout=10, method='GET') as g:
        g.say("Let's try this again. Press 1 to hear an example of the Say verb. Press 2 to hear Banana Phone.")
      return str(r)
  except Exception:
      r.say('Something went wrong')
      return str(r)

@app.route('/demo/recordingCallback', methods=['GET','POST'])
def recordingCallback():
  try:
    r = twiml.Response()
    r.say('Here is your recording.')
    r.play(url=request.values['RecordingUrl'])
    return str(r)
  except:
    r.say('Something went wrong')
    return str(r)

def getDemoTwiml(verb, toNumber, client):
  r = twiml.Response()
  if verb == 'say':
    r.say('Welcome to Twilio. This is an example of the Say verb.')
  elif verb == 'play':
    r.say('You are about to hear Banana Phone.')
    r.play(url='http://tw.spurint.org/thx/banana-phone.mp3')
  elif verb == 'gather':
    with r.gather(action='http://trytwilio.herokuapp.com/demo/callback', numDigits=1, timeout=10, method='GET') as g:
      g.say('Press 1 to hear an example of the Say verb. Press 2 to hear Banana Phone.')
  elif verb == 'record':
    r.say('After the beep, make your recording')
    r.record(action='http://trytwilio.herokuapp.com/demo/recordingCallback', method='GET')
  elif verb == 'sms':
    if client == 'true':
      r.say('Sorry, you need a phone number to be sent an sms.')
    else:
      r.say('You are about to be sent an sms.')
      r.sms('This is a test sms.', to=toNumber, from_='+17862458451')
  else:
    return 'failure'
  return str(r)

# Voice URL for our client app
@app.route('/client/getTwiml', methods=['GET','POST'])
def getClientTwiml():
  twiml = ''
  if request.values['demo'].lower() == 'true':
    twiml = getDemoTwiml(request.values['verb'].lower(),
                         request.values['toNumber'].lower(),
                         request.values['client'].lower())
  else:
    twiml = request.values['twimlBody']
  return twiml

# Endpoint for different options in the <Gather> tutorial
@app.route('/handleInput')
def requestTwimlForGather():
  s = request.values['twimlBody' + request.values['Digits']]
  sys.stderr.write(s + '\n')
  return s

# Endpoint to make an outbound call (Demo or User TwiML)
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

      ip = request.remote_addr
      if request.values['demo'].lower() == 'true':
        twimlBody = getDemoTwiml(request.values['verb'].lower())
      else:
        sys.stderr.write('TwimlBody: ' + request.values['twimlBody'] + '\n')
        twimlBody = request.values['twimlBody']

      url = 'http://trytwilio.herokuapp.com/requestCall?' + urlencode({'twimlBody':twimlBody})

      # If this is a gather, re-write the url to contain all of the twiml
      # of each digit provided and give it to handleInput
      if 'verb' in request.values:
        if request.values['verb'].lower() == 'gather' and request.values['demo'].lower() != 'true':
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
  except Exception:
    traceback.print_exc()
    return 'failure'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if port == 5000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
