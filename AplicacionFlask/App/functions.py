from CyberSource import *
import os
import json
from importlib.machinery import SourceFileLoader

config_file = os.path.join(os.getcwd(), "data", "Configuration.py")
configuration = SourceFileLoader("module.name", config_file).load_module()

# To delete None values in Input Request Json body
def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d

def setup_completion_with_card_number(CardType, CardExpirationMonth, CardExpirationYear, CardNumber):

    clientReferenceInformationCode = "cybs_test"
    clientReferenceInformationPartnerDeveloperId = "7891234"
    clientReferenceInformationPartnerSolutionId = "89012345"
    clientReferenceInformationPartner = Riskv1decisionsClientReferenceInformationPartner(
        developer_id = clientReferenceInformationPartnerDeveloperId,
        solution_id = clientReferenceInformationPartnerSolutionId
    )

    clientReferenceInformation = Riskv1decisionsClientReferenceInformation(
        code = clientReferenceInformationCode,
        partner = clientReferenceInformationPartner.__dict__
    )

    paymentInformationCardType = CardType
    paymentInformationCardExpirationMonth = CardExpirationMonth
    paymentInformationCardExpirationYear = CardExpirationYear
    paymentInformationCardNumber = CardNumber
    # paymentInformationCardType = "001"
    # paymentInformationCardExpirationMonth = "12"
    # paymentInformationCardExpirationYear = "2025"
    # paymentInformationCardNumber = "4000000000000101"
    paymentInformationCard = Riskv1authenticationsetupsPaymentInformationCard(
        type = paymentInformationCardType,
        expiration_month = paymentInformationCardExpirationMonth,
        expiration_year = paymentInformationCardExpirationYear,
        number = paymentInformationCardNumber
    )

    paymentInformation = Riskv1authenticationsetupsPaymentInformation(
        card = paymentInformationCard.__dict__
    )

    requestObj = PayerAuthSetupRequest(
        client_reference_information = clientReferenceInformation.__dict__,
        payment_information = paymentInformation.__dict__
    )


    requestObj = del_none(requestObj.__dict__)
    requestObj = json.dumps(requestObj)


    try:
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        api_instance = PayerAuthenticationApi(client_config)
        return_data, status, body = api_instance.payer_auth_setup(requestObj)

        # print("\nAPI RESPONSE CODE : ", type(return_data))
        # print("\nAPI RESPONSE BODY : ", body)

        return body
    except Exception as e:
        print("\nException when calling PayerAuthenticationApi->payer_auth_setup: %s\n" % e)

def authorization_with_pa_enroll_authentication_needed(CardExpirationMonth, CardExpirationYear, CardNumber, TotalAmount, SessionId, referenceId):
    clientReferenceInformationCode = "TC50171_3"
    clientReferenceInformation = Ptsv2paymentsClientReferenceInformation(
        code = clientReferenceInformationCode
    )


    processingInformationActionList = []
    processingInformationActionList.append("CONSUMER_AUTHENTICATION")
    processingInformationCapture = False
    processingInformation = Ptsv2paymentsProcessingInformation(
        action_list = processingInformationActionList,
        capture = processingInformationCapture
    )

    paymentInformationCardNumber = CardNumber
    paymentInformationCardExpirationMonth = CardExpirationMonth
    paymentInformationCardExpirationYear = CardExpirationYear
    paymentInformationCard = Ptsv2paymentsPaymentInformationCard(
        number = paymentInformationCardNumber,
        expiration_month = paymentInformationCardExpirationMonth,
        expiration_year = paymentInformationCardExpirationYear
    )

    paymentInformation = Ptsv2paymentsPaymentInformation(
        card = paymentInformationCard.__dict__
    )

    orderInformationAmountDetailsTotalAmount = TotalAmount
    orderInformationAmountDetailsCurrency = "usd"
    orderInformationAmountDetails = Ptsv2paymentsOrderInformationAmountDetails(
        total_amount = orderInformationAmountDetailsTotalAmount,
        currency = orderInformationAmountDetailsCurrency
    )

    orderInformationBillToFirstName = "John"
    orderInformationBillToLastName = "Smith"
    orderInformationBillToAddress1 = "201 S. Division St._1"
    orderInformationBillToAddress2 = "Suite 500"
    orderInformationBillToLocality = "Foster City"
    orderInformationBillToAdministrativeArea = "CA"
    orderInformationBillToPostalCode = "94404"
    orderInformationBillToCountry = "US"
    orderInformationBillToEmail = "accept@cybersource.com"
    orderInformationBillToPhoneNumber = "6504327113"
    orderInformationBillTo = Ptsv2paymentsOrderInformationBillTo(
        first_name = orderInformationBillToFirstName,
        last_name = orderInformationBillToLastName,
        address1 = orderInformationBillToAddress1,
        address2 = orderInformationBillToAddress2,
        locality = orderInformationBillToLocality,
        administrative_area = orderInformationBillToAdministrativeArea,
        postal_code = orderInformationBillToPostalCode,
        country = orderInformationBillToCountry,
        email = orderInformationBillToEmail,
        phone_number = orderInformationBillToPhoneNumber
    )

    orderInformation = Ptsv2paymentsOrderInformation(
        amount_details = orderInformationAmountDetails.__dict__,
        bill_to = orderInformationBillTo.__dict__
    )

    # consumerAuthenticationInformationRequestorId = "123123197675"
    consumerAuthenticationInformationReferenceId = referenceId
    consumerAuthenticationInformationTransactionMode = "S"
    consumerAuthenticationInformationReturnUrl = 'http://localhost:5000/ReturnUrl'
    consumerAuthenticationInformation = Ptsv2paymentsConsumerAuthenticationInformation(
        # fingerprint_session_id= consumerAuthenticationInformationFingerprintSessionId
        # requestor_id = consumerAuthenticationInformationRequestorId,
        reference_id = consumerAuthenticationInformationReferenceId,
        transaction_mode = consumerAuthenticationInformationTransactionMode,
        return_url=consumerAuthenticationInformationReturnUrl
    )
    
    deviceInformation = Ptsv2paymentsDeviceInformation(
        fingerprint_session_id= SessionId
    )
    

    requestObj = CreatePaymentRequest(
        client_reference_information = clientReferenceInformation.__dict__,
        processing_information = processingInformation.__dict__,
        payment_information = paymentInformation.__dict__,
        order_information = orderInformation.__dict__,
        consumer_authentication_information = consumerAuthenticationInformation.__dict__,
        device_information=deviceInformation.__dict__
    )


    requestObj = del_none(requestObj.__dict__)
    requestObj = json.dumps(requestObj)


    try:
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        api_instance = PaymentsApi(client_config)
        return_data, status, body = api_instance.create_payment(requestObj)

        # print("\nAPI RESPONSE CODE : ", status)
        # print("\nAPI RESPONSE BODY : ", body)

        return body
    except Exception as e:
        print("\nException when calling PaymentsApi->create_payment: %s\n" % e)

def authorization_with_payer_auth_validation(CardNumber, CardExpirationMonth, CardExpirationYear,TransactionId,TotalAmount):
    clientReferenceInformationCode = "TC50171_3"
    clientReferenceInformation = Ptsv2paymentsClientReferenceInformation(
        code = clientReferenceInformationCode
    )


    processingInformationActionList = []
    processingInformationActionList.append("VALIDATE_CONSUMER_AUTHENTICATION")
    processingInformationCapture = False
    processingInformation = Ptsv2paymentsProcessingInformation(
        action_list = processingInformationActionList,
        capture = processingInformationCapture
    )

    paymentInformationCardNumber = CardNumber
    paymentInformationCardExpirationMonth = CardExpirationMonth
    paymentInformationCardExpirationYear = CardExpirationYear
    paymentInformationCard = Ptsv2paymentsPaymentInformationCard(
        number = paymentInformationCardNumber,
        expiration_month = paymentInformationCardExpirationMonth,
        expiration_year = paymentInformationCardExpirationYear
    )

    paymentInformation = Ptsv2paymentsPaymentInformation(
        card = paymentInformationCard.__dict__
    )

    orderInformationAmountDetailsTotalAmount = TotalAmount
    orderInformationAmountDetailsCurrency = "usd"
    orderInformationAmountDetails = Ptsv2paymentsOrderInformationAmountDetails(
        total_amount = orderInformationAmountDetailsTotalAmount,
        currency = orderInformationAmountDetailsCurrency
    )

    orderInformationBillToFirstName = "John"
    orderInformationBillToLastName = "Smith"
    orderInformationBillToAddress1 = "201 S. Division St._1"
    orderInformationBillToAddress2 = "Suite 500"
    orderInformationBillToLocality = "Foster City"
    orderInformationBillToAdministrativeArea = "CA"
    orderInformationBillToPostalCode = "94404"
    orderInformationBillToCountry = "US"
    orderInformationBillToEmail = "accept@cybersource.com"
    orderInformationBillToPhoneNumber = "6504327113"
    orderInformationBillTo = Ptsv2paymentsOrderInformationBillTo(
        first_name = orderInformationBillToFirstName,
        last_name = orderInformationBillToLastName,
        address1 = orderInformationBillToAddress1,
        address2 = orderInformationBillToAddress2,
        locality = orderInformationBillToLocality,
        administrative_area = orderInformationBillToAdministrativeArea,
        postal_code = orderInformationBillToPostalCode,
        country = orderInformationBillToCountry,
        email = orderInformationBillToEmail,
        phone_number = orderInformationBillToPhoneNumber
    )

    orderInformation = Ptsv2paymentsOrderInformation(
        amount_details = orderInformationAmountDetails.__dict__,
        bill_to = orderInformationBillTo.__dict__
    )

    consumerAuthenticationInformationAuthenticationTransactionId = TransactionId
    consumerAuthenticationInformation = Ptsv2paymentsConsumerAuthenticationInformation(
        authentication_transaction_id = consumerAuthenticationInformationAuthenticationTransactionId
    )

    requestObj = CreatePaymentRequest(
        client_reference_information = clientReferenceInformation.__dict__,
        processing_information = processingInformation.__dict__,
        payment_information = paymentInformation.__dict__,
        order_information = orderInformation.__dict__,
        consumer_authentication_information = consumerAuthenticationInformation.__dict__
    )


    requestObj = del_none(requestObj.__dict__)
    requestObj = json.dumps(requestObj)


    try:
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        api_instance = PaymentsApi(client_config)
        return_data, status, body = api_instance.create_payment(requestObj)

        # print("\nAPI RESPONSE CODE : ", status)
        # print("\nAPI RESPONSE BODY : ", body)

        return body
    except Exception as e:
        print("\nException when calling PaymentsApi->create_payment: %s\n" % e)

