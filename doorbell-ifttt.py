import os
from time import sleep

import RPi.GPIO as GPIO

from ring_api import client
import urllib.request

from flask import Flask
from flask import request, abort

# Import ids of clients, pin definitions and 
from chats import chats
from pins import pins
from keys import KEY
# Initialize Flask app
app = Flask(__name__)

# Setup RPi GPIO pins
GPIO.setmode(GPIO.BCM)
for pin, values in pins.items():
    GPIO.setup(values['pin'], values['setup']['io'], pull_up_down=values['setup']['pud'])

# setup the ring service
options = client.options()
options.verbose = False
options.interpreter = True

# initialize the ring client
ring = client.Client(options)
ring.start()
sleep(1)

# i.e. interogate the ring daemon
account = ring.dring.config.accounts()[0]
details = ring.dring.config.account_details(account)

# function to trigger relay for unlocking the doors
def odkleni_vrata(pin):
    try:
        GPIO.output(pin, GPIO.HIGH)
        sleep(5)
        GPIO.output(pin, GPIO.LOW)
    except Exception as e:
        print(e)
        GPIO.cleanup()

# routes called by ifttt
@app.route('/unlock')
def odkleni():
    # use global variables chats and pins
    global chats
    global pins
    # check for the instructions and key in the url. Then send notification to the sender of the request.
    if request.args.get('instruction')=="unlock" and request.args.get('key')==KEY:
        sender = chats[request.args.get('sender')]['ifttt']
        data=urllib.parse.urlencode("Unlocking main entrance.").encode('utf-8')
        req=urllib.request.Request("https://maker.ifttt.com/trigger/notify/with/key/{}".format(sender),data=data)
        urllib.request.urlopen(req)
        # If you want to play a tune when unlocking doors, uncomment this and add sound file unlock_tune.wav.
        #os.system('aplay --device=hw:1,0 unlock_tune.wav &')
        odkleni_vrata(pins['relay_main']['pin'])
        return 'Success' # flask always needs a return statement.
    elif request.args.get('instruction')=="call" and request.args.get('key')==KEY:
        sender = request.args.get('sender')
        call_dest = chats[sender]['ring']
        # place a call to the sender.
        ring.dring.call.place_call(account,call_dest)
        return "Success"
    else:
        # if either key or instructions are wrong, then return 404.
        return abort(404)

### Here we listen for chime on pins.
# here we track if the button was pressed. This is to prevent triggering multiple notifications when someone rings.
last_status=0

# callback function to send notification to ifttt.
def handle(pin_value):
    global last_status
    global chats
    global account
    global pins
    if(GPIO.input(pin_value['pin']) and last_status==0):
        for c, v in chats.items():
            k = v['ifttt']
            data=urllib.parse.urlencode(pin_value['value1']).encode('utf-8')
            req=urllib.request.Request("https://maker.ifttt.com/trigger/notify/with/key/{}".format(k),data=data)
            urllib.request.urlopen(req)
        last_status=1
    elif(GPIO.input(pin_value['pin']) == False and last_status==1):
        last_status=0

# define actions for input pins.
for pin_name, values in pins.items():
    if values['setup']['io']==GPIO.IN:
        GPIO.add_event_detect(values['pin'], GPIO.BOTH, callback=lambda x:handle(values))

# start app
if __name__ == '__main__':
    app.run(host='0.0.0.0') # run on public ip
    # a hook to quit ring client nicely if ctrl c is pressed.
    try:
        while True:
            sleep(1)
    except(KeyboardInterrupt, SystemExit):
        ring.stop()

