import RPi.GPIO as GPIO

pins = { # first the input pins
        'chime_main':{
            'pin':5,
            'value1':'Chime at main doors.', # This defines the notification sent to ifttt.
            'setup':{
                'io':GPIO.IN,
                'pud':GPIO.PUD_OFF
            }
        },
        'chime_up':{
            'pin':27,
            'value1':'Chime at upper doors.',
            'setup':{
                'io':GPIO.IN,
                'pud':GPIO.PUD_UP
            }
        },
        # then the output pins
        'relay_main':{
            'pin':17,
            'setup':{
                'io':GPIO.OUT,
                'pud':GPIO.PUD_OFF
            }
        },
        'relay_unused':{
            'pin':18,
            'setup':{
                'io':GPIO.OUT,
                'pud':GPIO.PUD_OFF
            }
        }
    }


