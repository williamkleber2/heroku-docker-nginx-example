import collections
from typing import Final
from datetime import datetime

from django import http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import UserShopee, Order
from .allMethods import (
    getWorkingAdmin,
    getSubscriptionStatus,
    getPercentagePayStatus,
)

MONTHS: Final[list[str]] = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

@login_required(login_url='login')
def graphs(request: http.HttpRequest) -> http.HttpResponse:
    """ Carrega a tela de gráficos.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    working_admin = getWorkingAdmin(request.user)
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(request.user)

    return render(request, "graphs.html", {
        "nbar": "graphs",

        "subscription_status": subscriptionStatus,
        "percentagePay_status": percentagePayStatus,
        "daysUntilAccountBlock": daysUntilAccountBlock,
        "working_admin": working_admin,
    })


@login_required(login_url='login')
def graphs_users(request: http.HttpRequest) -> http.HttpResponse:
    """ Carrega a tela de gráficos dos usuários.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    users = (UserShopee.objects
                .filter(user_shop__user=request.user)
                .exclude(deactivate_status__exact="")
                .values_list("deactivate_status", flat=True))

    data = {
        "": [0, "Usuários disponíveis", "success"],

        "EL": [0, "Usuários com login expirados", "primary",
               None, None, None],
        "BA": [0, "Usuários banidos", "dark",
               None, None, None],
        "IP": [0, "Usuários com Proxy incorreta", "secondary",
               "Arrumar Proxies", "/vendorUsers",

               "Caso a proxy não seja validada, os status"
               " dos pedidos não serão atualizados."],
        "M" : [0, "Usuários desativados manualmente", "warning",
               None, None, None],
        "IT": [0, "Usuários com token inválido", "info",
               "Revalidar Tokens", "/vendorUsers",

               "Caso o token não seja validado novamente,"
               " os status dos pedidos não serão atualizados."],
    }

    for status in users:

        if status in data:
            data[status][0] += 1

    data = filter(lambda i: i[0], data.values())
    data = list(data)


    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


    data = chunks(data, 4)
    data = list(data)

    return http.JsonResponse(data, safe=False)


@login_required(login_url='login')
def graphs_total_orders(request: http.HttpRequest) -> http.HttpResponse:
    """ Carrega a tela de gráficos do total de pedidos.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    today = datetime.now()

    orders = (Order.objects
                .filter(user_shop__user=request.user,
                        status='F',
                        created_date__year=today.year,)
                .values_list("created_date__month", flat=True))

    counter = collections.Counter(orders)

    values = [counter.get(n, 0) for n, _ in enumerate(MONTHS)]

    return http.JsonResponse({
        "labels": MONTHS,
        "values": values,
        "empty": sum(values) == 0,
    })


@login_required(login_url='login')
def graphs_value_orders(request: http.HttpRequest) -> http.HttpResponse:
    """ Carrega a tela de gráficos do valor dos pedidos.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    today = datetime.now()

    orders = (Order.objects
                .filter(user_shop__user=request.user,
                        created_date__year=today.year,)
                .values("created_date__month",
                        "total_price",
                        "value",))

    counter = [{n: 0 for n, _ in enumerate(MONTHS)}
               for _ in range(3)]

    for order in orders:
        value = order["value"]
        if value is None:
            continue

        price = order["total_price"]
        month = order["created_date__month"]

        counter[0][month] += value
        counter[1][month] += price
        counter[2][month] += price - value  # lucro

    data = [tuple(d.values()) for d in counter]

    return http.JsonResponse({
        "labels": MONTHS,
        "datasets": [
            {
                "label": "Valor de Custo",
                "data": data[0],
                "backgroundColor": "rgba(255, 99, 132, .5)",
            },
            {
                "label": "Valor de Venda",
                "data": data[1],
                "backgroundColor": "rgba(75, 192, 192, .5)",
            },
            {
                "label": "Lucro",
                "data": data[2],
                "backgroundColor": "rgba(153, 102, 255, .5)"
            },
        ],
        "empty": not sum(sum(d) for d in data),
    })


@login_required(login_url='login')
def graphs_upsell(request: http.HttpRequest) -> http.HttpResponse:
    """ Carrega a tela de gráficos da upsell.
    :param request: O objeto da request.
    
    :returns: A renderização da tela. """

    today = datetime.now()

    orders = (Order.objects
                .exclude(parent_order=None)
                .filter(
                    status='F',
                    user_shop__user=request.user,
                    created_date__year=today.year,
                )
                .values("created_date__month"))

    orders  = map(lambda o: o["created_date__month"], orders)
    orders  = collections.Counter(orders)
    counter = {k: v*15 for k, v in orders.items()}

    values = [counter.get(i, 0) for i, _ in enumerate(MONTHS)]

    return http.JsonResponse({
        "labels": MONTHS,
        "datasets": [
            {
                "label": "Valor",
                "data": values,
                "backgroundColor": "rgba(75, 192, 192, .5)",
            },
        ],
        "empty": sum(values) == 0,
    })
