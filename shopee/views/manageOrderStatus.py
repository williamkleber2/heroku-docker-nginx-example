from shopee.models import *
from shopeeApi.lmbdFnctApiCall import *
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q
from typing import Tuple, Dict, Union

def statusShopifyToAwaitingOrder(request) -> JsonResponse:
    """ Processa o status do pedido da Shopify para Aguardando Pedido.
    :param request: O objeto da request.
    
    :returns: Resposta JSON vazia. """

    if request.method == "POST":
        user = request.user
        ordersRequest = request.POST.get("orders")
        ordersJson = json.loads(ordersRequest)
        processOrdersAndSendToQueue(user, ordersJson)
        return JsonResponse({}, safe=False)


def processOrdersAndSendToQueue(user, orders) -> None:
    """ Processa os pedidos e os envia para a fila.
    :parma user: O usuário.
    :param orders: Os pedidos. """

    orderIdsToSend = {}
    userShop = UserShop.objects.filter(user=user)[0]
    for order in orders:
        olis = order['olis']
        for oli in olis:
            if oli['status'] == "AI":
                buildAddress(userShop, order)
                if oli['status'] == "FO":
                    oli['updated_date_fo'] = timezone.now()
                else:
                    if not order['parent_order']:
                        orderIdsToSend.setdefault(order['id'], [])
                        orderIdsToSend[order['id']].append(oli['id'])
                    oli['status'] = "AO"
                    oli['updated_date_ao'] = timezone.now()
            else:
                if not order['sync_shopee']:
                    if not order['parent_order']:
                        orderIdsToSend.setdefault(order['id'], [])
                        orderIdsToSend[order['id']].append(oli['id'])
                    oli['status'] = "AO"
                    oli['updated_date_ao'] = timezone.now()
            if not order['dropshopee_created_date']:
                order['dropshopee_created_date'] = timezone.now()

            if not oli['oli_vendor'] and not oli['droplinkfy_created_date']:
                order['droplinkfy_created_date'] = timezone.now()
                order['vendor'] = oli['product_vendor']
            elif oli['oli_vendor'] == 'shopee' and oli['droplinkfy_created_date']:
                order['droplinkfy_created_date'] = timezone.now()
        
            print(oli['status'])

        OrderLineItem.objects.bulk_update([OrderLineItem(pk=oli['id'],
                                                        status=oli['status'],
                                                        droplinkfy_created_date=oli['droplinkfy_created_date'],
                                                        updated_date_ao=oli['updated_date_ao'],
                                                        updated_date_fo=oli['updated_date_fo'],
                                                        ) for oli in olis], [
                                                            "status",
                                                            "updated_date_ao",
                                                            "updated_date_fo",
                                                        ])

    Order.objects.bulk_update(
        [Order(pk=order['id'], 
               status=order['status'],
               dropshopee_created_date=order['dropshopee_created_date'],
               error=order['error'],
              ) for order in orders],
        [
            "status",
            "dropshopee_created_date",
            "error",
        ],
    )  

    if orderIdsToSend:
        apiMakeOrderManually(orderIdsToSend)


def buildAddress(userShop, order) -> None:
    """ Cria um endereço baseado nos dados do pedido.
    :param userShop: O UserShop.
    :parma order: O pedido. """

    addressObj, addressHasError, checkoutError = parseAddress(
        userShop.checkout, order['address']
    )
    order['street'] = addressObj.get("street")
    order['street_number'] = addressObj.get("streetNumber")
    order['complement'] = addressObj.get("complement")
    if addressObj.get("neighborhood"):
        order['neighborhood'] = addressObj.get("neighborhood")
    if addressHasError:
        order['status'] = "FO"
        order['error'] = "Endereço incompleto: " + order.address
    elif checkoutError:
        order['status'] = "FO"
        order['error'] = "O checkout selecionado não corresponde ao checkout do pedido!"


def parseAddress(checkoutName, shippingAddress) -> Tuple[Dict[str, Union[str, int, bool]], bool, bool]:
    """ Dá um parse no endereço.
    :param checkoutName: O nome do checkout.
    :param shippingAddress: O endereço de envio.
    
    :returns: As informações do envio, se o endereço tem erros e, se tem erros no checkout. """

    addressHasError = False
    checkoutError = False
    checkoutName = checkoutName.upper()
    shippingInfo = {}
    shippingInfo["street"] = ""
    shippingInfo["streetNumber"] = ""
    shippingInfo["complement"] = ""
    shippingInfo["neighborhood"] = ""

    try:
        if checkoutName == "YAMPI":
            addressRaw = shippingAddress.split(",")

            if not addressRaw[0]:
                addressHasError = True
            else:
                shippingInfo["street"] = addressRaw[0]

            if not addressRaw[1]:
                addressHasError = True
            else:
                shippingInfo["streetNumber"] = addressRaw[1]

            shippingInfo["complement"] = ""
            for i in range(2, len(addressRaw)):
                shippingInfo["complement"] = addressRaw[i]

        elif checkoutName == "CARTX":
            addressRaw = shippingAddress.split(",")

            if not addressRaw[0]:
                addressHasError = True
            else:
                shippingInfo["street"] = addressRaw[0]

            if not addressRaw[1]:
                addressHasError = True
            else:
                addressComplementRaw = addressRaw[1].split("-")
                try:
                    numbers = [
                        int(s) for s in addressComplementRaw[0].split() if s.isdigit()
                    ]
                    shippingInfo["streetNumber"] = numbers[0]
                except:
                    numbers = addressComplementRaw[0].split()
                    shippingInfo["streetNumber"] = numbers[0]
                if len(addressComplementRaw) > 1:
                    shippingInfo["complement"] = addressComplementRaw[1]

        elif checkoutName == "CLOUDFOX":
            addressRaw = shippingAddress.split("-")

            if not addressRaw[0]:
                addressHasError = True
            else:
                shippingInfo["street"] = addressRaw[0].strip()

            if not addressRaw[1]:
                addressHasError = True
            else:
                shippingInfo["streetNumber"] = int(addressRaw[1])

            if len(addressRaw) > 3:
                if addressRaw[3]:
                    shippingInfo["neighborhood"] = addressRaw[3].strip()
                if addressRaw[2]:
                    shippingInfo["complement"] = addressRaw[2].strip()
            else:
                if addressRaw[2]:
                    shippingInfo["neighborhood"] = addressRaw[2].strip()

        elif checkoutName == "HUBSALES":
            addressRaw = shippingAddress.split(",")

            if not addressRaw[0]:
                addressHasError = True
            else:
                shippingInfo["street"] = addressRaw[0]

            if not addressRaw[1]:
                addressHasError = True
            else:
                addressComplementRaw = addressRaw[1].split("-")
                try:
                    numbers = [
                        int(s) for s in addressComplementRaw[0].split() if s.isdigit()
                    ]
                    shippingInfo["streetNumber"] = numbers[0]
                except:
                    numbers = addressComplementRaw[0].split()
                    shippingInfo["streetNumber"] = numbers[0]
                if len(addressComplementRaw) > 1:
                    shippingInfo["complement"] = addressComplementRaw[1].strip()

        elif checkoutName == "CONVERTE.ME":
            addressRaw = shippingAddress.split(",")
            if not addressRaw[0]:
                addressHasError = True
            else:
                shippingInfo["street"] = addressRaw[0]

            if not addressRaw[1]:
                addressHasError = True
            else:
                addressComplementRaw = addressRaw[1].split()
                try:
                    numbers = [
                        int(s) for s in addressComplementRaw[0].split() if s.isdigit()
                    ]
                    shippingInfo["streetNumber"] = numbers[0]
                except:
                    numbers = addressComplementRaw[0].split()
                    shippingInfo["streetNumber"] = numbers[0]

                if len(addressComplementRaw) > 1:
                    shippingInfo["complement"] = " ".join(addressComplementRaw[1:])
            if len(addressRaw) > 2:
                if addressRaw[2]:
                    shippingInfo["neighborhood"] = addressRaw[2].strip()

    except Exception as e:
        checkoutError = True
    return shippingInfo, addressHasError, checkoutError
