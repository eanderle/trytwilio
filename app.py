import os
import re
from flask import Flask, request, render_template
from urllib import urlencode
from twilio.rest import TwilioRestClient
from mongokit import Connection

app = Flask(__name__)

account = "ACefb267919ab7c793e889ce40b8db2506"
auth_token = "6cb0a97591eaf94ca237572fe4472458"
client = TwilioRestClient(account, auth_token)

mongoHost = re.match('.*@(.*):', os.environ.get('MONGOLAB_URI')).group(1)
mongoPort = int(re.match('.*@.*:(.*)/', os.environ.get('MONGOLAB_URI')).group(1))
connection = Connection(mongoHost, mongoPort)

@app.route('/', methods=['GET', 'POST'])
def hello():
  params=[]
  return render_template('index.html', params=params)

@app.route('/test', methods=['GET', 'POST'])
def xmlcheck():
  return render_template('test.html')

@app.route('/testXml', methods=['GET', 'POST'])
def xmlcheck():
  return render_template('testValidation.html')

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
      return 'success'
  except:
    return 'failure'
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
