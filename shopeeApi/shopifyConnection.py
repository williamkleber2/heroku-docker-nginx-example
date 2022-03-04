import requests
from shopee.models import *
import traceback
from shopeeApi.lmbdFnctApiCall import *
import json
from typing import Tuple

def createLocation(userShop) -> None:
    """ Cria um local.
    :param userShop: Os dados do UserShop. """

    try:
        locations = getLocation(userShop)
        for location in locations.get("locations"):
            if location["legacy"] == False:
                locationId = location.get("id")
        if not locationId:
            return
        userShop.shopify_location_id = locationId
    except Exception as e:
        raise Exception(e)


def getLocation(userShop) -> Any:
    """ Pega um local.
    :param userShop: Os dados do UserShop.
    
    :returns: A resposta em formato JSON. """

    print("[getLocation]")
    headers = {"X-Shopify-Access-Token": userShop.shopify_key}
    response = requests.get(
        "https://" + userShop.shopify_name + "/admin/api/2021-01/locations.json",
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise Exception("Loja fora do ar")
    else:
        raise Exception(
            "Falha em capturar os locations da loja: " + userShop.shopify_name
        )


def createWebhook(userShop) -> None:
    """ Cria um Webhook.
    :param userShop: Os dados do UserShop. """

    try:
        createShopifyWebhooks(userShop)
    except Exception as e:
        raise Exception(e)


def deleteWebhook(userShop) -> None:
    """ Deleta um Webhook.
    :param userShop: Os dados do UserShop. """

    deleteShopifyWebhooks(userShop)


def verifyShopifyDomaindAndKey(userShop) -> bool:
    """ Verifica o domínio e a chave da Shopify.
    :param userShop: Os dados do UserShop.
    
    :returns: Verdadeiro ou falso se o código de status é 200.  """

    headers = {"X-Shopify-Access-Token": userShop.shopify_key}
    try:
        response = requests.get(
            "https://" + userShop.shopify_name + "/admin/api/2021-01/webhooks.json",
            headers=headers,
            timeout=3,
        )
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False


def checkShopifyProductsPermission(userShop) -> Tuple[bool, str]:
    """ Checa as permissões dos produtos da Shopify.
    :param userShop: Os dados do UserShop.
    
    :param returns: Tupla com verdadeiro ou falso e uma mensagem de resposta do
    código de status da request. """

    headers = {"X-Shopify-Access-Token": userShop.shopify_key}
    url = (
        "https://"
        + userShop.shopify_name
        + "/admin/api/2021-01/products.json?limit=250"
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True, "Sucesso"
    else:
        if response.status_code == 403:
            return (
                False,
                "Não foi possivel sincronizar porque o app privado não tem permissão de leitura dos produtos!",
            )
        return False, "Erro inesperado, contactar administrador."


def checkShopifyPermissions(userShop) -> Tuple[bool, str]:
    """Checa as permissões da Shopify.
    :param userShop: Os dados do UserShop.
    
    :param returns: Tupla com verdadeiro ou falso e uma mensagem de resposta do
    código de status da request. """

    print(userShop.shopify_name)
    headers = {"X-Shopify-Access-Token": userShop.shopify_key}
    url = "https://" + userShop.shopify_name + "/admin/oauth/access_scopes.json"
    response = requests.get(url, headers=headers)
    print(response.text)
    if response.status_code == 200:
        required_permissions = [
            "read_products",
            "write_orders",
            "read_all_orders",
            "read_orders",
            "write_inventory",
            "read_inventory",
        ]
        mapPermissionMsg = {
            "read_products": "Leitura de produtos",
            "write_orders": "Gravação de pedidos",
            "read_orders": "Leitura de pedidos",
            "read_all_orders": "Leitura de todos os pedidos",
            "write_inventory": "Leitura de Estoque",
            "read_inventory": "Gravação de Estoque",
        }
        access_scopes = json.loads(response.text).get("access_scopes")
        missing_permissions = [
            "read_products",
            "write_orders",
            "read_all_orders",
            "read_orders",
            "write_inventory",
            "read_inventory",
        ]
        for access in access_scopes:
            if access.get("handle") in required_permissions:
                missing_permissions.remove(access.get("handle"))

        if len(missing_permissions) > 0:
            error_message = "Permissões em falta no seu app privado do shopify: "
            error_permissions = []
            for missingPerm in missing_permissions:
                error_permissions.append(mapPermissionMsg.get(missingPerm))

            error_message += ", ".join(error_permissions)
            return False, error_message
        return True, "Sucesso"
    else:
        return False, "Erro inesperado, contactar administrador."
