from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
import json
import time
import smtplib

app = Flask(__name__)
app.config["DEBUG"] = True

carriers = {
	'att':     'txt.att.net',
	'tmobile': 'tmomail.net',
	'verizon': 'vtext.com',
	'boost':   'sms.myboostmobile.com',
	'cricket': 'sms.cricketwireless.net',
	'usc':     'email.uscc.net'
}

def sendSMS(text, phone, provider):
    to_number = f"{phone}@{carriers[provider]}"
    auth = ('teamaccessdenied22@gmail.com', 'vvgpsxsftdcxovmb')

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( "smtp.gmail.com", 587 )
    server.starttls()
    server.login(auth[0], auth[1])

    message = 'Subject: {}\n\n{}'.format("TEMP SYSTEM", text)
    # Send text message through SMS gateway of destination number
    server.sendmail( auth[0], to_number, message)

@app.route("/", methods=["GET"])
def index():
    return render_template("main_page.html")

@app.route("/up", methods=["GET"])
def upload():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    currTime = int(time.time()) #get current time using time library

    val = request.args.get('val')
    if (val == "start"):
        data['boxOn'] = 1
    else:
        val = int(val)
        if (val > -10 and val < 63):
            if (data['temp'][0][0] != currTime):
                data['temp'].insert(0, [currTime, val])
                data['boxOn'] = 1
                data['sensorConnected'] = 1
                if data['temp'][1][1] > data['alertLow'] and data['temp'][1][1] < data['alertHigh']:
                    if val >= data['alertHigh']: #send a text with a high temperature alert
                        sendSMS(text=data['textHigh'], phone=data['phone'], provider=data['phoneProvider'])
                    elif val <= data['alertLow']: #send a text with a low temperature alert
                        sendSMS(text=data['textLow'], phone=data['phone'], provider=data['phoneProvider'])
        else:
            data['boxOn'] = 1
            data['sensorConnected'] = 0

    if(len(data['temp']) > 300):
        data['temp'] = data['temp'][:300]

    with open('/home/accessdenied/mysite/data.json', 'w') as f:
        json.dump(data, f)

    return f"{data['dispOn']}, {val}"

@app.route("/data.json", methods=["GET"])
def data(): #read the temperature reading from the json file
    f = open('/home/accessdenied/mysite/data.json')
    s = f.read()
    f.close()
    return s

@app.route("/toggle", methods=["GET"])
def toggle():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    f.close()

    if data['dispOn'] == 0:
        data['dispOn'] = 1
    else:
        data['dispOn'] = 0

    with open('/home/accessdenied/mysite/data.json', 'w') as f:
        json.dump(data, f)
    return "Toggled display: {data['dispOn']}"

@app.route("/boxOff", methods=["GET"])
def boxOff():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    f.close()
    data['boxOn'] = 0
    with open('/home/accessdenied/mysite/data.json', 'w') as f:
        json.dump(data, f)
    return "Box off"

@app.route("/dispStatus", methods=["GET"])
def dispStatus():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    f.close()
    return f"{data['dispOn']}"

@app.route("/settings", methods=["GET", "POST"])
def settings():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    f.close()
    if request.method == "GET":
        return render_template("settings.html", data=data)
    else:
        data['phone'] = request.form["phone"]
        data['phoneProvider'] = request.form["phone_provider"]
        data['alertHigh'] = int(request.form["limit_hi"])
        data['alertLow'] = int(request.form["limit_lo"])
        data['textHigh'] = request.form["text_hi"]
        data['textLow'] = request.form["text_lo"]

        with open('/home/accessdenied/mysite/data.json', 'w') as f:
            json.dump(data, f)

        # return f"{data['phone']}, {data['phoneProvider']}<br>({data['alertLow']}, {data['textLow']})<br>({data['alertHigh']}, {data['textHigh']})"
        return redirect(url_for('index'))


@app.route("/testsms", methods=["GET"])
def testsms():
    f = open('/home/accessdenied/mysite/data.json')
    data = json.load(f)
    f.close()

    sendSMS("TEST", data['phone'], data['phoneProvider'])

    return redirect(url_for('index'))


@app.route("/testemail", methods=["GET"])
def testemail():
    auth = ('teamaccessdenied22@gmail.com', 'vvgpsxsftdcxovmb')
    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( "smtp.gmail.com", 587 )
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail( auth[0], "marajeys@gmail.com", "TEST")
    return redirect(url_for('index'))
