from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from requests.models import Response
from shopee.models import *
from shopee.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
import requests
from urllib.parse import urlparse
import json
from shopeeApi.shopifyConnection import *
from shopeeApi.lmbdFnctApiCall import *
from django.db.models.signals import post_save, pre_save
from shopee.signals import postSaveUserShop, preSaveUserShop
from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone
from shopeeApi.stripeApi import *
from django.views.decorators.csrf import csrf_exempt
import uuid
from sentry_sdk import capture_exception

from datetime import datetime, timedelta
from datetime import timezone as dtTimezone


def manuallyForceCancelOrders() -> JsonResponse:
    """ Força manualmente o cancelamento de pedidos.
    
    :returns: Resposta JSON vazia. """

    status = "C"
    # orders = Order.objects.filter(status='AO',
    #                              boleto_number__isnull=False,
    #                              updated_date_c__isnull=True,
    #                              updated_date_f__isnull=True,
    #                              updated_date_fo__isnull=True,
    #                              canceled_at__isnull=True,
    #                              updated_date_ap__isnull=False)

    orders = Order.objects.filter(status="AO")

    ordersId = [order.id for order in orders]

    if status == "C":
        cancelOrders(ordersId)
        return JsonResponse({}, safe=False)

    ordersFromDB = Order.objects.filter(id__in=ordersId)
    updatedOrders = []

    for order in ordersFromDB:
        order.status = status
        updatedOrders.append(order)

    Order.objects.bulk_update(updatedOrders, ["status"])
    return JsonResponse({}, safe=False)
