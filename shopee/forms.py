from django import forms
from .models import *


class UserShopUserForm(forms.Form):
    """ Formulário para o UserShop. """

    class Meta:
        """ Meta classe. """

        model = UserShop
        fields = ["checkout", "free_shipping", "shopify_name", "shopify_key", "working"]


class UserShopeeForm(forms.Form):
    """ Formulário para o UserShopee. """

    class Meta:
        """ Meta classe. """

        model = UserShopee
        fields = "__all__"


class UserBillingDataForm(forms.Form):
    """ Formulário para os dados de cobrança do usuário. """

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    doc_type = forms.CharField(max_length=5)
    document = forms.CharField(max_length=30)
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=120)
    address2 = forms.CharField(max_length=30, required=False)
    city = forms.CharField(max_length=85)
    state = forms.CharField(max_length=85)
    phone = forms.CharField(max_length=20)


class ShopeeProductVariant(forms.Form):
    """ Formulário para a variante do produto Shopee. """

    url = forms.URLField(max_length=1000)
    amount = forms.IntegerField(min_value=1)
    vendor = forms.ChoiceField(choices=VENDOR_CHOICES)


class VendorProductCreate(forms.Form):
    """ Formulário para a criação do produto do Vendor. """

    url = forms.URLField(max_length=1000)
    vendor = forms.ChoiceField(choices=VENDOR_CHOICES)
    amount = forms.IntegerField(min_value=1)
    variant_id = forms.CharField(max_length=250)
    option_name = forms.CharField(max_length=75)
    option_value = forms.CharField(max_length=75)
    values = forms.JSONField()
    variation = forms.JSONField()
    carrier = forms.CharField(required=False)
    carriers = forms.CharField(required=False)


class AliUserForm(forms.Form):
    """ Formulário para o AliUser. """

    email = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)

