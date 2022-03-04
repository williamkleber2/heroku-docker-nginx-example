from shopee.models import *
from shopeeApi.lmbdFnctApiCall import manualRetryBillingPercentage
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
import traceback
from datetime import datetime
from django.utils import timezone
from typing import Any

def manualRetryPercentagePay(request) -> JsonResponse:
    """ Retenta manualmente pagar o PercentagePay.
    :parma request: O objeto da request.
    
    :returns: O estado da resposta da request, com uma respectiva mensagem em formato JSON. """

    if request.method == "POST":
        try:
            user = request.user
            percentagePayId = request.POST.get("percentagePayId")
            customers = Customer.objects.filter(user=user)
            subscription = Subscription.objects.filter(
                customer__in=customers, status="active"
            )
            percentagePay = getObject(
                PercentagePay, subscription[0].customer.id, percentagePayId
            )
            if percentagePay.status == "paid":
                return jsonResponseBuild("200", "Essa fatura já foi paga!")
            limitManualPayRequests = settings.LIMIT_MANUAL_PAY_REQUEST
            if (
                percentagePay.last_manual_pay_date
                and percentagePay.last_manual_pay_date == datetime.today().date()
                and percentagePay.manual_pay_requests
                and percentagePay.manual_pay_requests > limitManualPayRequests
            ):
                raise Exception("Excedeu o número máximo de sincronizações para hoje")
            response = manualRetryBillingPercentage(user.id, percentagePayId)
            if not percentagePay.last_manual_pay_date:
                percentagePay.last_manual_pay_date = datetime.today().date()
                percentagePay.manual_pay_requests = 1
            else:
                if percentagePay.last_manual_pay_date == datetime.today().date():
                    percentagePay.manual_pay_requests += 1
                else:
                    percentagePay.last_manual_pay_date = datetime.today().date()
                    percentagePay.manual_pay_requests = 1
            percentagePay.save()
            if response.json().get("statusCode") == 200:
                percentagePay.status = "paid"
                percentagePay.paid_at = timezone.now()
                percentagePay.save()
                return jsonResponseBuild("200", response.json().get("body"))
            else:
                raise Exception(response.json().get("body"))
        except Exception as e:
            traceback.print_exc()
            return jsonResponseBuild("404", str(e))


def jsonResponseBuild(statusCode, message) -> JsonResponse:
    """ Cria uma resposta JSON com o código de status da request e uma mensagem relativa.
    :param statusCode: O código de status da request.
    :param message: A mensagem relativa ao código de status.
    
    :returns: A resposta JSON. """

    return JsonResponse({"status_code": statusCode, "message": message}, safe=False)


def getObject(model, objectRef, percentagePayId=None) -> Any:
    """ Pega um objeto qualquer a partir de um model.
    :param model: O model.
    :param objectReft: O objeto de referência.
    :param percentagePayId: O ID do PercentagePay.
    
    :returns: O objeto adquirido. """

    try:
        if percentagePayId:
            return model.objects.get(customer=objectRef, id=percentagePayId)
        else:
            return model.objects.get(user=objectRef)
    except model.DoesNotExist:
        raise Exception("Não existe nenhum objeto com esse id -> " + objectRef.id)
