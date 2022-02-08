from typing import List
from flask import Flask, render_template, request
from flask.helpers import url_for
from werkzeug.utils import redirect
# from functions import *
import base64
from StandAloneJWT import *


app = Flask(__name__)
# @app.route('/')
# def home():
#     return render_template('home.html')
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
        payload ={
            "clientReferenceInformation": {
                "code": "cybs_test5068",
            },
            "paymentInformation": {
                "card": {
                "type": CardType,
                "expirationMonth": CardExpirationMonth,
                "expirationYear": CardExpirationYear,
                "number": CardNumber
                }
            }
            }
        
        standalone_http_signature_obj = StandAloneJWT(json.dumps(payload))
        rsrc='/risk/v1/authentication-setups'
        ss=standalone_http_signature_obj.process_post(rsrc)
        jso=json.loads(ss.data.decode('utf-8'))
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

        payload ={
            "clientReferenceInformation": {
                "code": "cybs_test5068"
            },
            "processingInformation": {
                "actionList": [
                "CONSUMER_AUTHENTICATION"
                ]
            },
            "paymentInformation": {
                "card": {
                "number": CardNumber,
                "expirationMonth": CardExpirationMonth,
                "expirationYear": CardExpirationYear
                }
            },
            "orderInformation": {
                "amountDetails": {
                "totalAmount": TotalAmount,
                "currency": "usd"
                },
                "billTo": {
                "firstName": "John",
                "lastName": "Smith",
                "address1": "201 S. Division St._1",
                "address2": "Suite 500",
                "locality": "Foster City",
                "administrativeArea": "CA",
                "postalCode": "94404",
                "country": "US",
                "email": "accept@cybersource.com",
                "phoneNumber": "6504327113"
                }
            },
            "deviceInformation": {
                "fingerprintSessionId": SessionId
            },
            "consumerAuthenticationInformation": {
                "returnUrl": "http://localhost:5000/ReturnUrl",
                # "requestorId": "123123197675",
                "referenceId": ReferenceId
            }
            }
        
        standalone_http_signature_obj = StandAloneJWT(json.dumps(payload))
        rsrc='/pts/v2/payments'
        ss=standalone_http_signature_obj.process_post(rsrc)
        Respuesta=json.loads(ss.data.decode('utf-8'))
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

        payload ={
            "clientReferenceInformation": {
                "code": "cybs_test5068"
            },
            "processingInformation": {
                "actionList": [
                "VALIDATE_CONSUMER_AUTHENTICATION"
                ]
            },
            "paymentInformation": {
                "card": {
                "number": CardNumber,
                "expirationMonth": CardExpirationMonth,
                "expirationYear": CardExpirationYear
                }
            },
            "orderInformation": {
                "amountDetails": {
                    "totalAmount": TotalAmount,
                    "currency": "usd"
                },
                "billTo": {
                    "firstName": "John",
                    "lastName": "Smith",
                    "address1": "201 S. Division St._1",
                    "address2": "Suite 500",
                    "locality": "Foster City",
                    "administrativeArea": "CA",
                    "postalCode": "94404",
                    "country": "US",
                    "email": "accept@cybersource.com",
                    "phoneNumber": "6504327113"
                }
            },
            "consumerAuthenticationInformation": {
                "authenticationTransactionId": TransactionId
            }
            }
        
        standalone_http_signature_obj = StandAloneJWT(json.dumps(payload))
        rsrc='/pts/v2/payments'
        ss=standalone_http_signature_obj.process_post(rsrc)
        Respuesta=json.loads(ss.data.decode('utf-8'))

        if(Respuesta['status']=='AUTHORIZED'):
            return render_template('Success.html',Respuesta=Respuesta)
        elif(Respuesta['status']=='DECLINED'):
            data=Respuesta['errorInformation']
            return render_template('Failed.html',data=data)
        else:
            
            return Respuesta

if __name__ == '__main__':
    app.run(debug=True)