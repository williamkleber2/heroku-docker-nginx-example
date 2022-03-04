from shopeeApi.shopifyConnection import createWebhook
from shopeeApi.shopifyConnection import createLocation
from shopeeApi.shopifyConnection import deleteWebhook
from shopeeApi.lmbdFnctApiCall import upsertShopifyProducts
from shopeeApi import stripeApi


def postSaveUserShop(sender, instance, created, **kwargs) -> None:
    """ Faz um upsert em um UserShop.
    :param sender: O remetente.
    :param instance: A instância.
    :param created: Se já está criado.
    :param kwargs: As kwargs. """

    if created:
        upsertShopifyProducts(instance)

    if instance.working and instance.working_admin:
        createWebhook(instance)
    else:
        deleteWebhook(instance)

def postSaveUserBillingData(sender, instance, created, **kwargs) -> None:
    """ Faz um upsert nos dados de cobrança do usuário.
    :param sender: O remetente.
    :param instance: A instância.
    :param created: Se já está criado.
    :param kwargs: As kwargs. """

    stripeApi.set_customer_billing_data(instance)


def preSaveUserShop(sender, instance, **kwargs) -> None:
    """ Pré-salva um UserShop.
    :param sender: O remetente.
    :param instance: A instância.
    :param kwargs: As kwargs. """

    if instance.working and instance.working_admin:
        createLocation(instance)
