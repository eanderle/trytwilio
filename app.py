import os
import sys
import datetime
from flask import Flask, request, render_template
from urllib import urlencode
from twilio.rest import TwilioRestClient
from mongokit import Document, Connection

class OutboundCall(Document):
  __collection__ = 'outboundCalls'
  __database__ = 'heroku_app5944498'
  structure = { 'number': basestring,
                'timestamp': datetime.datetime
  }
  required_fields = ['number', 'timestamp']
  default_values = { 'timestamp': datetime.datetime.utcnow()}

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
def xmlcheck():
  return render_template('test.html')

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
      call = connection.OutboundCall()
      call['number'] = toNumber
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
