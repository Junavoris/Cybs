from typing import List
from flask import Flask, render_template, request
from flask.helpers import url_for
from werkzeug.utils import redirect
from functions import *
import base64


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/Formulario', methods={"GET", "POST"})
def Formulario():
    if request.method == 'POST':
        CardType  = request.form['CardType']
        CardNumber  = request.form['CardNumber']
        CardExpirationMonth  = request.form['CardExpirationMonth']
        CardExpirationYear  = request.form['CardExpirationYear']
        TotalAmount  = request.form['TotalAmount']
        jso = json.loads(setup_completion_with_card_number(CardType, CardExpirationMonth, CardExpirationYear, CardNumber))
        data ={
            'accessToken': jso['consumerAuthenticationInformation']['accessToken'],
            'deviceDataCollectionUrl': jso['consumerAuthenticationInformation']['deviceDataCollectionUrl'],
            'referenceId': jso['consumerAuthenticationInformation']['referenceId'],
            'CardType': CardType,
            'CardNumber': CardNumber,
            'CardExpirationMonth': CardExpirationMonth,
            'CardExpirationYear': CardExpirationYear,
            'TotalAmount': TotalAmount
        }
        return render_template('PasarelaDos.html',data=data)
        
        # return json.loads(authorization_with_pa_enroll_authentication_needed(CardExpirationMonth, CardExpirationYear, CardNumber,TotalAmount,data['consumerAuthenticationInformation']['referenceId']))
    else:
        return render_template('PasarelaUno.html')

@app.route('/Enroll', methods={"GET", "POST"})
def Enroll():
    if request.method == 'POST':
        CardType  = request.form['CardType']
        CardNumber  = request.form['CardNumber']
        CardExpirationMonth  = request.form['CardExpirationMonth']
        CardExpirationYear  = request.form['CardExpirationYear']
        TotalAmount  = request.form['TotalAmount']
        SessionId = request.form['SessionId']
        ReferenceId = request.form['referenceId']
        Respuesta = json.loads(authorization_with_pa_enroll_authentication_needed(CardExpirationMonth, CardExpirationYear, CardNumber,TotalAmount,SessionId,ReferenceId))
        # return Respuesta
        if(Respuesta['status']=='PENDING_AUTHENTICATION'):
            pareq =  Respuesta['consumerAuthenticationInformation']['pareq']
            pareq = pareq + '=' * (4 - len(pareq) % 4) if len(pareq) % 4 != 0 else pareq
            data = {
                'SessionId': SessionId,
                'referenceId': ReferenceId,
                'CardType': CardType,
                'CardNumber': CardNumber,
                'CardExpirationMonth': CardExpirationMonth,
                'CardExpirationYear': CardExpirationYear,
                'TotalAmount': TotalAmount,
                'challengeWindowSize': json.loads(base64.b64decode(pareq))['challengeWindowSize'],
                'stepUpUrl': Respuesta['consumerAuthenticationInformation']['stepUpUrl'],
                'accessToken': Respuesta['consumerAuthenticationInformation']['accessToken'],
            }
            return render_template('PasarelaTres.html',data=data)
        elif(Respuesta['status']=='AUTHORIZED'):
            return render_template('Success.html',Respuesta=Respuesta)
        elif(Respuesta['status']=='DECLINED'):
            data=Respuesta['errorInformation']
            return render_template('Failed.html',data=data)
            
        
@app.route('/ReturnUrl', methods={"POST"})
def ReturnUrl():
    if request.method == 'POST':
        Cadena = request.form['TransactionId']
    return render_template('Respuesta.html', Cadena=Cadena)


@app.route('/Validate', methods={"GET", "POST"})
def Validate():
    if request.method == 'POST':
        CardType  = request.form['CardType']
        CardNumber  = request.form['CardNumber']
        CardExpirationMonth  = request.form['CardExpirationMonth']
        CardExpirationYear  = request.form['CardExpirationYear']
        TotalAmount  = request.form['TotalAmount']
        SessionId = request.form['SessionId']
        ReferenceId = request.form['referenceId']
        TransactionId = request.form['TransactionId']
        Respuesta = json.loads(authorization_with_payer_auth_validation(CardNumber, CardExpirationMonth, CardExpirationYear,TransactionId,TotalAmount))
        if(Respuesta['status']=='AUTHORIZED'):
            return render_template('Success.html',Respuesta=Respuesta)
        elif(Respuesta['status']=='DECLINED'):
            data=Respuesta['errorInformation']
            return render_template('Failed.html',data=data)
        else:
            
            return Respuesta

if __name__ == '__main__':
    app.run(debug=True)