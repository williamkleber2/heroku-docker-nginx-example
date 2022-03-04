from .models import Customer, UserBillingData, PercentagePay, Subscription
from django.shortcuts import redirect
from shopeeApi.stripeApi import get_active_subscriptions, get_all_subscriptions

from typing import Callable, Union
from django.http.response import HttpResponse, HttpResponseRedirect

def have_plan(get_response: Callable) -> Union[HttpResponse, HttpResponseRedirect]:
    """ Checa se algo tem um plano.
    :param get_response: A função da qual pegar a resposta da request.
    
    :returns: A resposta da request, ou um redirect. """

    def middleware(request) -> Union[HttpResponse, HttpResponseRedirect]:
        """ Middleware da checagem.
        :param request: O objeto da request.
        
        :returns: A resposta da request, ou um redirect. """

        user = request.user
        response = get_response(request)

        if not user.is_authenticated:
            return redirect('login')

        if user.groups.filter(name='Afiliados').exists() or user.is_superuser:
            return response

        customer = Customer.objects.filter(user=request.user)
        has_subscription = False

        if customer.exists():
            active_subscriptions = get_active_subscriptions(customer.first())
            has_subscription = len(active_subscriptions) > 0

        if not has_subscription:
            return redirect('plans')

        is_trialling = all(sub["status"] == "trialing" for sub in active_subscriptions)

        if (not UserBillingData.objects.filter(user=request.user).exists() 
           and PercentagePay.objects.filter(customer=customer.first(), paid_at__isnull=False).exists() 
           and not is_trialling
           and not user.is_superuser
           ):
            return redirect('/charges/#billingInfo')

        return response
    
    return middleware

    