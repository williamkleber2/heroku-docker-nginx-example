from django.conf import settings
from typing import Final, List, Mapping, Optional
import math
import random
import calendar
import operator
import functools
import collections
from django.db.models import Count
from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest as BadRequest,
    HttpResponseNotAllowed as MethodNotAllowed,
    HttpResponseRedirect
)
from django.http.response import HttpResponseNotAllowed, HttpResponseNotFound
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from shopee.models import *
from shopee.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
import requests
from urllib.parse import urlparse
import json
from shopeeApi.shopifyConnection import *
from shopeeApi.lmbdFnctApiCall import *
from django.db.models.signals import post_save, pre_save
from shopee.signals import postSaveUserShop, preSaveUserShop, postSaveUserBillingData
from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone
from shopeeApi.stripeApi import *
from django.views.decorators.csrf import csrf_exempt
import stripe
import uuid
from sentry_sdk import capture_exception, capture_message
from django.utils.decorators import decorator_from_middleware
from datetime import datetime, timedelta
from datetime import timezone as dtTimezone
import base64
from shopee.middlewares import have_plan
from django_cpf_cnpj import validators
import re
import typing as t
from functools import wraps
from shopee.views import sql
from functools import wraps

# A product URL in Shopee has this template:
#   - https://shopee.com.br/{product_name}-i.{shopid}.{itemid}
#       NOTE `product_name` doesn't come in percent encoding.
#   - https://shopee.com.br/product/{shopid}/{itemid}
#
# The RegEx below has an "assertion" (using literals) if the string
# starts with `shopee.com.br` and "checks" if `shopid` and `itemid`
# exist, if they exist, put them inside a capture group, otherwise, the 
# string is invalid.
#
REGEX_SHOPEE_URL = re.compile(r"^.*shopee\.com\.br/(?:product/(\d+)/(\d+)|.*-i\.(\d+)\.(\d+)\??)")
# A product URL in AliExpress has this template:
#   - https://pt.aliexpress.com/item/{product_id}.html
#
# The RegEx below only asserts if regex has an `product_id`.
#
REGEX_ALIEXPRESS_URL = re.compile(r"^.*aliexpress\.com/item/(\d+).html.*")

SUPPORTED_VENDORS = ("aliexpress", "shopee",)

## Add signals
post_save.connect(postSaveUserBillingData, sender=UserBillingData)
post_save.connect(postSaveUserShop, sender=UserShop)
pre_save.connect(preSaveUserShop, sender=UserShop)


def extract_product_data(url: str, /, vendor: str) -> t.Optional[t.Tuple[str, ...]]:
    """ Extrai os dados do produto.
    :param url: O url do produto.
    :param vendor: O vendor do produto.
    
    :returns: A extração. """

    pattern = REGEX_SHOPEE_URL

    if vendor == "ali":
        pattern = REGEX_ALIEXPRESS_URL

    if match := pattern.match(url):
        match = match.groups()
        return (*filter(bool, match),)


def cache_request(f) -> Any:
    """ O cache da request.
    :param f: A função. """

    cache = {}

    @wraps(f)
    def decorator(req, *args, **kwargs) -> Dict[str, Any]:
        """ Pega o cache. """

        body = getattr(req, req.method, ...)
        if body is not ...:
            if isinstance(body, Mapping):
                body = dict(body.items())
                del body["csrfmiddlewaretoken"]

                body = tuple(body.values())

        data = (
            req.path,
            req.method,
            body,
        )

        if data not in cache:
            cache[data] = f(req, *args, **kwargs)

        return cache[data]
    return decorator


def getShopeeHeader(url) -> Dict[str, str]:
    """ Pega os headers da Shopee.
    :param url: O URL do referer.
    
    :returns: O dicionário dos headers. """

    shopeeHeader = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "referer": url,
        "if-none-match-": "55b03-42b689ea8b5402c76ce6539bb6ff8013",
    }
    return shopeeHeader


@login_required(login_url="login")
def index(request) -> HttpResponse:
    """ Renderiza a página da dashboard.
    :param request: O objeto da request. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == 'canceled' or not working_admin:
        return redirect('shopifyInfo')

    return render(request, 'dashboard.html', {'nbar': 'home', 'subscription_status': subscriptionStatus,
                                              'percentagePay_status': percentagePayStatus,
                                              'daysUntilAccountBlock': daysUntilAccountBlock,
                                              'working_admin': working_admin})
@login_required(login_url='login')
@csrf_exempt
def userShopeeCredentials(request) -> JsonResponse:
    """  Pega as credenciais do UserShopee.
    :param request: O objeto da request.

    :returns: A resposta da request em JSON. """

    user_shop = UserShop.objects.get(user=request.user)
    email = request.POST.get('email')
    user_shopee = UserShopee.objects.get(email=email, user_shop=user_shop)
    spc_ec = user_shopee.spc_ec

    if user_shopee.account_type != 'G':
        response = loginInfoUserShopee(user_shopee)
        spc_ec = response['SPC_EC']
    
    return JsonResponse({"SPC_EC": spc_ec, 
                         "SPC_F": user_shopee.spc_f, 
                         "proxy": user_shopee.proxy,
                         "port": user_shopee.port,
                         "proxy_login": user_shopee.proxy_login,
                         "proxy_password": user_shopee.proxy_password,
                        },
                         safe=False)

@have_plan
@login_required(login_url='login')
def reactivateGoogleAccount(request) -> HttpResponseRedirect:
    """ Reativa a conta do Google.
    :param request: O objeto da request.
    
    :returns: Um redirect pra vendorUsers/ """

    print("[reactivateGoogleAccount]")
    spc_ec = request.POST.get('spc_ec')
    email = request.POST.get('email')
    user_shop = UserShop.objects.get(user=request.user)
    usr_shopee = UserShopee.objects.get(email=email, user_shop=user_shop)

    if len(spc_ec) < 8:
        capture_message('A reativação da conta Google falhou. Email: ' + str(email))
        messages.error(request, 'A reativação falhou, tente novamente.')
        return redirect('vendorUsers')

    usr_shopee.spc_ec = spc_ec
    usr_shopee.deactivate_status = ""
    usr_shopee.activated = True
    usr_shopee.save()

    return redirect('vendorUsers')

@have_plan
@login_required(login_url="login")
def vendorUsers(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a página do vendorUsers.
    :param request: O objeto da request.
    
    :returns: A resposta da request em JSON. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    try:
        userShop = UserShop.objects.get(user=user)
        shopeeUsers = UserShopee.objects.filter(user_shop=userShop)
        hasAliUser = UserShopee.objects.filter(vendor='ali', user_shop=userShop).exists()
    except UserShop.DoesNotExist:
        shopeeUsers = []
        hasAliUser = False

    counter_seconds = settings.VENDORUSERCREATE_SMS_COUNTER

    return render(
        request,
        "shopeeUsers.html",
        {
            "nbar": "shopeeUsers",
            "ctype": "google",
            "shopeeUsers": shopeeUsers,
            "subscription_status": subscriptionStatus,
            "notionUrl": settings.NOTION_VENDOR_USERS_URL,
            "working_admin": working_admin,
            "counter_seconds": counter_seconds,
            "hasAliUser": hasAliUser
        },
    )


@login_required(login_url="login")
def associateUserVendorToShop(request) -> JsonResponse:
    """ Associa o UserVendor ao Shop.
    :param request: O objeto da request.
    
    :returns: A resposta da request em JSON. """

    userShopeeIds = request.POST.get("userShopeeIds")
    userShopeeIdsLst = json.loads(userShopeeIds)
    userShopName = request.POST.get("userShopName")
    userShops = UserShop.objects.filter(shopify_name=userShopName)

    if not userShops:
        return JsonResponse(
            {"status_code": "404", "message": "Não existe loja com esse nome"},
            safe=False,
        )

    userShop = userShops[0]

    usersFromDB = UserShopee.objects.filter(id__in=userShopeeIdsLst)
    updatedUsers = []

    for userShopee in usersFromDB:
        userShopee.user_shop = userShop
        updatedUsers.append(userShopee)

    UserShopee.objects.bulk_update(updatedUsers, ["user_shop_id"])
    return JsonResponse(
        {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
    )


@login_required(login_url="login")
@transaction.atomic
def editUserVendorWithoutShop(request) -> JsonResponse:
    """ Edita um UserVendor sem o Shop.
    :param request: O objeto da request.
    
    :returns: A resposta da request em JSON. """

    if request.method == "POST":
        sid = transaction.savepoint()
        shopeeUser = UserShopee.objects.get(email=request.POST.get("email"))
        shopeeUser.password = request.POST.get("password")
        shopeeUser.proxy = request.POST.get("proxy")
        shopeeUser.port = request.POST.get("port")
        shopeeUser.proxy_login = request.POST.get("proxy_login")
        shopeeUser.proxy_password = request.POST.get("proxy_password")
        shopeeUser.captcha_signature = request.POST.get("captcha_signature")
        shopeeUser.sms_api_key = request.POST.get("sms_api_key")
        shopeeUser.created_status = "BC"
        shopeeUser.creation_request_date = timezone.now()
        try:
            shopeeUser.save()
            createUserShopee(shopeeUser)
            transaction.savepoint_commit(sid)
            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
            )
        except Exception as e:
            transaction.savepoint_rollback(sid)
            if e.__cause__ and e.__cause__.pgcode == "23505":
                return JsonResponse(
                    {
                        "status_code": "404",
                        "message": "Já existe um usuário com esse email",
                    },
                    safe=False,
                )
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)
    return redirect("vendorUsersWithoutShop")


@login_required(login_url="login")
def vendorUserJson(request, pk) -> JsonResponse:
    """ Carrega o VendoUser em JSON.
    :param request: O objeto da request.
    :param pk: A primary key do VendorUser.

    :returns: A resposta da request em JSON. """

    shopeeUsers = UserShopee.objects.filter(id=pk).values(
        "id",
        "email",
        "phone",
        "password",
        "proxy",
        "port",
        "proxy_login",
        "proxy_password",
        "created_status",
        "captcha_signature",
        "sms_api_key",
    )
    data = list(shopeeUsers)
    response = {"data": data}

    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorUserValidateEmail(request, pk) -> JsonResponse:
    """ Valida o VendoUser.
    :param request: O objeto da request.
    :param pk: A primary key do VendorUser.

    :returns: A resposta da request em JSON. """

    shopeeUser = UserShopee.objects.get(id=pk)
    try:
        validateInfos = validateUserVendorApiUpdateLmbd(shopeeUser)
        if validateInfos:
            shopeeUser.created_status = "C"
            shopeeUser.save()
            return JsonResponse(
                {"status_code": "200", "message": "Validado com sucesso"}, safe=False
            )
    except DropShopeeProxyError as e:
        return JsonResponse({"message": str(e), "status_code": "302"}, safe=False)
    except Exception as e:
        capture_exception(e)
        return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)


@login_required(login_url="login")
def shopeeUserErrors(request) -> HttpResponse:
    """ Renderiza os erros do ShopeeUser.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de erro. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    userShop = UserShop.objects.get(user=user)
    shopeeUserErrors = UserShopeeError.objects.filter(user_shopee__user_shop=userShop)
    return render(
        request,
        "shopeeUserErrors.html",
        {
            "nbar": "shopeeUserErrors",
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
        },
    )


@login_required(login_url="login")
def vendorUserEdit(request, pk) -> JsonResponse:
    """ Edita o VendoUser.
    :param request: O objeto da request.
    :param pk: A primary key do VendorUser.

    :returns: A resposta da request em JSON. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)

    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    user_shop = UserShop.objects.get(user=user)
    shopeeUsers = UserShopee.objects.filter(pk=pk, user_shop=user_shop)

    if shopeeUsers.exists():
        shopeeUser = shopeeUsers.first()
    else:
        return redirect("vendorUsers")
    
    if shopeeUser.deactivate_status == "BA":
        return redirect("vendorUsers")

    is_being_created = shopeeUser.created_status == "BC"
    if is_being_created:
        messages.warning(request, "O usuário ainda está sendo criado...")
        return redirect("vendorUsers")
        
    if request.method == "POST":
        try:
            shopeeUser.user_shop = UserShop.objects.get(user=user)
            shopeeUser.email = request.POST.get("email")
            shopeeUser.phone = request.POST.get("phone")
            shopeeUser.password = request.POST.get("password")
            shopeeUser.proxy = request.POST.get("proxy")
            shopeeUser.port = request.POST.get("port")
            shopeeUser.proxy_login = request.POST.get("proxy_login")
            shopeeUser.proxy_password = request.POST.get("proxy_password")
            shopeeUser.activated = (
                True if request.POST.get("activated") == "true" else False
            )

            if request.POST.get("activatedWasChangedManually") == "true":
                if shopeeUser.activated:
                    shopeeUser.deactivate_status = ""
                    shopeeUser.last_free_shipping_purchase = None
                    shopeeUser.last_purchase = None
                else:
                    shopeeUser.deactivate_status = "M"

            successMsg = "Salvo com sucesso"
            if shopeeUser.activated:
                try:
                    validateInfos = validateUserVendorApiUpdateLmbd(shopeeUser)
                except DropShopeeUserBannedError as e:
                    successMsg = "Sua conta foi banida"
                    validateInfos = True

                    shopeeUser.activated = False
                    shopeeUser.deactivate_status = "BA"
            else:
                validateInfos = True

            if validateInfos:
                if shopeeUser.created_status == "EAR":
                    shopeeUser.created_status = "C"
                shopeeUser.save()
                return JsonResponse(
                    {"status_code": "200", "message": successMsg}, safe=False
                )
        except DropShopeeProxyError as e:
            return JsonResponse({"message": str(e), "status_code": "302"}, safe=False)
        except IntegrityError:
            return JsonResponse({"message": "Esse usuário já existe.", "status_code": "302"})
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)

    return render(
        request,
        "shopeeUserEdit.html",
        {
            "nbar": "shopeeUsers",
            "ctype": "google",
            "userShopee": shopeeUser,
            "userShopee_pk": pk,
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
        },
    )


@login_required(login_url="login")
def charges(request) -> HttpResponse:
    """ Renderiza a tela de cobranças.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de cobranças. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    form = UserShopUserForm()
    need_billing_data = False
    try:
        userInfo = UserInfo.objects.get(user=user)
        percentage = userInfo.percentage
    except UserInfo.DoesNotExist:
        percentage = ""

    customer = Customer.objects.filter(user=user)
    if customer.exists():
        customer = customer.first()
        active_subscriptions = get_active_subscriptions(customer)
        subscription = active_subscriptions[0]
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id, 
            type="card",
        )['data']
        charges = stripe.Charge.list(customer=customer.id)['data']
    else:
        charges = []
        payment_methods = []
        subscription = {}

    try:
        user_bill_data = UserBillingData.objects.get(user=user)
    except UserBillingData.DoesNotExist:
        user_bill_data = UserBillingData.objects.none()
        need_billing_data = True
        
    if UserShop.objects.filter(user=user).exists():
        shopifyInfo = UserShop.objects.get(user=user)
    else:
        shopifyInfo = None
        
    return render(request, 'charges.html', {'nbar': 'shopifyInfo',
                                            'shopifyInfo': shopifyInfo,
                                            'form': form,
                                            'need_billing_data': need_billing_data,
                                            'user_bill_data': user_bill_data,
                                            'subscription_status': subscriptionStatus,
                                            'subscription': subscription,
                                            'payment_methods': payment_methods,
                                            'charges': charges,
                                            'percentagePay_status': percentagePayStatus,
                                            'daysUntilAccountBlock': daysUntilAccountBlock,
                                            'working_admin': working_admin,
                                            'percentage': percentage})
def get_doc_validator(doc_type) -> Any:
    """ Pega o validador do doc.
    :param doc_type: O tipo do doc. """

    try:
        return getattr(validators, 'is_valid_' + doc_type)
    except TypeError:
        return lambda x: False

def is_biiling_data_valid(data) -> Tuple[bool, str]:
    """ Verifica se os dados da cobrança são validos
    :param data: Os dados.
    
    :returns: Uma resposta em tupla, contendo verdadeiro ou falso e
    uma mensagem explicativa. """

    print(data)
    
    is_doc_type_valid = data.get('doc_type') in ('cpf', 'cnpj')
    is_doc_valid = get_doc_validator(data.get('doc_type'))(data.get('document'))
    is_name_valid = len(data['name']) >= 3
    is_zipcode_valid = len(data['zipcode']) > 8
    is_phone_valid = len(data['phone']) > 8
    is_state_valid = data.get('state') is not None
    is_city_valid = len(data['city']) > 2
    is_address_valid = len(data['address']) > 2
    is_address_number_valid = len(data['addressNumber']) > 0


    if not all([is_doc_type_valid,is_doc_valid]):
        return False, "Tipo e/ou código do documento inválidos."     

    if not all([is_name_valid]):
        return False, "Nome/Razão Social inválido."     

    if not all([is_zipcode_valid,is_state_valid,is_city_valid,is_address_valid,is_address_number_valid]):
        return False, "Verifique as informações de endereço e tente novamente."     

    if not all([is_phone_valid]):
        return False, "Número de telefone inválido."     
        
    return True, "ok"


@login_required(login_url='login')
def billing_data(request) -> JsonResponse:
    """ Pega os dados de cobrança.
    :param request: O objeto da request.
    
    :returns: Mensagem de sucesso ou erro em JSON. """

    user = request.user
    data = request.POST
    
    is_valid, msg = is_biiling_data_valid(data)

    if not is_valid:
        return JsonResponse({'error': msg})

    user_bill_data = {
            "doc_type": data.get('doc_type'),
            "name": data.get('name'),
            "address": data.get('address'),
            "address_number": data.get('addressNumber'),
            "address2": data.get('address2'),
            "city": data.get('city'),
            "state": data.get('state'),
            "phone": data.get('phone'),
            "zipcode": data.get('zipcode'),
            }

    user_bill_data[data.get('doc_type')] = data.get('document')    
    UserBillingData.objects.update_or_create(user=user, defaults=user_bill_data)

    return JsonResponse({'success': 'Dados de Faturamento atualizados com sucesso.'})

@csrf_exempt
@login_required(login_url='login')
def cancel_subscription(request) -> JsonResponse:
    """ Cancela a inscrição.
    :param request: O objeto da request. """
    
    if request.method == 'POST':
        user = request.user
        user.profile.last_cancel_request_datetime = timezone.now()
        user.profile.save()

        user_bill_data = UserBillingData.objects.get(user=user)
        response = requests.post(settings.CANCEL_SLACK_WEBHOOK, json={
            "username": "Droplinkfy",
            "icon_url": settings.CANCEL_SLACK_WEBHOOK_ICON,
            "text": f"""*[NOTIFICAÇÃO DE CANCELAMENTO]*\nO usuário {user.first_name} {user.last_name} ({user.email}) acabou de solicitar o cancelamento de sua assinatura.
            Telefone: {user_bill_data.phone}"""
        })

        if response.status_code != 200:
            return JsonResponse({'error': "Algum erro ocorreu ao solicitar o cancelamento de sua assinatura."})
    
        return JsonResponse({'success': settings.CANCEL_SUBSCRIPTION_MESSAGE})
    


@login_required(login_url="login")
def percentagePaysJson(request) -> JsonResponse:
    """ Pega as PercentagePays.
    :param request: O objeto da request.
    
    :returns: Os dados em JSON. """
    
    try:
        user = request.user
        percentagePayRecords = (
            PercentagePay.objects.filter(customer__user=user)
            .annotate(orders_count=Count("percentagePayOrderss"))
            .values("status", "start_date", "end_date", "value", "orders_count", "id")
        )
        data = list(percentagePayRecords)
        response = {"data": data}
        return JsonResponse(response, safe=False)
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()

@have_plan
@login_required(login_url='login')
def shopifyInfo(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a página de informações da Shopify.
    :param request: O objeto da request.
    
    :returns: A renderização da página ou um redirect. """

    notionUrl = settings.NOTION_SHOPIFY_URL
    user = request.user
    if not user.is_superuser:
        redirectName = verifyCustomerExists(request)
        if redirectName != "shopifyInfo":
            return redirect(redirectName)
    subscriptionStatus = getSubscriptionStatus(user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    form = UserShopUserForm()
    if UserShop.objects.filter(user=user).exists():
        shopifyInfo = UserShop.objects.get(user=user)
        userInfo = UserInfo.objects.get(user=user)
    else:
        shopifyInfo = None
        userInfo = None
    return render(
        request,
        "shopifyInfo.html",
        {
            "nbar": "shopifyInfo",
            "shopifyInfo": shopifyInfo,
            "userInfo": userInfo,
            "form": form,
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
            "notionUrl": notionUrl,
        },
    )


@login_required(login_url="login")
def shopifyInfoUpdate(request) -> JsonResponse:
    """ Atualiza as informações da Shopify.
    :param request: O objeto da request.
    
    :returns: A resposta do estado da request. """

    try:
        user = request.user
        if UserShop.objects.filter(user=user).exists():
            shopifyInfo = UserShop.objects.get(user=user)
        else:
            shopifyInfo = None
        if request.method == "POST":
            checkout = request.POST.get("checkout")
            shopifyName = request.POST.get("shopify_name")
            o = urlparse(shopifyName)
            if o.scheme:
                shopifyName = o.netloc
                if shopifyName.startswith("www."):
                    shopifyName = o.netloc[4:]
                else:
                    shopifyName = o.netloc
            else:
                shopifyName = o.path
                if shopifyName.startswith("www."):
                    shopifyName = o.path[4:]
                else:
                    shopifyName = o.path

            if shopifyName.endswith("/"):
                shopifyName = shopifyName[:-1]

            shopifyKey = request.POST.get("shopify_key")
            shopifySharedSecret = request.POST.get("shopify_shared_secret")
            trackingUrl = request.POST.get("tracking_url")
            working = request.POST.get("working") == "true"
            freeShipping = request.POST.get("free_shipping") == "true"
            automaticUpsell = request.POST.get("automatic_upsell") == "true"
            userShop = shopifyInfo if shopifyInfo else UserShop()
            userShop.user = user
            userShop.checkout = checkout
            if not shopifyInfo:
                userShop.shopify_name = shopifyName
            userShop.shopify_key = shopifyKey
            userShop.shopify_shared_secret = shopifySharedSecret
            userShop.working = working
            userShop.free_shipping = freeShipping
            userShop.automatic_upsell = automaticUpsell
            userShop.tracking_url = trackingUrl
            user_info = UserInfo.objects.get(user=request.user)
            user_info.order_memo = request.POST.get("order_memo")
            user_info.save()

            if working:
                shopifyIsValid = verifyShopifyDomaindAndKey(userShop)
                if not shopifyIsValid:
                    return JsonResponse(
                        {
                            "status_code": "404",
                            "message": "Senha e/ou domínio da sua loja estão incorretos",
                        },
                        safe=False,
                    )
            success, message = checkShopifyPermissions(userShop)
            if not success:
                return JsonResponse(
                    {"status_code": "404", "message": message}, safe=False
                )
            userShop.save()
        return JsonResponse(
            {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
        )
    except Exception as e:
        capture_exception(e)
        print(e)


@login_required(login_url="login")
def updateUserNewsNotification(request) -> JsonResponse:
    """ Atualiza as notificações de novidades para o usuário.
    :param request: O objeto da request.
    
    :returns: A resposta do estado da request. """

    user = request.user
    news_id = request.POST.get("news_id")

    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist as e:
        capture_exception(e)
        return JsonResponse({"status_code": 404})

    try:
        result = UserNewsNotification.objects.get(news__id=news_id, user=user)
    except UserNewsNotification.DoesNotExist:
        notification = UserNewsNotification(user=user, news=news)
        notification.save()
    else:
        return JsonResponse(
            {
                "status_code": "400",
            }
        )

    return JsonResponse({"status_code": "200",})
 
@have_plan
@login_required(login_url='login')
def shopifyProducts(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a tela de produtos da Shopify.
    :param request: O objeto da request.
    
    :returns: A renderização da página, ou um redirect para a tela de informações. """

    notionUrl = settings.NOTION_PRODUCT_URL
    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    try:
        userShop = UserShop.objects.get(user=user)
        available_syncs = (
            settings.LIMIT_SYNC_PRODUCTS_REQUEST - userShop.products_sync_requests
        )
        if userShop.last_products_sync_date < datetime.today().date():
            available_syncs = settings.LIMIT_SYNC_PRODUCTS_REQUEST
    except UserShop.DoesNotExist:
        available_syncs = 0

    return render(
        request,
        "shopifyProducts.html",
        {
            "nbar": "shopifyProducts",
            "available_syncs": available_syncs,
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
            "notionUrl": notionUrl,
        },
    )


@login_required(login_url="login")
def vendorSyncProducts(request) -> JsonResponse:
    """ Sincroniza os produtos do vendor.
    :param request: O objeto da request.
    
    :returns: O estado da resposta do request. """

    user = request.user
    userShop = UserShop.objects.get(user=user)
    if userShop.last_products_sync_date < datetime.today().date():
        userShop.products_sync_requests = 1
    else:
        userShop.products_sync_requests = userShop.products_sync_requests + 1

    if userShop.products_sync_requests > settings.LIMIT_SYNC_PRODUCTS_REQUEST:
        return JsonResponse(
            {
                "status_code": "404",
                "message": "Excedeu o número máximo de sincronizações para hoje",
            },
            safe=False,
        )
    available_syncs = (
        settings.LIMIT_SYNC_PRODUCTS_REQUEST - userShop.products_sync_requests
    )
    userShop.last_products_sync_date = datetime.today().date()
    if userShop.working:
        shopifyIsValid = verifyShopifyDomaindAndKey(userShop)
        if not shopifyIsValid:
            return JsonResponse(
                {
                    "status_code": "404",
                    "message": "Senha e/ou domínio da sua loja estão incorretos",
                },
                safe=False,
            )
    success, message = checkShopifyProductsPermission(userShop)
    if success:
        userShop.save()
        upsertShopifyProducts(userShop)
        return JsonResponse(
            {
                "status_code": "200",
                "message": "Sincronização em curso",
                "available_syncs": available_syncs,
            },
            safe=False,
        )
    else:
        return JsonResponse({"status_code": "404", "message": message}, safe=False)


@login_required(login_url="login")
def shopifyOrders(request, pk) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a tela de pedidos da Shopify.
    :param request: O objeto da request.
    :param pk: A primary key dos estados dos pedidos.
    
    :returns: A renderização da página com os pedidos, ou um redirect para a página de informações. """

    notionUrl = settings.NOTION_ORDER_URL
    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    htmlFile = "shopifyOrders_" + pk + ".html"
    return render(
        request,
        htmlFile,
        {
            "nbar": "orders",
            "status": pk,
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
            "notionUrl": notionUrl,
        },
    )


@login_required(login_url="login")
def vendorOrdersJson(request, pk) -> JsonResponse:
    """ Pega os pedidos do vendor.
    :param request: O objeto da request.
    :param pk: A primary key do status dos pedidos.
    
    :returns: Os pedidos em formato JSON. """

    user = request.user
    status = pk
    orders = sql.get_user_shop_orders_by_status(user.id, status)

    child_orders = []
    for order in orders:
        order = order.__dict__
        order['child'] = Order.objects.filter(parent_order=order.id)
        child_orders.append(order)

    response = {"data": child_orders}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorOrdersByPercentagePayJson(request, pk) -> JsonResponse:
    """ Pega os pedidos do  do vendor pela porcentagem de pagamento.
    :param request: O objeto da request.
    :param pk: A primary key do status dos pedidos.
    
    :returns: Os pedidos em formato JSON. """

    user = request.user
    shopeeOrders = Order.objects.filter(
        user_shop__user=user, percentage_pay_id=pk
    ).values("name", "dropshopee_created_date", "total_price")
    data = list(shopeeOrders)
    response = {"data": data}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorOrderLineItemsJson(request, pk) -> JsonResponse:
    """ Pega as OLIs do vendor.
    :param request: O objeto da request.
    :param pk: A primary key do status das OLIs.
    
    :returns: As OLIs em formato JSON. """
    
    orderId = pk
    shopeeOrderLineItems = OrderLineItem.objects.filter(order__id=orderId).values(
        "order",
        "product_variant__product_shopify__title",
        "product_variant__title",
        "quantity",
        "id",
    )
    data = list(shopeeOrderLineItems)
    response = {"data": data}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorOrderPurchaseLineItemsJson(request, pk) -> JsonResponse:
    """ Pega os OrderPurchaseLineItems do vendor.
    :param request: O objeto da request.
    :param pk: A primary key do status das OLIs.
    
    :returns: Os OrderPurchaseLineItems em formato JSON. """

    shopeeOrderPurchaseLineItems = OrderPurchaseLineItem.objects.filter(
        order_id=pk
    ).values(
        "user_shopee__email",
        "shopee_product_name",
        "shopee_product_variant",
        "purchase_date",
        "order_purchase__shipping_fee",
        "order_purchase__list_type",
        "order_purchase__tracking_number",
        "order_purchase__shopee_order_id",
        "order_purchase__canceled_status",
        "order_purchase__serial_number",
    )
    data = list(shopeeOrderPurchaseLineItems)
    response = {"data": data}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorUserErrorsJson(request, pk) -> JsonResponse:
    """ Pega os erros do usuário vendor.
    :param request: O objeto da request.
    :param pk: A primary key do ID do usuário.
    
    :returns: Os erros em formato JSON. """

    usershopeeErrors = UserShopeeError.objects.filter(user_shopee__id=pk).values(
        "user_shopee__email", "date", "message"
    )
    data = list(usershopeeErrors)
    response = {"data": data}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorProductsJson(request, variant_id: int) -> HttpResponse:
    """ Pega os produtos do vendor.
    :param request: O objeto da request.
    :param variant_id: O ID da variante dos produtos.
    
    :returns: Os produtos em formato JSON. """

    user = request.user

    shopeeProducts = (ProductShopee.objects
                        .filter(
                            product_variant=variant_id,
                            product_variant__product_shopify__user_shop__user=user,
                        )
                        .values(
                            "vendor",
                            "shopee_url",
                            "quantity",
                            "option_name",
                            "id",
                        ))

    data = list(shopeeProducts)
    response = {"data": data}

    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def vendorProductDeleteJson(request) -> HttpResponse:
    """ Deleta um produto do vendor.
    :param request: O objeto da request.
    
    :returns: A renderização da dashboard. """

    user = request.user

    if request.method == "POST":
        productShopeeId = request.POST.get("shopeeProductId")

        try:
            ProductShopee.objects.get(
                pk=productShopeeId,
                product_variant__product_shopify__user_shop__user=user,
            ).delete()
        except ProductShopee.DoesNotExist:
            return HttpResponseNotFound("O produto já foi excluído ou não existe.")

    return render(request, "dashboard.html")


@login_required(login_url="login")
def doneOrders(request) -> HttpResponse:
    """ Renderiza a tela de pedidos feitos.
    :param request: O objeto da request.
    
    :returns: A renderização da página de produtos. """

    user = request.user
    productShopify = Order.objects.filter(user_shop__user=user)
    return render(
        request,
        "shopifyProducts.html",
        {"nbar": "Order", "productShopify": productShopify},
    )


def verifyCustomerExists(request) -> str:
    """ Verifica se o customer existe.
    :param request: O objeto da request.
    
    :returns: O nome da página na qual ele existe. """

    try:
        user = request.user
        if True:
            return "shopifyInfo"
        customers = Customer.objects.filter(user=user)
        subscriptions = Subscription.objects.select_related("customer").filter(
            customer__in=customers
        )
        subscriptionsActive = subscriptions.filter(status="active")
        if subscriptionsActive:
            customer = subscriptionsActive[0].customer
        else:
            customer = subscriptions[0].customer
        if customers:
            taxIds = getCustomerTaxIds(customer)
            if taxIds:
                return "shopifyInfo"
            else:
                return "checkoutCustomerTax"
        else:
            return "checkoutSetup"
    except stripe.error.StripeError as e:
        capture_exception(e)
        messages.error(request, str(e))
    except Exception as e:
        capture_exception(e)


def loginPage(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a tela de login.
    :param request: O objeto da request.
    
    :returns: A renderização da tela, ou um redirect para uma outra tela. """

    if request.user.is_authenticated:
        redirectName = verifyCustomerExists(request)
        return redirect(redirectName)
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                redirectName = verifyCustomerExists(request)
                return redirect(redirectName)
            else:
                messages.error(request, "Usuário ou Senha incorretos")

        context = {}
        return render(request, "auth-login-basic.html", context)

def registerPage(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Renderiza a tela de registração.
    :param request: O objeto da request.
    
    :returns: A renderização da tela, ou um redirect. """

    if request.user.is_authenticated:
        redirectName = verifyCustomerExists(request)
        return redirect(redirectName)
  
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        country_code = request.POST.get('country_code')
        dropshipping_xp_time = request.POST.get('dropshipping_xp_time')
        referral = request.POST.get('referral')
        dropshipping_xp_time = request.POST.get('dropshipping_xp_time')
        has_error = False
        
        if password != password2:
            messages.error(request, 'Erro: As senhas informadas são diferentes.') 
            has_error = True
        
        if len(full_name.split()) < 2:
            messages.error(request, 'Erro: Informe seu nome completo.') 
            has_error = True

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Erro: Já existe um usuário com esse email.') 
            has_error = True

        if len(phone) < 8:
            messages.error(request, 'Erro: Telefone inválido.') 
            has_error = True

        dropshipping_xp_time_keys = [x[0] for x in Profile.XpTimes.choices]
        if dropshipping_xp_time not in dropshipping_xp_time_keys:
            messages.error(request, 'Erro: Selecione seu tempo de experiência com Dropshipping para continuar.') 
            has_error = True

        if has_error:
            return render(request, 'auth-register.html', {})

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email, 
                    email=email, 
                    password=password,
                    first_name=full_name.split()[0],
                    last_name=' '.join(full_name.split()[1:]),
                )
                Profile.objects.create(
                    user=user, 
                    phone=phone, 
                    country_code=country_code, 
                    referral=referral, 
                    dropshipping_xp_time=dropshipping_xp_time
                )
                cleaned_phone = str(country_code) + ''.join(filter(str.isdigit, phone))
                customer = stripe.Customer.create(email=email, phone=cleaned_phone, name=full_name, metadata={ "xp_time": dropshipping_xp_time })
                Customer.objects.create(id=customer['id'], user=user, created=customer['created'], email=customer['email'])
        except IntegrityError as e:
            capture_exception(e)
            messages.error("Verifique se todos os dados estão corretos e tente novamente.")
            return render(request, 'auth-register.html', {})

        
        user = authenticate(request, username=email, password=password)
        login(request, user)

        return redirect('plans')

    context = {}

    return render(request, 'auth-register.html', context)


def logoutUser(request) -> HttpResponseRedirect:
    """ Desloga o usuário.
    :param request: O objeto da request.
    
    :returns: Um redirect para a página de login. """

    logout(request)
    return redirect("login")


def error_404(request, exception) -> HttpResponse:
    """ Renderiza a tela de erro 404.
    :param request: O objeto da request.
    :param exception: O erro.
    
    :returns: A renderização da página de erro. """

    data = {}
    return render(request, "error-404-1.html", data)


def error_500(request, *args, **argv) -> HttpResponse:
    """ Renderiza a tela de erro 500.
    :param request: O objeto da request.
    :param *args: Args.
    :param **argv: Kwargs.
    
    :returns: A renderização da página de erro. """

    return render(request, "error-500.html", status=500)


def error_403(request, exception) -> HttpResponse:
    """ Renderiza a tela de erro 403.
    :param request: O objeto da request.
    :param exception: O erro.
    
    :returns: A renderização da página de erro. """

    data = {}
    return render(request, "error-403.html", data)


def error_400(request, exception) -> HttpResponse:
    """ Renderiza a tela de erro 400.
    :param request: O objeto da request.
    :param exception: O erro.
    
    :returns: A renderização da página de erro. """

    data = {}
    return render(request, "error-400.html", data)


def getShopeeProducts(request) -> JsonResponse:
    """ Pega os produtos da Shopee.
    :param request: O objeto da request.
    
    :returns: Os produtos em formato JSON. """

    shopeeProducts = ProductShopee.objects.all()
    data = [product.to_dict_json() for product in shopeeProducts]
    response = {"data": data}
    return JsonResponse(response)


@login_required(login_url="login")
def shopifyProductsJson(request) -> JsonResponse:
    """ Pega os produtos da Shopify em JSON.
    :param request: O objeto da request.
    
    :returns: Retorna os produtos em formato JSON. """

    user = request.user
    shopifyProductVariants = (
        ProductVariant.objects.filter(product_shopify__user_shop__user=user)
        .annotate(Count("productVariantsShopee", distinct=True))
        .values(
            "productVariantsShopee__count",
            "product_shopify__title",
            "title",
            "sku",
            "price",
            "id",
            "gid",
            "price",
            "compare_at_price",
            "created_at",
            "updated_at",
            "is_processable",
        )
    )
    data = list(shopifyProductVariants)
    response = {"data": data}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def datatable(request) -> HttpResponse:
    """ Renderiza a página da tabela de dados.
    :param request: O objeto da request.
    
    :returns: A renderização da página. """

    return render(request, "datatable.html")


@login_required(login_url="login")
def vendorProductCreate(request) -> HttpResponse:
    """ Cria um produto pro vendor.
    :param request: O objeto da request.
    
    :returns: Renderiza a página do código de status da request. """

    if request.method != "POST":
        return HttpResponseNotAllowed(("POST",))

    user = request.user

    if not getWorkingAdmin(user):
        return redirect("shopifyInfo")

    subscriptionStatus = getSubscriptionStatus(user)
    if subscriptionStatus == "canceled":
        return redirect("shopifyInfo")

    data = json.loads(request.body)

    url = data["url"]
    vendor = data["vendor"]
    amount = data["amount"]
    variant_id = data["variant_id"]

    option_name = data["option_name"]
    option_value = data["option_value"]

    variation = data["variation"]
    carrier = data["carrier"] or "null"

    if not carrier and vendor not in ("shopee",):
        return HttpResponse(status=403)

    data = extract_product_data(url, vendor)
    if not data:
        return HttpResponseNotFound("fornecedor não suportado")

    product = ProductShopee()
    product.product_variant = ProductVariant.objects.get(pk=variant_id)
    product.quantity = int(amount)
    product.shopee_url = url

    if vendor == "shopee":
        shop_id, item_id = data

        product.shop_id = int(shop_id)
        product.item_id = int(item_id)
        product.model_id = int(option_value)

        product.option_name = option_name
    else:  # aliexpress
        product_id, = data

        product.item_id = int(product_id)
        product.shop_id = int(variation["store_id"])

        if option_value == "null":
            option_value = None

        product.model_id = option_name  # sku
        product.option_name = option_value

        company = carrier["company"]

        product.carrier_id = Carrier(
            company["id"],
            company["name"],
            "ali",
        )

    if vendor == "aliexpress":
        vendor = "ali"

    product.vendor = vendor

    product.save()

    return HttpResponse(status=201)


@login_required(login_url="login")
def processableProduct(request) -> HttpResponse:
    """ Carrega a dashboard na parte do produto processável.
    :param request: O objeto da request.
    
    :returns: A renderização da página. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    if request.method == "POST":
        print(request.POST)
        formData = request.POST
        variantId = formData.get("variantId")
        status = (formData.get("status")).upper()
        if status == "TRUE":
            status = True
        else:
            status = False
        print(status)
        print("status")
        print(type(status))
        productVariant = ProductVariant.objects.get(pk=variantId)
        productVariant.is_processable = not status
        productVariant.save()
    return render(
        request,
        "dashboard.html",
        {
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
        },
    )


# @cache_request
@login_required(login_url="login")
def vendorProductGetVariant(request, variant_id: int) -> JsonResponse:
    """ Pega a variante de um produto.
    :param request: O objeto da request.
    :param variant_id: O ID da variante do produto.
    
    :returns: Os dados do vendor em formato JSON. """

    if request.method != "POST":
        return HttpResponseNotAllowed(("POST",))

    form = ShopeeProductVariant(request.POST)
    if not form.is_valid():
        errors = form.errors.as_json()
        errors = json.loads(errors)

        return JsonResponse(errors, status=400)

    url = form.cleaned_data["url"]
    vendor = form.cleaned_data["vendor"]

    data = extract_product_data(url, vendor)

    if not data:
        form.add_error("url", f"URL inválida para {vendor!r}.")

        errors = form.errors.as_json()
        errors = json.loads(errors)

        return JsonResponse(errors, status=400)

    user = request.user

    mapping_other_vendor = (
        ProductShopee.objects
            .filter(
                product_variant=variant_id,
                product_variant__product_shopify__user_shop__user=user,
            )
            .exclude(vendor=vendor)
            .values_list("vendor", flat=True)
            [:1]
    )

    if mapping_other_vendor:
        vendor, = mapping_other_vendor

        form.add_error("vendor",
                       f"Você já tem mapeamento(s) para {vendor}."
                       " Você não pode utilizar outro fornecedor.")

        errors = form.errors.as_json()
        errors = json.loads(errors)

        return JsonResponse(errors, status=400)

    if vendor == "ali":
        # The lambda uses `aliexpress` instead of `ali`.
        vendor = "aliexpress"

    body = json.dumps({vendor: data})

    lambda_url = settings.REST_GATEWAY_CONSULT_PRODUCT
    lambda_key = settings.REST_GATEWAY_CONSULT_PRODUCT_API_KEY
    response = requests.post(
        lambda_url,
        data=body,
        timeout=settings.CONSULT_PRODUCT_TIMEOUT,
        headers={"X-Api-Key": lambda_key},
    )

    try:
        body = response.json()
    except Exception:
        response.status_code = 500
        body = {"message": "Não foi possível acessar a URL."}

    if response.status_code != 200:
        form.add_error("url", body["message"])

        errors = form.errors.as_json()
        errors = json.loads(errors)

        body = errors

    print(body)
    return JsonResponse(body, status=response.status_code)


@login_required(login_url="login")
def vendorUserCreate(request, **kwargs) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Cria um VendorUser.
    :param request: O objeto da request.
    :param kwargs: As kwargs.
    
    :returns A renderização da página de criação, ou um redirect para a tela de informações. """

    notionUrl = settings.NOTION_ACCOUNT_URL
    user = request.user
    template = "shopeeUserCreate.html"
    subscriptionStatus = getSubscriptionStatus(request.user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    counter_seconds = settings.VENDORUSERCREATE_SMS_COUNTER

    if "ctype" not in kwargs:
        return redirect("vendorUsers")
    
    if kwargs["ctype"] == "aliexpress":
        template = "shopeeUserCreateAli.html"

    return render(
        request,
        template,
        {
            "nbar": "shopeeUsers",
            "ctype": kwargs["ctype"],
            "PHONE_VALIDATION_ERROR_DDI_MSG": settings.PHONE_VALIDATION_ERROR_DDI_MSG,
            "PHONE_VALIDATION_ERROR_DDD_MSG": settings.PHONE_VALIDATION_ERROR_DDD_MSG,
            "PHONE_VALIDATION_ERROR_PHONE_MSG": settings.PHONE_VALIDATION_ERROR_PHONE_MSG,
            "FILL_ALL_FIELDS_VALIDATION_MSG": settings.FILL_ALL_FIELDS_VALIDATION_MSG,
            "counter_seconds": counter_seconds,
            "subscription_status": subscriptionStatus,
            "working_admin": working_admin,
            "notionUrl": notionUrl,
        },
    )


@login_required(login_url="login")
def vendorUserResendSmsApi(request) -> JsonResponse:
    """ Reenvia um SMS para o VendorUser pela API.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em formato JSON. """

    try:
        jsonData = {}
        jsonData["csrftoken"] = request.POST.get("csrftoken")
        jsonData["spc_f"] = request.POST.get("spc_f")
        jsonData["spc_si"] = request.POST.get("spc_si")
        jsonData["phone"] = request.POST.get("phone")
        jsonData["proxy"] = request.POST.get("proxy")
        jsonData["port"] = request.POST.get("port")
        jsonData["proxy_login"] = request.POST.get("proxy_login")
        jsonData["proxy_password"] = request.POST.get("proxy_password")
        jsonData["spc_ec"] = request.POST.get("spc_ec")
        jsonData["account_type"] = "O"

        if request.POST.get("ctype") == "true":
            identity_token = request.POST.get("captcha_signature")
            print(identity_token)
            b64_string = identity_token.split(".")[1]
            print(b64_string)
            signData = base64.b64decode(b64_string + "==").decode("utf-8")
            signData = json.loads(signData)
            userShopee = UserShopee.objects.get(email=signData["email"])

            if userShopee.user_shop.user != request.user:
                raise Exception("Esse usuário não é associado a sua conta.")
            jsonData["spc_ec"] = userShopee.spc_ec
            jsonData["account_type"] = userShopee.account_type

        print("[ResendSMS]")
        response = resendSmsOptCode(jsonData)
        print("response resend: ", response)
        responseJson = json.loads(response)
        if responseJson.get("statusCode") == 200:
            return JsonResponse(
                {"status_code": 200, "message": "Código reenviado."}, safe=False
            )
        else:
            capture_message(responseJson.get("body"))
            raise Exception(responseJson.get("body"))
    except Exception as e:
        capture_exception(e)
        return JsonResponse({"status_code": 404, "message": str(e)}, safe=False)


@login_required(login_url="login")
def createUserOnVendor(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Cria um usuário no vendor.
    :param request: O objeto da request.
    
    :returns: A renderização da página de criação, ou um redirect para a página de informações. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    return render(
        request,
        "createUserOnShopee.html",
        {
            "nbar": "shopeeUsersWithoutShop",
            "subscription_status": subscriptionStatus,
            "working_admin": working_admin,
        },
    )


@login_required(login_url="login")
def createUserOnVendorFromVendorUsers(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Cria um usuário no vendor pelo VendorUser.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de criação do usuário. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    return render(
        request,
        "createUserOnShopee.html",
        {
            "nbar": "shopeeUsers",
            "subscription_status": subscriptionStatus,
            "working_admin": working_admin,
        },
    )


@login_required(login_url="login")
@transaction.atomic
def createUserOnVendorAPI(request) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Cria um usuário no vendor pela API.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request. """

    print("[createUserOnVendorAPI]")
    if request.method == "POST":
        sid = transaction.savepoint()
        shopeeUser = UserShopee()
        shopeeUser.email = request.POST.get("email")
        shopeeUser.password = request.POST.get("password")
        shopeeUser.proxy = request.POST.get("proxy")
        shopeeUser.port = request.POST.get("port")
        shopeeUser.proxy_login = request.POST.get("proxy_login")
        shopeeUser.proxy_password = request.POST.get("proxy_password")
        shopeeUser.captcha_signature = request.POST.get("captcha_signature")
        shopeeUser.sms_api_key = request.POST.get("sms_api_key")
        shopeeUser.created_status = "BC"
        shopeeUser.creation_request_date = timezone.now()

        try:
            shopeeUser.save()
            createUserShopee(shopeeUser)
            transaction.savepoint_commit(sid)
            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
            )
        except Exception as e:
            if e.__cause__ and e.__cause__.pgcode == "23505":
                return JsonResponse(
                    {
                        "status_code": "404",
                        "message": "Já existe um usuário com esse email",
                    },
                    safe=False,
                )
            transaction.savepoint_rollback(sid)
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)

    return redirect("vendorUsers")


@login_required(login_url="login")
def vendorUserValidateSmsJson(request) -> JsonResponse:
    """ Valida o VendorUser por SMS pela API.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request. """

    print("[shopeeUserValidateSms]")
    user = request.user
    if request.method == "POST":
        try:
            shopeeUser = UserShopee()
            csrftoken = request.POST.get("csrftoken")
            shopeeUser.email = request.POST.get("email")
            shopeeUser.phone = request.POST.get("phone")
            spc_f = request.POST.get("spc_f")
            spc_si = request.POST.get("spc_si")
            sms_code = request.POST.get("sms_code")
            shopeeUser.user_shop = UserShop.objects.get(user=user)
            shopeeUser.password = request.POST.get("password")
            shopeeUser.proxy = request.POST.get("proxy")
            shopeeUser.port = request.POST.get("port")
            shopeeUser.proxy_login = request.POST.get("proxy_login")
            shopeeUser.proxy_password = request.POST.get("proxy_password")
            shopeeUser.captcha_signature = request.POST.get("captcha_signature")
            shopeeUser.activated = (
                True if request.POST.get("activated") == "true" else False
            )
            body = validateSmsV3(shopeeUser, csrftoken, spc_f, spc_si, "", "", sms_code)

            is_email_updated = body.get("is_email_updated")

            qs = UserShopee.objects.filter(email=shopeeUser.email)
            usershopee_id = -1
            if qs.exists():
                usershopee_id = qs.first().id

            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso", "is_email_updated": is_email_updated, "usershopee_id": usershopee_id }, safe=False
            )
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)


@login_required(login_url="login")
def vendorUserValidateSmsGoogleJson(request) -> JsonResponse:
    """ Valida por SMS o ShopeeUser.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """

    print("[shopeeUserValidateGoogleSms]")
    if request.method == "POST":
        try:
            identity_token = request.POST.get("identity_token")
            email = request.POST.get("email")

            if not email:
                b64_string = identity_token.split(".")[1]
                signData = base64.b64decode(b64_string + "==").decode("utf-8")
                signData = json.loads(signData)
                email = signData["email"]
            sms_code = request.POST.get("sms_code")
            spc_f = request.POST.get("spc_f")
            spc_si = request.POST.get("spc_si")
            spc_ec = request.POST.get("spc_ec")
            spc_u = request.POST.get("spc_u")
            seed = request.POST.get("seed")
            phone = request.POST.get("phone")
            shopeeUser = UserShopee.objects.get(email=email)

            if shopeeUser.user_shop.user != request.user:
                raise Exception("Esse usuário não é associado a sua conta.")

            shopeeUser.spc_f = spc_f
            shopeeUser.save()
            print("PHONEEEEEEEEEEEEEEEEEE", phone)
            csrftoken = request.POST.get("csrftoken")
            print("vendorUserValidateSmsGoogleJson", request.POST)
            validateSmsGoogle(
                shopeeUser,
                csrftoken,
                spc_f,
                spc_si,
                spc_ec,
                spc_u,
                seed,
                phone,
                sms_code,
            )
            shopeeUser = UserShopee.objects.get(email=email)
            shopeeUser.phone = phone
            shopeeUser.created_status = "C"
            shopeeUser.save()
            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
            )
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)


@login_required(login_url="login")
def aliUserValidateJson(request) -> JsonResponse:
    """ Valida o usuário aliexpress.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """

    ali_form = AliUserForm(request.POST)
    if ali_form.is_valid():
        try:
            usr_shop = UserShop.objects.get(user=request.user)
            usr_shopee = UserShopee()
            usr_shopee.email = ali_form.cleaned_data['email']
            usr_shopee.password = ali_form.cleaned_data['password']
            usr_shopee.vendor = "ali"
            usr_shopee.created_status = "C"
            usr_shopee.user_shop = usr_shop
            usr_shopee.activated = True
            usr_shopee.save()

        except IntegrityError:
            return JsonResponse({"error": "Esse usuário já existe."})

        return JsonResponse({"success": "Usuário adicionado com sucesso."})

    return JsonResponse({"error": "Dados inválidos."})
    
    

@login_required(login_url="login")
def vendorUserValidateJson(request) -> JsonResponse:
    """ Valid o VendorUser.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """ 

    print("shopeeUserValidate")
    if request.method == "POST":
        try:
            ctype = request.POST.get("ctype")

            shopeeUser = UserShopee()

            header = {}
            if ctype != "google":
                print("NÃO GOOGLE")

                shopeeUser.password = request.POST.get("password")
                shopeeUser.email = request.POST.get("email")

                validateEmail(shopeeUser.email)

                header64 = request.POST.get("header")
                headerString = base64.b64decode(header64).decode("utf-8")
                header = json.loads(headerString)

                cookies = header.get("Cookie")
                csrfToken = cookies.split("csrftoken=")[1].split(";")[0]
                spcF = cookies.split("SPC_F=")[1].split(";")[0]
                spcSi = cookies.split("SPC_SI=")[1].split(";")[0]

                print("spcF", spcF)
                print("spcSi", spcSi)
                print("csrfToken", spcSi)

                shopeeUser.captcha_signature = request.POST.get("captcha_signature")
            else:
                shopeeUser.identity_token = request.POST.get("captcha_signature")

                b64_string = shopeeUser.identity_token.split(".")[1]
                print(b64_string)

                signData = base64.b64decode(b64_string + "==").decode("utf-8")
                signData = json.loads(signData)

                shopeeUser.email = signData["email"]
                shopeeUser.created_status = "TNV"
                shopeeUser.user_shop_id = UserShop.objects.get(user=request.user).id

                csrfToken = header.get("X-CSRFToken")
                spcF = header.get("SPC_F")
                spcSi = header.get("SPC_SI")

            shopeeUser.phone = request.POST.get("phone")
            shopeeUser.proxy = request.POST.get("proxy")
            shopeeUser.account_type = "G" if ctype == "google" else "O"
            shopeeUser.port = request.POST.get("port")
            shopeeUser.proxy_login = request.POST.get("proxy_login")
            shopeeUser.proxy_password = request.POST.get("proxy_password")
            shopeeUser.fingerprint = request.POST.get("fingerprint")

            try:
                UserShopee.objects.get(email=shopeeUser.email)
            except UserShopee.DoesNotExist:
                pass
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "code": 403,
                        "message": "Já existe uma conta com o email informado.",
                    }
                )

            jsonData = validateUserShopeeHandler(shopeeUser, csrfToken, spcF, spcSi)

            return JsonResponse(jsonData, safe=False)
        except DropShopeeProxyError as e:
            return JsonResponse({"status": False, "message": str(e), "code": 301})
        except DropShopeeUserError as e:
            return JsonResponse({"status": False, "message": str(e), "code": 301})
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status": False, "message": str(e), "code": 201})


@login_required(login_url="login")
def sendValidatePhoneSms(request) -> JsonResponse:
    """ Envia a validação do número de telefone por SMS.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """

    if request.method == "POST":
        print("[sendValidatePhoneSms]")
        try:
            identity_token = request.POST.get("identity_token")
            email = request.POST.get("email")

            if not email:
                b64_string = identity_token.split(".")[1]
                signData = base64.b64decode(b64_string + "==").decode("utf-8")
                signData = json.loads(signData)
                print(signData["email"])
                email = signData["email"]

            shopeeUser = UserShopee.objects.get(email=email)
            if shopeeUser.user_shop.user != request.user:
                raise Exception("Esse usuário não é associado a sua conta.")
            shopeeUser.phone = request.POST.get("phone")

            csrfToken = request.POST.get("X-CSRFToken")
            spcF = request.POST.get("SPC_F")
            spcSi = request.POST.get("SPC_SI")
            spcEc = request.POST.get("SPC_EC")
            spcU = request.POST.get("SPC_U")

            jsonData = sendGoogleSms(shopeeUser, csrfToken, spcF, spcSi, spcEc, spcU)
            print("RESULT GOOGLE SMS: ", jsonData)

            json.loads(jsonData)

            return JsonResponse(jsonData, safe=False)
        except DropShopeeProxyError as e:
            return JsonResponse({"status": False, "message": str(e), "code": 301})
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status": False, "message": str(e), "code": 201})


def validateEmail(email) -> None:
    """ Valida o campo de email.
    :param email: O email para validar. """

    encodedEmail = email.encode("utf-8")
    if "\\" in str(encodedEmail):
        raise DropShopeeUserError(
            "Email inválido - O email não pode ter caracteres especiais."
        )


def validateUserShopeeHandler(shopeeUser, csrfToken, spcF, spcSi) -> Dict[str, str]:
    """ Valida o handler do UserShopee.
    :param shopeeUser: O ShopeeUser.
    :param csrfToken: O token csrf da request.
    :param spcF: O token scpF da request.
    :param scpSi: O token scpSi da request. """

    print("[validateUserShopeeHandler]")
    body = createUserShopeeV3(shopeeUser, csrfToken, spcF, spcSi)
    bodyJson = json.loads(body)
    jsonData = {
        "csrftoken": bodyJson["sessionObj"].get("csrftoken"),
        "spc_f": bodyJson["sessionObj"].get("SPC_F"),
        "spc_ec": bodyJson["sessionObj"].get("SPC_EC"),
        "spc_u": bodyJson["sessionObj"].get("SPC_U"),
        "spc_si": bodyJson["sessionObj"].get("SPC_SI"),
    }

    return jsonData


@login_required(login_url="login")
def vendor_order_line_item_bulk_update_status(request) -> HttpResponse:
    """ Atualiza em massa o status das OLIs do vendor.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request. """

    if request.method != "POST":
        return MethodNotAllowed(("POST",))

    try:
        status = request.POST["status"]

        assert status in dict(Order.STATUS)
        #                implicit iter in dict.keys()
        #                same as:
        #                   map(lambda i: i[0], Order.STATUS)

        olis = []
        for order in json.loads(request.POST["orders"]):
            olis += order["olis"]

        assert isinstance(olis, list)
    except Exception as e:
        print(e)
        capture_exception(e)
        return BadRequest()

    order_line_items_id = [i["id"] for i in olis]

    if status == "C":
        cancel_order_line_items(order_line_items_id)

        return HttpResponse(status=200)
    query = (OrderLineItem.objects
                .filter(id__in=order_line_items_id))

    temp = []


    for order_line_item in query:
        order_line_item.status = status

        temp.append(order_line_item)

        if status == "APS":
            order_purchase_line_items = OrderPurchaseLineItem.objects.filter(order_line_item=order_line_item)
            for order_purchase_line_item in order_purchase_line_items:
                boleto = order_purchase_line_item.order_purchase.boleto_id
                boleto.paid = True
                boleto.save()

    OrderLineItem.objects.bulk_update(temp, ("status",))

    return HttpResponse(status=200)


@login_required(login_url="login")
def verifyShopifyOrdersFulfillment(request) -> JsonResponse:
    """ Verifica o cumprimento dos pedidos da Shopify.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """

    if request.method == "POST":
        user = request.user
        try:
            userShop = UserShop.objects.get(user=user)
            success, message = checkShopifyPermissions(userShop)
            if success:
                return JsonResponse(
                    {
                        "status_code": "200",
                        "message": "Sim, estão sendo processados automaticamente!",
                    },
                    safe=False,
                )
            if not success:
                return JsonResponse(
                    {"status_code": "404", "message": message}, safe=False
                )
        except UserShop.DoesNotExist:
            if not success:
                return JsonResponse(
                    {
                        "status_code": "404",
                        "message": "Você não tem nenhuma loja cadastrada com credenciais válidas !",
                    },
                    safe=False,
                )


@login_required(login_url="login")
def vendorOrdersProcessManually(request) -> JsonResponse:
    """ Atualiza manualmente o status de processamento dos pedidos do vendor.
    :param request: O objeto da request.
    
    :returns: Resposta JSON vazia. """

    if request.method == "POST":
        orders = request.POST.get("orders")
        ordersJson = json.loads(orders)

        ordersId = [order.get("id") for order in ordersJson]

        ordersFromDB = Order.objects.filter(id__in=ordersId)
        updatedOrders = []
        ordersIdToUpdate = []

        updatedOrdersLocked = []

        for order in ordersFromDB:
            if order.sync_shopee:
                updatedOrdersLocked.append(order.id)
            else:
                order.status = "AO"
                updatedOrders.append(order)
                ordersIdToUpdate.append(order.id)

        Order.objects.bulk_update(updatedOrders, ["status"])
        apiMakeOrderManually(ordersIdToUpdate)
        return JsonResponse({}, safe=False)


@login_required(login_url="login")
def vendorOrdersDelete(request) -> JsonResponse:
    """ Deleta os pedidos do vendor.
    :param request: O objeto da request.
    
    :returns: Resposta JSON vazia. """

    if request.method == "POST":
        orders = request.POST.get("orders")
        ordersJson = json.loads(orders)

        ordersId = [order.get("id") for order in ordersJson]

        ordersFromDB = Order.objects.filter(
            Q(id__in=ordersId) | Q(parent_order__in=ordersId)
        )

        updated_orders = []
        updated_olis = []

        for order in ordersFromDB:
            order.status = "DO"
            order.dropshopee_deleted_date = timezone.now()
            for oli in OrderLineItem.objects.filter(order=order):
                oli.droplinkfy_deleted_date = timezone.now()
                oli.status = "DO"
                updated_olis.append(oli)
            updated_orders.append(order)

        Order.objects.bulk_update(updated_orders, ["status", "dropshopee_deleted_date"])
        OrderLineItem.objects.bulk_update(updated_olis, ["status", "droplinkfy_deleted_date"])
        return JsonResponse({}, safe=False)


def parseShopeeUrl(url) -> Union[str, Tuple[int, int]]:
    """ Dá um parse no URL da Shopee.
    :param url: O URL para dar o parse.
    
    :returns: O URL parsado. """

    if url[-1] == "/":
        url = url[:-1]
    if "/product/" in url:
        linkSplitted = url.split("/")
        shopId = linkSplitted[len(linkSplitted) - 2]
        itemId = linkSplitted[len(linkSplitted) - 1]

        if not shopId.isnumeric() or not itemId.isnumeric():
            return ""

        return shopId, itemId

    elif len(url.split(".")) > 2:
        linkSplitted = url.split(".")
        shopId = linkSplitted[len(linkSplitted) - 2]
        itemId = linkSplitted[len(linkSplitted) - 1]

        if not shopId.isnumeric() or not itemId.isnumeric():
            return ""

        return shopId, itemId

    return ""


@login_required(login_url="login")
@transaction.atomic
def vendorUsersRetryCreationBulk(request) -> Union[HttpResponseRedirect, JsonResponse]:
    """ Tenta novamente a criação em massa dos VendorUsers.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request ou um redirect para o vendorUsersWithoutShop. """

    if request.method == "POST":
        try:
            sid = transaction.savepoint()
            ids = json.loads(request.POST.get("userShopeeIds"))
            print(type(ids))
            captcha_signature = request.POST.get("captcha_signature")
            shopeeUsers = UserShopee.objects.filter(id__in=ids)

            for shopeeUser in shopeeUsers:
                shopeeUser.captcha_signature = captcha_signature
                shopeeUser.created_status = "BC"
                shopeeUser.creation_request_date = timezone.now()

            UserShopee.objects.bulk_update(
                shopeeUsers,
                ["captcha_signature", "created_status", "creation_request_date"],
            )
            transaction.savepoint_commit(sid)
            createUsersShopees(ids)
            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
            )
        except Exception as e:
            transaction.savepoint_rollback(sid)
            if e.__cause__ and e.__cause__.pgcode == "23505":
                return JsonResponse(
                    {
                        "status_code": "404",
                        "message": "Já existe um usuário com esse email",
                    },
                    safe=False,
                )
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)
    return redirect("vendorUsersWithoutShop")


def vendorUsersUploadCSV(request) -> HttpResponse:
    """ Faz um upload CSV dos VendorUsers.
    :param request: O objeto da request.
    
    :returns: A renderização da tela do upload CSV. """

    try:
        if request.method == "POST":
            sid = transaction.savepoint()
            captcha = request.POST.get("captcha_signature")
            uploaded_csv = request.FILES["usersCSV"]
            usersList = []
            it = 0
            for chunk in uploaded_csv.chunks():
                newLines = chunk.decode("utf-8").split("\r\n")
                if it == 0:
                    del newLines[0]

                processLines(usersList, captcha, newLines)
                it += 1

            list_of_users = UserShopee.objects.bulk_create(usersList)
            transaction.savepoint_commit(sid)
            list_of_ids = [user.id for user in list_of_users]
            createUsersShopees(list_of_ids)
            messages.success(request, "Sucesso - Usuários em criação")
    except IntegrityError as e:
        pqp = e.args[0]
        r = pqp.split("DETAIL")
        r1 = r[-1]
        r1 = r1.replace("\n", "")
        r1 = r1.replace(":", "")
        r1 = r1.strip()
        messages.error(request, r1)
    except Exception as e:
        messages.error(request, str(e))
        transaction.savepoint_rollback(sid)
    finally:
        return render(
            request, "shopeeUsersUploadCSV.html", {"nbar": "shopeeUsersWithoutShop"}
        )


def processLines(usersList, captcha, newLines) -> None:
    """ Processa as linhas.
    :param usersList: A lista de usuários.
    :param captcha: A assinatura captcha.
    :param newLines: As linhas para processar. """

    for line in newLines:
        print(line)
        if line:
            lineSplt = line.split(";")
            userShopee = UserShopee()
            userShopee.email = lineSplt[0]
            userShopee.password = lineSplt[1]
            userShopee.proxy = lineSplt[2]
            userShopee.port = lineSplt[3]
            userShopee.proxy_login = lineSplt[4]
            userShopee.proxy_password = lineSplt[5]
            userShopee.sms_api_key = lineSplt[6]
            userShopee.captcha_signature = captcha
            userShopee.created_status = "BC"
            userShopee.creation_request_date = timezone.now()

            usersList.append(userShopee)

@login_required(login_url='login')
def plans(request) -> HttpResponse:
    """ Carrega a tela de dos planos de checkout.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de checkout. """

    freeShippingMessage = settings.FREE_SHIPPING_MESSAGE
    priceMessage = settings.PRICE_MESSAGE
    return render(
        request,
        "checkout-index.html",
        {"freeShippingMessage": freeShippingMessage, "priceMessage": priceMessage},
    )

@login_required(login_url='login')
def plansReactivate(request) -> HttpResponse:
    """ Carrega a tela de reativação do checkout os planos.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de checkout. """

    freeShippingMessage = settings.FREE_SHIPPING_MESSAGE
    priceMessage = settings.PRICE_MESSAGE
    return render(request, 'checkout-reactivate.html', {"freeShippingMessage": freeShippingMessage, "priceMessage": priceMessage})

@login_required(login_url='login')
def affiliates(request) -> HttpResponse:
    """ Carrega a tela de checkout dos afiliados.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de checkout. """

    freeShippingMessage = settings.FREE_SHIPPING_MESSAGE
    return render(
        request,
        "checkout-affiliates.html",
        {"freeShippingMessage": freeShippingMessage},
    )


def checkoutThanks(request) -> HttpResponse:
    """ Carrega a tela de agradecimento pelo checkout.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de agradecimento. """

    return render(request, "checkout-thanks.html")


@csrf_exempt
def checkoutSession(request) -> JsonResponse:
    """ Cria uma sessão de checkout.
    :param request: O objeto da request.
    
    :returns: A sessão em formato JSON. """

    referral = json.loads(request.body.decode("utf-8")).get("referral")
    if not referral:
        referral = str(uuid.uuid4())
    urlFromRequest = json.loads(request.body.decode("utf-8")).get("url")
    qs_customer = Customer.objects.filter(user=request.user)

    if qs_customer.exists():
        user_customer = qs_customer.first()
    else:
        customer = stripe.Customer.create(email=request.user.email)
        user_customer = Customer.objects.create(id=customer['id'], user=request.user, created=customer['created'], email=customer['email'])
        

    affiliatesUrl = settings.AFFILIATES_URL
    stripeProductPrice = settings.STRIPE_PRODUCT_PRICE
    affiliatestripeProductPrice = settings.AFFILIATE_STRIPE_PRODUCT_PRICE
    if affiliatesUrl in urlFromRequest:
        responseJson = createCheckoutSession(request, affiliatestripeProductPrice, 'affiliates', user_customer)
    else:
        responseJson = createCheckoutSession(request, stripeProductPrice, 'plans', user_customer)
    return JsonResponse(responseJson, safe=False)

@csrf_exempt
def checkoutReactivate(request) -> HttpResponseRedirect:
    """ Reativa o checkout.
    :param request: O objeto da request.
    
    :returns: Um redirect para a página de cobranças. """

    user_customer = Customer.objects.get(user=request.user)
    affiliatestripeProductPrice = settings.AFFILIATE_STRIPE_PRODUCT_PRICE
    
    reactivateSubscription(affiliatestripeProductPrice, user_customer)
    
    return redirect('charges')

@login_required(login_url="login")
def checkoutSetup(request) -> HttpResponse:
    """ Carrega a tela de configuração do checkout.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de configurações do checkout. """

    return render(request, "checkout-setup.html")


@login_required(login_url="login")
def checkoutCustomerTax(request) -> HttpResponse:
    """ Carrega a tela de taxas do customer no checkout.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    return render(request, "checkout-customerTax.html")


@login_required(login_url="login")
def checkoutSetupThanks(request) -> HttpResponseRedirect:
    """ Carrega a tela de agradecimento de conclusão das configurações de checkout.
    :param request: O objeto da request.
    
    :returns: Um redirect para a tela de index. """

    user = request.user
    sessionId = request.GET.get("session_id")
    manageSession(sessionId, user)
    return redirect("index")


@csrf_exempt
def checkoutSetupSession(request) -> JsonResponse:
    """ Cria uma sessão de configurações do checkout.
    :param request: O objeto da request.
    
    :returns: O sessão em formato JSON. """

    responseJson = createCheckoutSetupSession(request)
    return JsonResponse(responseJson)


@login_required(login_url="login")
def portal(request) -> HttpResponseRedirect:
    """ Carrega a tela do portal.
    :param request: O objeto da request.
    
    :returns: Um redirect para a página de cobranças. """

    try:
        user = request.user
        customers = Customer.objects.filter(user=user).order_by("-created")
        if not customers:
            messages.error(
                request, "Sua assinatura é antiga, para ve-lâ contate o suporte"
            )
            return redirect(charges)
        subscriptionsCount = Subscription.objects.filter(
            customer__in=customers, status="active"
        ).count()
        if subscriptionsCount > 1:
            messages.error(
                request,
                "Você tem mais de 1 assinatura ativa para o mesmo usuário, para ve-lâ contate o suporte",
            )
            return redirect(charges)
        session = getPortal(request, customers[0])
        return redirect(session.url)
    except stripe.error.StripeError as e:
        capture_exception(e)
        messages.error(request, str(e))
        return redirect(charges)


def getSubscriptionStatus(user) -> str:
    """ Pega o status da inscrição.
    :param user: O usuário para checar a inscrição.
    
    :returns: O status. """

    customer = Customer.objects.filter(email=user.email).order_by("-created")
    if customer:
        subscriptions = Subscription.objects.filter(
            customer_id=customer[0].id
        ).order_by("-current_period_end")
        if subscriptions:
            subscriptionStatus = subscriptions[0].status
            if subscriptionStatus != "past_due" and subscriptionStatus != "canceled":
                return "valid"
            return subscriptionStatus
    return "valid"


def getPercentagePayStatus(user) -> Tuple[str, int]:
    """ Pega o status do PercentagePay.
    :param user: O usuário de quem pegar.
    
    :returns: Uma tupla com o status e os dias até a conta ser bloqueada. """

    customer = Customer.objects.filter(email=user.email).order_by("-created")
    if customer:
        percentagePays = PercentagePay.objects.filter(
            customer_id=customer[0].id
        ).order_by("-created_at")
        if percentagePays:
            activePercentagePay = percentagePays[0]
            daysUntilAccountBlock = (
                activePercentagePay.created_at
                + timedelta(2)
                - datetime.now(dtTimezone.utc)
            ).days
            return activePercentagePay.status, daysUntilAccountBlock
    return "valid", 0


def getWorkingAdmin(user) -> bool:
    """ Checa se o usuário é um working admin.
    :param user: O usuário para checar.
    
    :returns: Verdadeiro ou falso. """

    if UserShop.objects.filter(user=user).exists():
        userShop = UserShop.objects.get(user=user)
        return userShop.working_admin
    else:
        return True


def setUpdatedDate(order, updatedFields) -> None:
    """ Seta a data de atualziação do pedido.
    :param order: O pedido pra setar.
    :param updatedFields: Os campos atualizados. """

    if order.status == "AO":
        order.updated_date_ao = timezone.now()
        updatedFields.append("updated_date_ao")
    if order.status == "AP":
        order.updated_date_ap = timezone.now()
        updatedFields.append("updated_date_ap")
    if order.status == "APS":
        order.updated_date_aps = timezone.now()
        updatedFields.append("updated_date_aps")
    if order.status == "AS":
        order.updated_date_as = timezone.now()
        updatedFields.append("updated_date_as")
    if order.status == "AF":
        order.updated_date_af = timezone.now()
        updatedFields.append("updated_date_af")
    if order.status == "F":
        order.updated_date_f = timezone.now()
        updatedFields.append("updated_date_f")
    if order.status == "C":
        order.updated_date_c = timezone.now()
        updatedFields.append("updated_date_c")
    if order.status == "FO":
        order.updated_date_fo = timezone.now()
        updatedFields.append("updated_date_fo")


def getTokenCrisp(request) -> JsonResponse:
    """ Pega o token do crisp.
    :param request: O objeto da request.
    
    :returns: Os dados do token em formato JSON. """

    user = request.user
    email = user.email
    crispWebsiteId = settings.CRISP_WEBSITE_ID

    try:
        token = UserInfo.objects.get(user=user).crisp_token
    except UserInfo.DoesNotExist:
        token = str(uuid.uuid4())
        userinfo = UserInfo()
        userinfo.user = user
        userinfo.crisp_token = token
        userinfo.save()
    response = {"token": token, "email": email, "crispWebsiteId": crispWebsiteId}
    return JsonResponse(response, safe=False)


def termsOfService(request) -> FileResponse:
    """ Pega os termos de uso.
    :param request: O objeto da request.
    
    :returns: O arquivo dos termos de uso. """

    try:
        return FileResponse(
            open("DROPLINKFY-TERMOS-DE-USO.pdf", "rb"), content_type="application/pdf"
        )
    except FileNotFoundError:
        raise Http404()


def privacyPolicy(request) -> FileResponse:
    """ Pega a política de privacidade.
    :param request: O objeto da request.
    
    :returns: O arquivo da política de privacidade. """

    try:
        return FileResponse(
            open("DROPLINKFY-POLITICA-DE-PRIVACIDADE.pdf", "rb"),
            content_type="application/pdf",
        )
    except FileNotFoundError:
        raise Http404()


def orders_report(request) -> JsonResponse:
    """ Pega o relatório dos pedidos.
    :param request: O objeto da request.
    
    :returns: O ID do relatório, ou o relatório em si em formato JSON. """

    if request.method == 'GET':
        report = Report.objects.get(pk=request.GET.get("report"))
        return JsonResponse({ "url": report.url, "status": report.status, "created_at": report.created_at })

    if request.method == 'POST':
        send_mail = request.POST.get("send_mail") == "true"
        report = Report()
        report.send_mail = send_mail
        user_shop = UserShop.objects.get(user=request.user)
        report.user_shop = user_shop
        report.save()
        
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        status = request.POST.get("status")

        generateCsvReport({
            "user_id": request.user.id,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "send_mail": send_mail,
            "report_id": report.id,
            "user_email": request.user.email
        })

        return JsonResponse({"id": report.id})


