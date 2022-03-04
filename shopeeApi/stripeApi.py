from typing import Dict, List
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
import stripe
from stripe.api_resources import Customer as ApiCustomer, subscription
from stripe.error import InvalidRequestError
from django.conf import settings
from django.urls import reverse
from shopee.models import *
from enum import Enum
import logging
from typing import Any, Union

stripe.api_key = settings.STRIPE_API_KEY
stripePublicKey = settings.STRIPE_PUBLIC_KEY
SUBSCRIPTION_ACTIVE_STATUS_LIST = ("active", "trialing", "past_due")

def set_customer_billing_data(data: UserBillingData) -> None:
    """ Seta os dados de cobrança do customer.
    :param data: Os dados de cobrança do usuário. """

    customer = Customer.objects.get(user=data.user)
    metadata = {}

    metadata["doc_type"] = data.doc_type
    metadata[data.doc_type] = getattr(data, data.doc_type)
    stripe_customer = stripe.Customer.modify(customer.id, 
                        address={
                            "country": "BR",
                            "state": data.state,
                            "city": data.city,
                            "line1": data.address + ', ' + data.address_number,
                            "line2": data.address2,
                            "postal_code": data.zipcode,
                            }, phone=data.phone, metadata=metadata)

    try:
        stripe.Customer.create_tax_id(customer.id, **{ 'type': 'br_' + data.doc_type, 'value': getattr(data, data.doc_type)})
    except InvalidRequestError:
        # error raised when a document with same number already exists
        # for debugging see https://github.com/stripe/stripe-python/blob/e70949b8b6961907620f01aaea60ecea9759558f/stripe/api_resources/abstract/nested_resource_class_methods.py
        print("O número do documento não mudou.")

def createCheckoutSession(request, stripeProductPrice, cancelUrl, customer: Customer) -> Dict[str, Union[int, str]]:
    """ Cria uma sessão de checkout.
    :param request: O objeto da request.
    :param stripeProductPrice.
    :param cancelUrl: O URL dá página de cancelamento.
    :param customer: O customer.
    
    :returns: A resposta da criação em um dicionário. """

    logger = logging.getLogger()
    try:
        trial_period_days = 14 if Subscription.objects.filter(customer=customer).count() == 0 else None
        referral = None

        try:
            referral = customer.user.profile.referral
        except ObjectDoesNotExist:
            logger.warn("No profile.")

        checkout_session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse("checkoutThanks"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse(cancelUrl)),
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": stripeProductPrice,
                    "quantity": 1
                }
            ],
            customer=customer.id,
            client_reference_id=referral,
            allow_promotion_codes=True,
            subscription_data={'trial_period_days': trial_period_days}

        )
        responseJson = {
            "session_id": checkout_session.id,
            "stripe_public_key": stripePublicKey,
        }
        return responseJson
    except Exception as e:
        print(str(e))

def get_all_subscriptions(customer: Customer) -> List[Dict]:
    """ Pega todas as inscrições do customer.
    :param customer: O customer.
    
    :returns: Lista de de diiicionários das inscrições. """

    return stripe.Subscription.list(
        customer=customer.id,
    )['data']


def get_active_subscriptions(customer: Customer) -> List[Dict]:
    subscriptions = get_all_subscriptions(customer)
    return [s for s in subscriptions if s['status'] in SUBSCRIPTION_ACTIVE_STATUS_LIST]


def getPortal(request, customer: Customer) -> Dict:
    """ Gera uma sessão para o portal de cobrança.
    :param request: O objeto da request.
    :param customer: O customer.
    
    :returns: O objeto da sessão """

    session = stripe.billing_portal.Session.create(
        customer=customer.id,
        return_url=request.build_absolute_uri(reverse("login")),
    )
    return session


def manageSession(sessionId, user) -> None:
    """ Gerencia uma sessão.
    :param sessionId: ID of the session.
    :param user: O usuário. """

    session = stripe.checkout.Session.retrieve(sessionId)
    customerId = session.get("customer")
    customerJson = getCustomerFromStripe(customerId)
    customerObj = Customer()
    customerObj.id = customerId
    customerObj.user = user
    customerObj.created = customerJson.get("created")
    customerObj.email = customerJson.get("email")
    customerObj.save()
    print(customerObj)


def getCustomerFromStripe(customerId) -> Customer:
    """ Pega um customer pelo Stripe.
    :param customerId: O ID do customer.
    
    :returns: O customer. """

    customer = stripe.Customer.retrieve(customerId)
    return customer


def createCheckoutSetupSession(request) -> Dict[str, Union[int, str]]:
    """ Cria uma sessão da setup de checkout.
    :param request: O objeto da request.
    
    :returns: O dicionário da sessão. """

    try:
        customer = stripe.Customer.create()
        checkout_session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse("checkoutSetupThanks"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("index")),
            payment_method_types=["card"],
            mode="setup",
            customer=customer["id"],
        )
        responseJson = {
            "session_id": checkout_session.id,
            "stripe_public_key": stripePublicKey,
        }
        return responseJson
    except Exception as e:
        print(str(e))


def getCustomerTaxIds(customerActive) -> List[int]:
    """ Pega os IDs de taxa do customer.
    :param customerActive: O customer que está ativo.
    
    :returns: Lista de IDs das taxas. """

    if customerActive:
        taxIds = stripe.Customer.list_tax_ids(
            customerActive.id,
            limit=5,
        )
        return taxIds
    else:
        return None
