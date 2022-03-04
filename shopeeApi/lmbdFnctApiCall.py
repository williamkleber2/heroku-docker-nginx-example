import datetime
import json
import collections
from copy import copy
from typing import List, Dict, Any
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.db.models import Q

from shopee.models import *


def createUserShopee(usrShopee) -> None:
    """ Cria um novo usuário na Shopee.
    :param usrShopee: Os dados crus do usuário Shopee. """

    usrShopeeRaw = copy(usrShopee)
    usrShopeeDict = usrShopeeRaw.__dict__
    usrShopeeDict.pop("_state", None)
    usrShopeeDict.pop("creation_request_date", None)
    bodyToSend = {"userShopee": usrShopeeDict}
    sqsUrl = settings.REST_GATEWAY_CREATE_USERSHPOPEE
    apiKey = settings.REST_GATEWAY_CREATE_USERSHOPEE_ORDER_KEY
    print(apiKey)
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header)
    print(response)
    print(response.text)
    responseJson = response.json()
    if response.status_code == 200 and responseJson.get("statusCode") != 200:
        raise Exception(responseJson.get("body"))

def loginInfoUserShopee(userShopeeData: UserShopee) -> None:
    """ Faz o login com a conta UserShopee.
    :param userShopeeData: Os dados de login da conta. """

    bodyToSend = {
        "email": userShopeeData.email,
        "spc_f": userShopeeData.spc_f,
        "password": userShopeeData.password,
    }
    sqsUrl = settings.REST_GATEWAY_INFO_LOGIN_USERSHOPEE
    apiKey = settings.REST_GATEWAY_INFO_LOGIN_USERSHOPEE_API_KEY
    header= {"accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
            "content-type": "application/json",
            "x-api-key": apiKey }
    print("'" + sqsUrl + "'")
    response = requests.post(sqsUrl, json=bodyToSend, headers=header)
    
    return response.json()

def createUsersShopees(userShopeeIds) -> None:
    """ Cria contas UserShopee.
    :param userShopeeIds: A lista de IDs das contas para criar. """

    bodyToSend = {"userShopeeIds": userShopeeIds}
    sqsUrl = settings.REST_GATEWAY_CREATE_USERSSHOPEES
    apiKey = settings.REST_GATEWAY_CREATE_USERSSHOPEES_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header)


def upsertShopifyProducts(userShop) -> None:
    """ Faz um UPSERT nos produtos da Shopify.
    :param userShop: Os dados do UserShop. """

    bodyToSend = {"id": userShop.id}
    sqsUrl = settings.API_GATEWAY_UPSERT_PRODUCTS
    urlHost = urlparse(sqsUrl).netloc
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "host": urlHost,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header)


def apiMakeOrderManually(orderIdLst) -> None:
    """ Faz uma make order manualmente.
    :param orderIdList: Lista de order IDs. """

    print(orderIdLst)
    sqsUrl = settings.API_GATEWAY_MAKE_ORDER
    urlHost = urlparse(sqsUrl).netloc
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "host": urlHost,
    }

    response = requests.post(sqsUrl, json=orderIdLst, headers=header)


def call_cancel_order(orders: List[int]) -> None:
    """ Cancela orders.
    :param orders: Lista de IDs orders das orders para cancelar. """

    body = {"ids": orders}

    url = settings.REST_GATEWAY_CANCEL_ORDER

    headers = {
        "x-api-key": settings.REST_GATEWAY_CANCEL_ORDER_KEY,
    }

    response = requests.post(url, json=body, headers=headers)

    print(f"{response=}")
    print(f"{response.text=}")


def cancel_order_line_items(ids: List[int]) -> None:
    """ Cancela OrderLineItems.
    :param ids: Os IDs das OLIs para cancelar. """

    query = OrderLineItem.objects.filter(id__in=ids)

    orderLineItemIds = []

    for order_line_item in query:
        if order_line_item.cancellation_status != "NC":  # not canceled
            continue

        order_line_item.cancellation_status = "WC"  # will be canceled

        order_line_item.status = "C"
        order_line_item.updated_date_c = timezone.now()

        orderLineItemIds.append(order_line_item.id)

    OrderLineItem.objects.bulk_update(
        query,
        (
            "cancellation_status",
            "status",
            "updated_date_c",
        ),
    )

    call_cancel_order(orderLineItemIds)


def createUserShopeeV3(usrShopee, csrfToken, spcF, spcSi) -> str:
    """ Cria um usuário UserShopee usando a V3 da API.
    :param usrShopee: Os dados crus do usuário.
    :param csrfToken: O token da request.
    :param spcF: O spcF da request.
    :param spcSi: O spcSi da request.
    
    :returns: O texto da resposta da request. """

    usrShopeeDict = usrShopee.__dict__
    usrShopeeDict.pop("_state", None)
    bodyToSend = {
        "userShopee": usrShopeeDict,
        "csrfToken": csrfToken,
        "spcF": spcF,
        "spcSi": spcSi,
    }
    bodyToSend = json.dumps(bodyToSend)
    if usrShopee.account_type == "G":
        sqsUrl = settings.REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE
        apiKey = settings.REST_GATEWAY_CREATE_USERSHOPEE_GOOGLE_ORDER_KEY
    else:
        sqsUrl = settings.REST_GATEWAY_CREATE_USERSHPOPEE_V3
        apiKey = settings.REST_GATEWAY_CREATE_USERSHOPEE_V3_ORDER_KEY

    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    print("response")
    print(response)
    print("response.text")
    print(response.text)
    print("response.status_copde")
    print(response.status_code)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 301:
        raise DropShopeeProxyError(response.text)
    else:
        raise Exception(response.text)


def sendGoogleSms(usrShopee, csrfToken, spcF, spcSi, spcEc, spcU) -> str:
    """ Envia um SMS de confirmação da Google.
    :param usrShopee: Os dados crus do usuário.
    :param csrfToken: O token da request.
    :param spcF: O spcF da request.
    :param spcSi: O spcSi da request.
    :param spcEc: O spcEc da request.
    :param spcU: O spcU da request.
    
    :returns: O texto da resposta da request. """

    print("[sendGoogleSms]")
    usrShopeeRaw = copy(usrShopee)
    usrShopeeDict = usrShopeeRaw.__dict__
    usrShopeeDict.pop("_state", None)
    usrShopeeDict.pop("creation_request_date", None)
    usrShopeeDict.pop("last_purchase_date", None)
    usrShopeeDict.pop("last_free_shipping_purchase", None)
    usrShopeeDict.pop("last_purchase", None)
    bodyToSend = {
        "userShopee": usrShopeeDict,
        "csrfToken": csrfToken,
        "spcF": spcF,
        "spcSi": spcSi,
        "spcEc": spcEc,
        "spcU": spcU,
    }
    bodyToSend = json.dumps(bodyToSend)
    print("RTEADAS ", bodyToSend)

    sqsUrl = settings.REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE
    apiKey = settings.REST_GATEWAY_CREATE_USERSHOPEE_EDITPHONE_ORDER_KEY

    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    print("response")
    print(response)
    print("response.text")
    print(response.text)
    print("response.status_copde")
    print(response.status_code)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 301:
        raise DropShopeeProxyError(response.text)
    else:
        raise Exception(response.text)


def validateUserVendorApiUpdateLmbd(usrShopee) -> bool:
    """ Valida o UserVendor pela API.
    :param usrShopee: Os dados do UserShopee.
    
    :returns: Verdadeiro se o código de status da resposta for 200. """

    usrShopeeRaw = copy(usrShopee)
    usrShopeeDict = usrShopeeRaw.__dict__
    usrShopeeDict.pop("_state", None)
    usrShopeeDict.pop("creation_request_date", None)
    usrShopeeDict.pop("last_purchase_date", None)
    usrShopeeDict.pop("last_free_shipping_purchase", None)
    usrShopeeDict.pop("last_purchase", None)
    bodyToSend = {"userShopee": usrShopeeDict}
    print(bodyToSend)
    sqsUrl = settings.REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE
    apiKey = settings.REST_GATEWAY_CREATE_VALIDATEUSERSHOPEE_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    if response.status_code == 200:
        responseJson = response.json()
        if responseJson.get("statusCode") == 200:
            return True
        elif responseJson.get("statusCode") == 301:
            raise DropShopeeUserBannedError(responseJson.get("body"))
        elif responseJson.get("statusCode") == 302:
            raise DropShopeeProxyError(responseJson.get("body"))
        else:
            raise Exception(responseJson.get("body"))
    else:
        raise Exception(response.text)


def resendSmsOptCode(jsonData) -> str:
    """ Reenvia o SMS opt.
    :param jsonData: Os dados JSON.
    
    :returns: O texto da resposta da request. """

    bodyToSend = {"data": jsonData}
    lmbdUrl = settings.REST_GATEWAY_CREATE_RESENDSMSOPT
    apiKey = settings.REST_GATEWAY_CREATE_RESENDSMSOPT_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }

    print("Resend body: ", bodyToSend)
    response = requests.post(lmbdUrl, json=bodyToSend, headers=header, timeout=50)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(response.text)

def generateCsvReport(data) -> str:
    """ Gera um relatório em formato CSV.
    :param data: Os dados do relatório.
    
    :returns: O texto da resposta da request. """

    bodyToSend = data
    lmbdUrl = settings.REST_GATEWAY_GENERATE_REPORT
    apiKey = settings.REST_GATEWAY_GENERATE_REPORT_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }

    print("Resend body: ", bodyToSend)
    response = requests.post(lmbdUrl, json=bodyToSend, headers=header, timeout=50)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(response.text)


def validateSmsV3(shopeeUser, csrftoken, spc_f, spc_si, spc_ec, spc_u, sms_code) -> Any:
    """ Valida o SMS pela V3 da API.
    :param csrfToken: O token da request.
    :param spc_f: O spcF da request.
    :param spc_si: O spcSi da request.
    :param spc_ec: O spcEc da request.
    :param spc_u: O spcU da request.
    :param sms_code: O código SMS para validar.

    :returns: A resposta da request em formato JSON. """

    usrShopeeDict = shopeeUser.__dict__
    usrShopeeDict.pop("_state", None)
    bodyToSend = {
        "userShopee": usrShopeeDict,
        "csrftoken": csrftoken,
        "spc_f": spc_f,
        "spc_si": spc_si,
        "spc_ec": spc_ec,
        "spc_u": spc_u,
        "otpToken": sms_code,
    }
    sqsUrl = settings.REST_GATEWAY_SECONDPART_CREATE_USERSHPOPEE_V3
    apiKey = settings.REST_GATEWAY_SECONDPART_CREATE_USERSHOPEE_V3_ORDER_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(response.text)


def validateSmsGoogle(
    shopeeUser, csrftoken, spc_f, spc_si, spc_ec, spc_u, seed, phone, sms_code
) -> str:
    """ Valida o SMS da Google.
    :param csrfToken: O token da request.
    :param spc_f: O spcF da request.
    :param spc_si: O spcSi da request.
    :param spc_ec: O spcEc da request.
    :param spc_u: O spcU da request.
    :param seed: A seed.
    :param phone: O número de telefone.
    :param sms_code: O código SMS para validar.

    :returns: O texto da resposta da request. """

    usrShopeeDict = shopeeUser.__dict__
    usrShopeeDict.pop("creation_request_date", None)
    usrShopeeDict.pop("last_purchase_date", None)
    usrShopeeDict.pop("last_free_shipping_purchase", None)
    usrShopeeDict.pop("last_purchase", None)
    usrShopeeDict.pop("_state", None)
    print("usrShopeeDict: ", usrShopeeDict)
    bodyToSend = {
        "userShopee": usrShopeeDict,
        "csrftoken": csrftoken,
        "spc_f": spc_f,
        "spc_si": spc_si,
        "spc_ec": spc_ec,
        "spc_u": spc_u,
        "otpSeed": seed,
        "phone": phone,
        "otpToken": sms_code,
    }
    sqsUrl = settings.REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE
    apiKey = settings.REST_GATEWAY_CREATE_USERSHOPEE_SECONDGOOGLE_ORDER_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)

    print("POST DADO", response.text)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(response.text)


def createShopifyWebhooks(userShop) -> None:
    """ Cria Webhooks da Shopify.
    :param userShop: Os dados do UserShop. """

    bodyToSend = {"userId": userShop.user.id}
    sqsUrl = settings.REST_GATEWAY_CREATE_WEBHOOKS
    apiKey = settings.REST_GATEWAY_CREATE_WEBHOOKS_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    print("response")
    print(response)
    print("response.text")
    print(response.text)
    print("response.status_copde")
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.text)


def deleteShopifyWebhooks(userShop) -> None:
    """ Deleta Webhooks da Shopfiy.
    :param userShop: Os dados do UserShop. """

    bodyToSend = {"userId": userShop.user.id}
    sqsUrl = settings.REST_GATEWAY_DELETE_WEBHOOKS
    apiKey = settings.REST_GATEWAY_DELETE_WEBHOOKS_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    print("response")
    print(response)
    print("response.text")
    print(response.text)
    print("response.status_copde")
    print(response.status_code)


def manualRetryBillingPercentage(userId, percentagePayId) -> requests.Response:
    """ Tenta novamente a procentagem de cobrança.
    :param userId: O ID do usuário.
    :param percentagePayId: O ID do percentagePay. """

    bodyToSend = {"userId": userId, "percentagePayId": percentagePayId}
    sqsUrl = settings.REST_GATEWAY_MANUAL_RETRY_PERCENTAGE
    apiKey = settings.REST_GATEWAY_MANUAL_RETRY_PERCENTAGE_API_KEY
    header = {
        "accept-encoding": "gzip;q=1.0m,deflate;q=0.6,identity;q=0.3",
        "content-type": "application/json",
        "x-api-key": apiKey,
    }
    response = requests.post(sqsUrl, json=bodyToSend, headers=header, timeout=50)
    return response


def strConverter(o) -> str:
    """ Converte um objeto para string. """

    if isinstance(o, datetime.datetime):
        return o.__str__()
