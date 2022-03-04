from collections import defaultdict
import traceback
import json
from datetime import timezone, timedelta

from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
import pytz
from django.utils.decorators import decorator_from_middleware
from shopee.models import *
from shopee.views.allMethods import *
from shopee.middlewares import have_plan
from shopee.views import sql
from django.conf import settings
from typing import Union


def fmt_gmt(gmt: Union[str, float, int]) -> str:
    """ Formata um horário GMT.
    :param gmt: O horário para formatar.
    
    :returns: O horário formatado. """

    gmt = float(gmt) / -60
    if gmt > 0:
        formatted = "+" + str(int(gmt)).zfill(2)
    elif gmt == 0:
        return "+00:00"
    else:
        formatted = str(int(gmt)).zfill(3) # include signal to zfill (Ex. -02)

    # add decimal
    formatted += ":" + str(int((gmt%1) * 60)).zfill(2)

    return formatted

@have_plan
@login_required(login_url='login')
def orders(request) -> HttpResponse:
    """ Carrega a tela dos pedidos.
    :param request: O objeto da request.
    
    :returns: A renderização da tela de pedidos. """

    notionUrl = settings.NOTION_ORDER_URL
    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    return render(
        request,
        "orders.html",
        {
            "nbar": "orders",
            "subscription_status": subscriptionStatus,
            "percentagePay_status": percentagePayStatus,
            "daysUntilAccountBlock": daysUntilAccountBlock,
            "working_admin": working_admin,
            "notionUrl": notionUrl,
        },
    )


@login_required(login_url="login")
def ordersFilterJSON(request) -> JsonResponse:
    """ Filtra os pedidos.
    :param request: O objeto do request.
    
    :returns: Os dados dos pedidos em JSON. """

    try:
        user = request.user
        postData = request.GET.get("selectedDates")
        pk = request.GET.get("orderFilter")

        selectedDates = json.loads(postData)

        gmt = fmt_gmt(request.GET.get("GMT"))
        startDate = datetime.strptime(selectedDates["startDate"] + " 00:00:00 " + gmt, "%Y-%m-%d %H:%M:%S %z")
        endDate = datetime.strptime(selectedDates["endDate"] + " 23:59:59 " + gmt, "%Y-%m-%d %H:%M:%S %z")

        allStatus = ["AF", "AO", "AP", "APS", "AS", "C", "F", "FO", "DO", "AI"]
        statusWithCount = []

        if pk == "<empty>":
            orders = (
                OrderLineItem.objects.filter(
                    user_shop__user=user,
                    order__created_date__gte=startDate,
                    order__created_date__lte=endDate,
                )
                .values("order__id", "status")
                .annotate(dcount=Count("status"))
                .values("status", "dcount")
            )
        else:
            orders = (
                OrderLineItem.objects.filter(
                    order__user_shop__user=user,
                    name__contains=pk,
                    order__created_date__gte=startDate,
                    order__created_date__lte=endDate,
                )
                .values("order__id", "status")
                .annotate(dcount=Count("status"))
                .values("status", "dcount")
            )

        status = defaultdict(lambda: { 'status': '', 'dcount': 0})
        for order in list(orders):
            status[order['status']] = { 
                'status': order['status'], 
                'dcount': status[order['status']]['dcount'] + 1
                }
            statusWithCount.append(order["status"])

        data = list(status.values())

        orderStatusWithoutCount = list(set(allStatus) - set(statusWithCount))

        for orderStatus in orderStatusWithoutCount:
            data.append({"status": orderStatus, "dcount": 0})
        response = {"data": data}

        return JsonResponse(response, safe=False)
    except Exception as e:
        traceback.print_exc()
        print(e)


@login_required(login_url="login")
def vendorOrdersJson(request, pk) -> JsonResponse:
    """ Pega os pedidos do vendor.
    :param request: O objeto da request.
    :param pk: A primary key do status.
    
    :returns: Os pedidos com filhos em formato JSON. """

    user = request.user
    gmt = fmt_gmt(request.GET.get("GMT"))
    postData = request.GET.get("selectedDates")
    name_filter = request.GET.get("orderFilter")

    selectedDates = json.loads(postData)

    startDate = selectedDates["startDate"]
    startDate = datetime.strptime(startDate, "%Y-%m-%d")
    startDate = startDate.replace(tzinfo=pytz.utc)
    start_date = localtime(startDate)

    endDate = selectedDates["endDate"]
    endDate = datetime.strptime(endDate, "%Y-%m-%d")
    endDate = endDate.replace(tzinfo=pytz.utc) + timedelta(days=1)
    end_date = localtime(endDate)

    def get_users(seq):
        ids = [i.get("user_shopee") for i in seq]

        us = UserShopee.objects.filter(id__in=ids)
        for i, u in enumerate(us):
            seq[i]["user_shopee"] = u.serialize_to_extension()

    status = pk

    orders = sql.get_user_shop_orders_by_status(user.id, status, name_filter, start_date, end_date, gmt)
    orders_with_child = []
    for order in orders:
        order["child"] = sql.get_child_orders_by_status(order["id"], status)
        order["olis"] = []

        for child in sql.get_orderlineitem_by_status(order["id"], status):
            child["olis"] = sql.get_child_orders_by_status(child["id"], status)
            order["olis"].append(child)

        get_users(order["olis"])
        cancel_status = [oli["cancellation_status"] for oli in order["olis"]]

        if all(s == 'C' for s in cancel_status):
            order["status"] = 'C'
        elif any(s == "NC" for s in cancel_status):
            order["status"] = "NC"
        elif any(s == "WC" for s in cancel_status):
            order["status"] = "WC"

        orders_with_child.append(order)
    
    return JsonResponse({
        "data": orders_with_child
    }, safe=False)


@login_required(login_url="login")
def vendorOrderEdit(request, pk) -> JsonResponse:
    """ Edita o pedido do vendor.
    :param request: O objeto da request.
    :param pk: A primary key do pedido.
    
    :returns: Lista de pedidos do vendor em um JSON. """

    user = request.user
    subscriptionStatus = getSubscriptionStatus(request.user)
    percentagePayStatus, daysUntilAccountBlock = getPercentagePayStatus(user)
    working_admin = getWorkingAdmin(user)
    if subscriptionStatus == "canceled" or not working_admin:
        return redirect("shopifyInfo")

    vendorOrders = Order.objects.filter(id=pk).values(
        "client_name",
        "client_phone",
        "street",
        "street_number",
        "complement",
        "zip_code",
        "city",
        "state",
        "neighborhood",
        "cpf",
        "id",
        "name",
    )

    if request.method == "POST":
        try:
            orderRequest = request.POST.get("order")
            orderJson = json.loads(orderRequest)
            vendorOrder = Order.objects.get(id=pk)
            vendorOrder.client_name = orderJson.get("client_name")
            vendorOrder.client_phone = orderJson.get("client_phone")
            vendorOrder.street = orderJson.get("street")
            vendorOrder.street_number = orderJson.get("street_number")
            vendorOrder.complement = orderJson.get("complement")
            vendorOrder.zip_code = orderJson.get("zip_code")
            vendorOrder.city = orderJson.get("city")
            vendorOrder.state = orderJson.get("state")
            vendorOrder.neighborhood = orderJson.get("neighborhood")
            vendorOrder.cpf = orderJson.get("cpf")

            vendorOrder.save()
            return JsonResponse(
                {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
            )
        except Exception as e:
            capture_exception(e)
            return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)
    response = {"data": list(vendorOrders)}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def upsellOrdersCheck(request) -> JsonResponse:
    """ Checa se os pedidos tem upsell.
    :param request: O objeto da request.
    
    :returns: Um JSON contento o dado se tem upsell e os IDs dos pedidos upsell. """

    user = request.user
    selectedordersData = request.GET.get("selectedOrders")
    selectedorders = json.loads(selectedordersData)

    addresses = []

    for order in selectedorders:
        addresses.append(order["address"])

    orders = (
        Order.objects.filter(user_shop__user=user, address__in=addresses, status="AI")
        .values("address")
        .annotate(dcount=Count("address"))
        .filter(dcount__gt=1)
    )
    dataOrders = list(orders)
    hasUpsell = len(dataOrders) > 0

    addressesToUpsell = []

    for order in dataOrders:
        addressesToUpsell.append(order["address"])

    ordersToUpsell = Order.objects.filter(
        user_shop__user=user, address__in=addressesToUpsell, status="AI"
    ).values("id")
    dataOrdersToUpsell = list(ordersToUpsell)
    print(dataOrdersToUpsell)
    upsellOrdersIds = []

    for order in dataOrdersToUpsell:
        upsellOrdersIds.append(order["id"])

    response = {"hasUpsell": hasUpsell, "upsellOrderIds": upsellOrdersIds}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def upsellOrders(request) -> JsonResponse:
    """ Pega os pedidos upsell.
    :param request: O objeto da request.
    
    :returns: Os pedidos. """
    
    user = request.user
    selectedordersData = request.GET.get("selectedOrders")
    upsellOrderIdsData = request.GET.get("upsellOrderIds")
    selectedorders = json.loads(selectedordersData)
    upsellOrderIds = json.loads(upsellOrderIdsData)
    orderIds = []
    addresses = []

    for order in selectedorders:
        orderId = order["id"]
        if orderId in upsellOrderIds:
            orderIds.append(orderId)
            addresses.append(order["address"])

    shopeeOrders = Order.objects.filter(
        user_shop__user=user, id__in=orderIds, status="AI"
    ).values(
        "name",
        "client_name",
        "client_phone",
        "cpf",
        "address",
        "status",
        "user_shopee__email",
        "shopee_checkout_id",
        "value",
        "boleto_url",
        "boleto_number",
        "boleto_due_date",
        "error",
        "error_date",
        "free_shipping",
        "canceled_at",
        "id",
        "sync_shopee",
        "created_date",
        "state",
        "street",
        "street_number",
    )

    dataOrders = list(shopeeOrders)

    ordersMap = {}
    orderIds = []
    for order in dataOrders:
        order["otus"] = []
        if order["address"] not in ordersMap:
            ordersMap[order["address"]] = order
            orderIds.append(order["id"])

    ordersToUpsell = (
        Order.objects.exclude(id__in=orderIds)
        .filter(address__in=addresses, status="AI")
        .values("name", "client_name", "address")
    )

    dataOrdersToUpsell = list(ordersToUpsell)
    print(dataOrdersToUpsell)

    for otu in dataOrdersToUpsell:
        order = ordersMap[otu["address"]]
        order["otus"].append(otu)
    orders = list(ordersMap.values())

    response = {"data": orders}
    return JsonResponse(response, safe=False)


@login_required(login_url="login")
def processUpsell(request) -> None:
    """ Processa o upsell.
    :param request: O objeto da request. """

    user = request.user
    ordersData = request.POST.get("orders")
    ordersUpsellData = request.POST.get("ordersUpsell")
    orders = json.loads(ordersData)
    ordersUpsell = json.loads(ordersUpsellData)

    addresses = []
    orderIdsUpsell = []
    orderIds = []
    mapAddressParentOrder = {}

    selectedtOrderIds = excludeOrdersNotSelected(user, orders, ordersUpsell)

    for orderUpsell in ordersUpsell:
        orderIdsUpsell.append(orderUpsell["id"])
        addresses.append(orderUpsell["address"])
        mapAddressParentOrder[orderUpsell["address"]] = orderUpsell["id"]

    parentOrders = Order.objects.filter(id__in=orderIdsUpsell).values("id")

    for parentOrder in parentOrders:
        parentOrder["has_child"] = True
        if parentOrder["id"] not in orderIds:
            orderIds.append(parentOrder["id"])

    Order.objects.bulk_update(parentOrders, ["has_child"])

    upsellOrders = (
        Order.objects.exclude(id__in=orderIdsUpsell)
        .filter(user_shop__user=user, address__in=addresses, status="AI")
        .values("id", "address")
    )

    for upsellOrder in upsellOrders:
        parentOrderId = upsellOrder["address"]
        upsellOrder["parent_order"] = parentOrderId
        if upsellOrder["id"] not in orderIds:
            orderIds.append(upsellOrder["id"])

    Order.objects.bulk_update(upsellOrders, ["parent_order"])

    for orderId in selectedtOrderIds:
        if orderId not in orderIds:
            orderIds.append(orderId)

    if len(orderIds) > 0:
        print(orderIds)
        processOrdersAndSendToQueue(user, orderIds)


def excludeOrdersNotSelected(user, selectedOrders, upsellOrdersIds) -> List[int]:
    """ Exclui pedidos não selecionados.
    :param user: O usuário.
    :param selectedOrders: Os pedidos selecionados.
    :param upsellOrdersIds: Os IDs dos pedidos upsell.
    
    :returns: Lista de IDs dos pedidos selecionados. """

    addresses = []
    finalSelectedOrders = []

    for order in selectedOrders:
        finalSelectedOrders.append(order["id"])
        addresses.append(order["address"])

    ordersWithUpsell = (
        Order.objects.filter(user_shop__user=user, address__in=addresses, status="AI")
        .values("address")
        .annotate(dcount=Count("address"))
        .filter(dcount__gt=1)
    )
    dataOrders = list(ordersWithUpsell)

    addressesToUpsell = []

    for order in dataOrders:
        addressesToUpsell.append(order["address"])

    ordersToUpsell = Order.objects.filter(
        user_shop__user=user, address__in=addressesToUpsell, status="AI"
    ).values("id")
    dataOrdersToUpsell = list(ordersToUpsell)

    for order in dataOrdersToUpsell:
        if order["id"] not in upsellOrdersIds and order["id"] in finalSelectedOrders:
            finalSelectedOrders.remove(order["id"])

    return finalSelectedOrders


@login_required(login_url="login")
def unlinkParentOrder(request) -> JsonResponse:
    """ Desconecta o pedido pai.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request em JSON. """

    try:
        if not request.POST:
            return
        orderId = request.POST.get("orderId")
        childOrder = Order.objects.get(id=orderId)
        anothersChildsOrders = Order.objects.filter(
            parent_order=childOrder.parent_order_id
        ).exclude(id=orderId)
        ordersToUpdate = []

        if not anothersChildsOrders:
            order = Order.objects.get(id=childOrder.parent_order_id)
            order.has_child = False
            ordersToUpdate.append(order)

        childOrder.parent_order = None

        ordersToUpdate.append(childOrder)

        Order.objects.bulk_update(ordersToUpdate, ["parent_order", "has_child"])
        return JsonResponse(
            {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
        )
    except Exception as e:
        capture_exception(e)
        return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)


@login_required(login_url="login")
def getPossibleParents(request) -> JsonResponse:
    """ Pega os possíveis pais dos pedidos.
    :param request: O objeto da request.
    
    :returns: Os pedidos em formato JSON. """

    try:
        user = request.user
        orderIdData = request.GET.get("orderId")
        orderId = json.loads(orderIdData)
        print("orderId")

        orderInfo = Order.objects.get(user_shop__user=user, id=orderId)
        orderlineitems = OrderLineItem.objects.filter(~Q(status="AI"), order__user_shop__user=user).values("order__id")
        availableParentOrders = (
            Order.objects.exclude(id=orderId)
            .filter(
                user_shop__user=user,
                address=orderInfo.address,
                parent_order__isnull=True,
            ).exclude(id__in=orderlineitems)
            .values(
                "name",
                "client_name",
                "client_phone",
                "cpf",
                "address",
                "status",
                "user_shopee__email",
                "shopee_checkout_id",
                "value",
                "boleto_url",
                "boleto_number",
                "boleto_due_date",
                "error",
                "error_date",
                "free_shipping",
                "canceled_at",
                "id",
                "sync_shopee",
                "created_date",
                "state",
                "street",
                "street_number",
            )
        )

        dataOrders = list(availableParentOrders)

        ordersMap = {}
        orderIds = []
        for order in dataOrders:
            order["olis"] = sql.get_orderlineitem_by_status(order["id"], "")
            order["otus"] = []
            ordersMap[order["id"]] = order
            orderIds.append(order["id"])

        response = {"data": list(ordersMap.values())}
        return JsonResponse(response, safe=False)
    except Exception as e:
        capture_exception(e)
        return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)


@login_required(login_url="login")
def linkParentOrder(request) -> JsonResponse:
    """ Conecta o pedido pai.
    :param request: O objeto da request.
    
    :returns: O estado da resposta da request. """

    try:
        if not request.POST:
            return
        parentOrderId = request.POST.get("parent_order_id")
        childOrderId = request.POST.get("child_order_id")
        parentOrderObj = Order.objects.get(id=parentOrderId)
        childOrderObj = Order.objects.get(id=childOrderId)
        parentOrderObj.has_child = True
        childOrderObj.parent_order = parentOrderObj

        ordersToUpdate = []
        ordersToUpdate.append(parentOrderObj)
        ordersToUpdate.append(childOrderObj)

        Order.objects.bulk_update(ordersToUpdate, ["parent_order", "has_child"])

        return JsonResponse(
            {"status_code": "200", "message": "Salvo com sucesso"}, safe=False
        )
    except Exception as e:
        print(e)
        capture_exception(e)
        return JsonResponse({"status_code": "404", "message": str(e)}, safe=False)
