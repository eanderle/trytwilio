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
  return render_template('testValidation.html')

@app.route('/testClient', methods=['GET','POST'])
def testClient():
  application_sid = "AP256035c642dcf6ad2f82119f86e4ea35"

  capability = TwilioCapability()
  capability.allow_client_outgoing(application_sid)
  token = capability.generate()

  return render_template("client.html", token=token)
  

@app.route('/client/getTwiml')
def requestTwiml():
  return "<Response><Say>This is a test</Say></Response>"

@app.route('/requestCall', methods=['GET', 'POST'])
def requestCall():
  try:
    if request.method == 'GET':
      return request.values['twimlBody']

    if request.method == 'POST':
      # Clean up numbers
      # Delete any non-numeric character
      ex = re.compile('[^0-9]')
      toNumber = re.sub(ex, '', request.values['To'])
      fromNumber = re.sub(ex, '', request.values['From'])
      ip = request.remote_addr
      
      # If the number is 10 digits, it's US/Canada, so do a +1
      # Else it's some other country (we assume) so just add a plus
      toNumber = ('+1' if len(toNumber) == 10 else '+') + toNumber
      fromNumber = ('+1' if len(fromNumber) == 10 else '+') + fromNumber

      twimlBody = request.values['twimlBody']

      # Clean up old entries and make sure this number hasn't been called too much
      d = datetime.datetime.utcnow() - datetime.timedelta(days = 1)
      connection.OutboundCall.collection.remove({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                          {'timestamp': {'$lt': d}}]})
      if connection.OutboundCall.find({'$and': [{'$or': [{'number': toNumber}, {'ip': ip}]},
                                                         {'timestamp': {'$lt': d}}]}) >= MAX_CALLS_PER_DAY:
        raise Exception()

      client.calls.create(to=toNumber, from_=fromNumber, 
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
