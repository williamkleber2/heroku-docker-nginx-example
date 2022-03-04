from datetime import datetime
import hashlib
import typing as t

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.enums import TextChoices
from django.db.models.fields.related import ForeignKey
from django.forms.fields import ChoiceField
from django.utils import timezone

from datetime import datetime
from django.contrib.auth.models import User
from django_cpf_cnpj.fields import CPFField, CNPJField

DEFAULT_VENDOR = "shopee"
COLOR_CHOICES = (
    # https://getbootstrap.com/docs/4.0/utilities/colors/
    ("primary", "Azul"),
    ("secondary", "Cinza"),
    ("success", "Verde"),
    ("danger", "Vermelho"),
    ("warning", "Amarelo"),
    ("info", "Ciano"),
    # ("light",       "Branco"),
    ("dark", "Preto"),
    ("white", "Branco"),
)


VENDOR_CHOICES = (
    ("shopee", "shopee"),
    ("ali", "ali"),
)

CANCELLATTION_STATUS = (
    ("NC", "Não cancelado"),
    ("WC", "A cancelar"),
    ("C", "Cancelado"),
)

VendorField = lambda **options: models.CharField(
    max_length=25,
    choices=VENDOR_CHOICES,
    default=DEFAULT_VENDOR,
    **options,
)
PriceField = lambda **options: models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=options.pop("null", True),
    default=options.pop("default", None),

    **options,
)


class Error(Exception):
    """ Classe de erro geral. """

    pass


class DropShopeeError(Error):
    """ Classe de erro da DropShopee. """

    pass


class DropShopeeUserError(Error):
    """ Classe de erro de usuário da DropShopee. """

    pass


class DropShopeeUserBannedError(Error):
    """ Classe de erro de usuário banido da DropShopee. """

    pass


class DropShopeeProxyError(Error):
    """ Classe de erro de proxy da DropShopee. """

    pass


class Carrier(models.Model):
    """ Modelo para o Carrier. """

    id = models.CharField(max_length=70, primary_key=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    vendor = models.CharField(max_length=15, default="shopee", choices=VENDOR_CHOICES)

class UserInfo(models.Model):
    """ Modelo para o as informações do usuário. """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    crisp_token = models.CharField(max_length=100, blank=True, null=True)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    order_memo = models.TextField(max_length=512, blank=True, null=True, default="")


class Profile(models.Model):
    """ Modelo para o perfil do usuário. """

    class XpTimes(TextChoices):
        """ Classe de escolhas de tempo de experiência com Dropshipping. """

        ONE_TO_THREE_MONTH = 'ONE_TO_THREE_MONTH', '1 a 3 meses'
        THREE_TO_SIX_MONTH = 'THREE_TO_SIX_MONTH', '3 a 6 meses'
        SIX_TO_TWELVE_MONTH = 'SIX_TO_TWELVE_MONTH',  '6 a 12 meses'
        MORE_THAN_TWELVE_MONTH = 'MORE_THAN_TWELVE_MONTH', 'Mais de 12 meses'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=4, null=True, blank=True)
    last_cancel_request_datetime = models.DateTimeField(null=True, blank=True)
    dropshipping_xp_time = models.CharField(max_length=50, null=True, blank=True, choices=XpTimes.choices)
    referral = models.CharField(max_length=255, null=True, blank=True)

class UserBillingData(models.Model):
    """ Modelo para os dados de cobrança do usuário. """

    user = models.ForeignKey(get_user_model(), models.CASCADE)
    doc_type = models.CharField(max_length=5, choices=[('cpf', 'CPF'), ('cnpj', 'CNPJ')])
    cnpj = CNPJField(masked=True, blank=True, null=True)
    cpf = CPFField(masked=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=120)
    address_number = models.CharField(max_length=6, default='')
    address2 = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=85)
    state = models.CharField(max_length=85)
    phone = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=20)


class UserShop(models.Model):
    """ Modelo para o UserShop. """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    checkout = models.CharField(max_length=255, blank=False)
    free_shipping = models.BooleanField(default=False)
    shopify_name = models.CharField(unique=True, max_length=255, null=False)
    shopify_key = models.CharField(max_length=255, blank=False, null=False)
    shopify_shared_secret = models.CharField(max_length=255, blank=False, null=False)
    working = models.BooleanField(default=False)
    working_admin = models.BooleanField(default=True)
    automatic_upsell = models.BooleanField(default=True)
    notify_order_fulfillment = models.BooleanField(default=True)
    shopify_location_id = models.CharField(max_length=255, blank=True, null=True)
    tracking_url = models.CharField(max_length=255, blank=False, null=False)
    last_products_sync_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )
    products_sync_requests = models.IntegerField(default=0, blank=False)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return str(self.user) + self.shopify_name


class UserShopee(models.Model):
    """ Modelo para o UserShopee. """

    DEACTIVATE_STATUS = (
        ('IL', 'Login incorreto'),
        ('IP', 'Proxy incorreta'),
        ('IT', 'Token inválido'),
        ('TE', 'Erro ao finalizar transação'),
        ('M', 'Manual'),
        ('BA', 'Conta banida'),
        ('EL', 'Login expirou'),
        ('FSL', 'Limite de Frete Grátis'),
        ('EL', 'Login Expirado'),
    )
    CREATED_STATUS = (
        ("C", "Created"),
        ("BC", "Being Created"),
        ("NC", "Not Created"),
        ("ENV", "Email not validated"),
        ("EAR", "Email already exists"),
        ("TNV", "Telephone not validated"),
    )
    ACCOUNT_TYPES = (
        ("G", "Google"),
        ("O", "Other"),
    )
    email = models.CharField(unique=True, max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    proxy = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    proxy_login = models.CharField(max_length=255, blank=True, null=True)
    proxy_password = models.CharField(max_length=255, blank=True, null=True)
    fingerprint = models.CharField(max_length=255, blank=True, null=True)
    user_shop = models.ForeignKey(
        UserShop,
        on_delete=models.CASCADE,
        related_name="shopeeUsers",
        blank=True,
        null=True,
    )
    activated = models.BooleanField(default=False)
    last_free_shipping_purchase = models.DateTimeField(blank=False, null=True)
    last_purchase = models.DateTimeField(blank=False, null=True)
    spc_f = models.CharField(max_length=255,blank=True,null=True)
    deactivate_status = models.CharField(default='', max_length=3, choices=DEACTIVATE_STATUS, blank=True, null=False)
    captcha_signature = models.CharField(max_length=2500,blank=True,null=True)
    identity_token = models.CharField(max_length=2500,blank=True,null=True)
    created_status = models.CharField(max_length=3, choices=CREATED_STATUS, blank=True)
    sms_api_key = models.CharField(max_length=100, blank=True, null=True)
    creation_request_date = models.DateTimeField(blank=False, null=True)
    last_purchase_date = models.DateTimeField(blank=False, null=True)
    account_type = models.CharField(
        max_length=5, choices=ACCOUNT_TYPES, default="other"
    )
    spc_ec = models.CharField(max_length=500, blank=True, null=True)
    device_sz_fingerprint = models.CharField(max_length=500, blank=True, null=True)
    vendor = models.CharField(max_length=15, default="shopee", choices=VENDOR_CHOICES)
    banned_at = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self) -> str:
        """ Retorna a representação string do email instância do objeto. """

        return self.email

    @property
    def is_spc_ec_expired(self) -> bool:
        """Returns if `spc_ec` is expired (only google accounts)."""
        return self.deactivate_status == "EL"  # type: ignore

    @property
    def can_be_logged(self) -> bool:
        """Returns if `email`, `password` and `spc_f` fields is not
        empty or `None`.
        """
        return all((self.email, self.spc_f))  # type: ignore

    @property
    def encrypted_password(self) -> t.Optional[str]:
        """Returns the `password` field ecrypted using MD5 and SHA256."""

        s: str = self.password  # type: ignore
        if not s:
            return

        s_MD5 = hashlib.md5(s.encode("UTF-8"))
        s_MD5 = s_MD5.hexdigest().encode("UTF-8")

        sha256_hash = hashlib.sha256()
        sha256_hash.update(s_MD5)

        return sha256_hash.hexdigest()

    def serialize_to_extension(self) -> t.Dict[str, t.Any]:
        """ Serializa o objeto para a extensão no navegador.
        
        :returns: A serialização do objeto. """

        return {
            "valid": self.can_be_logged,
            "type": self.account_type,
            "expired": self.is_spc_ec_expired,

            "email": self.email,
            "cookie": self.spc_f,
            "password": self.encrypted_password,

            "port": self.port,
            "proxy": self.proxy,
            "proxylogin": self.proxy_login,
            "proxypassword": self.proxy_password,

            "vendor": self.vendor,
        }

    class Meta:
        """ Classe meta. """

        permissions = [
            ("create_user_on_shopee", "Can create a user directly on shopee"),
        ]


class UserShopeeError(models.Model):
    """ Modelo para o erro do UserShopee. """

    user_shopee = models.ForeignKey(
        UserShopee, on_delete=models.CASCADE, related_name="shopeeUsersErros"
    )
    date = models.DateTimeField(default=timezone.now, blank=False)
    message = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.user_shopee


class Customer(models.Model):
    """ Model para o customer. """

    id = models.CharField(max_length=70, primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created = models.BigIntegerField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)


class PercentagePay(models.Model):
    """ Model para o PercentagePay. """

    STATUS = (
        ("paid", "Pago"),
        ("unpaid", "Não Pago"),
        ("past_due", "Pagamento atrasado"),
        ("refunded", "Reembolsado"),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS)
    retry = models.IntegerField(blank=False, default=3)
    created_at = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    percentage = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_intent_id = models.CharField(
        max_length=70, unique=True, blank=True, null=True
    )
    error_message = models.CharField(max_length=255, blank=True, null=True)
    last_manual_pay_date = models.DateField(default=timezone.now, blank=True, null=True)
    manual_pay_requests = models.IntegerField(default=0, blank=True, null=True)


class Order(models.Model):
    """ Model para o pedido. """
    
    STATUS = (
        ("AO", "Aguardando Pedido"),
        ("AP", "Aguardando Pagamento"),
        ("APS", "Aguardando Pagamento Fornecedor"),
        ("AS", "Aguardando Envio"),
        ("AF", "Aguardando Processamento"),
        ("F", "Processado"),
        ("C", "Cancelado"),
        ("FO", "Pedidos Falhadas"),
        ("DO", "Pedido Deletado"),
        ("AI", "Aguardando Integração"),
    )
    id = models.CharField(max_length=70, primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    user_shopee = models.ForeignKey(
        UserShopee,
        on_delete=models.CASCADE,
        related_name="userShopeeOrders",
        blank=True,
        null=True,
    )
    user_shop = models.ForeignKey(
        UserShop, on_delete=models.CASCADE, related_name="userShopOrders"
    )
    shopee_checkout_id = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    street_number = models.CharField(max_length=255, blank=True, null=True)
    complement = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=500, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_phone = models.CharField(max_length=255, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    boleto_url = models.CharField(max_length=255, blank=True, null=True)
    boleto_number = models.CharField(max_length=255, blank=True, null=True)
    boleto_due_date = models.DateField(default=timezone.now, blank=True, null=True)
    paid = models.BooleanField(default=False)
    error = models.CharField(max_length=500, blank=True, null=True)
    free_shipping = models.BooleanField(default=False)
    status = models.CharField(max_length=3, choices=STATUS)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    updated_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    sync_shopee = models.BooleanField(default=False)
    error_date = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    dropshopee_created_date = models.DateTimeField(
        default=timezone.now, blank=True, null=True
    )
    dropshopee_deleted_date = models.DateTimeField(blank=True, null=True)
    updated_date_ao = models.DateTimeField(blank=False, null=True)
    updated_date_ap = models.DateTimeField(blank=False, null=True)
    updated_date_aps = models.DateTimeField(blank=False, null=True)
    updated_date_as = models.DateTimeField(blank=False, null=True)
    updated_date_af = models.DateTimeField(blank=False, null=True)
    updated_date_f = models.DateTimeField(blank=False, null=True)
    updated_date_c = models.DateTimeField(blank=False, null=True)
    updated_date_fo = models.DateTimeField(blank=False, null=True)
    percentage_pay = models.ForeignKey(
        PercentagePay,
        on_delete=models.SET_NULL,
        related_name="percentagePayOrderss",
        blank=True,
        null=True,
    )
    has_child = models.BooleanField(default=False)
    parent_order = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="childOrders",
        blank=True,
        null=True,
    )
    users_without_valid_voucher = models.TextField(blank=False, null=True)
    shipping_price = PriceField()

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.name


class Product(models.Model):
    """Represents a Shopify product.

    Attributes
    ----------
    id: CharField
        The product ID in our database. Max 70 characters.
    gid: CharField
        The Shopify product ID. Max 70 characters.
    title: CharField
        The name of the product. Max 255 characters.
    handle: CharField
        A unique human-friendly string for the product. Automatically
        generated from the product's title. Used by the Liquid
        templating language to refer to objects. Max 255 characters.
    published_at: DateTimeField, optional
    created_at: DateTimeField
    updated_at: DateTimeField, optional
    user_shop: ForeignKey[UserShop]
        The Shopify shop owner of the product.
    """
    id = models.CharField(max_length=70, primary_key=True)
    gid = models.CharField(max_length=70, unique=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    handle = models.CharField(max_length=255, blank=False, null=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=False, null=False)
    updated_at = models.DateTimeField(blank=True, null=True)
    user_shop = models.ForeignKey(
        UserShop, on_delete=models.CASCADE, related_name="userShopProductsShopify"
    )

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.title


class ProductImage(models.Model):
    """Represets an image product from a Shopify product.

    Attributes
    ----------
    id: CharField
        The Shopify ID the image. Max 70 characters.
    created_at: DateTimeField, optional
    updated_at: DateTimeField, optional
    product_shopify: ForeignKey[Product]
        The Shopify product owner of the image.
    src: CharField, optional
        URL to the image.

        According to `getShopifyProducts` lambda, this field never
        comes empty. Probably this is a mistake, you can check it in
        `60a7e87` commit.
    """
    id = models.CharField(max_length=70, primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    product_shopify = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="shopifyProductImages"
    )
    src = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.id


class ProductVariant(models.Model):
    """Represets an variation of a Shopify product.

    id: CharField
        According to `getShopifyProducts`, this field is the same than
        `gid`.
    gid: CharField
        The ID of variation in Shopify.
    title: CharField, optional
        The title of the product variant. The title field is a
        concatenation of the option1, option2, and option3 fields.
    sku: CharField, optional
        A unique identifier for the product variant in the shop.
    price: DecimalField
    compare_at_price: DecimalField, optional
    product_shopify: ForeignKey[Product]
    created_at: DateTimeField, optional
    updated_at: DateTimeField, optional
    inventory_item_id: CharField, optional
        The unique identifier for the inventory item, which is used in
        the Inventory API - Shopify - to query for inventory
        information.
    is_processable: BooleanField, default=True
    """
    id = models.CharField(max_length=70, primary_key=True)
    gid = models.CharField(max_length=70, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_shopify = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="productVariants"
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    inventory_item_id = models.CharField(max_length=255, blank=True, null=True)
    is_processable = models.BooleanField(default=True, null=False)
    vendor = models.CharField(max_length=15, default="shopee", choices=VENDOR_CHOICES)
  
    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.title

    def to_dict_json(self) -> t.Dict[str, t.Any]:
        """ Converte o objeto de dicionário para JSON.
        
        :returns: O dicionário convertido para JSON-like. """

        return {
            "id": self.id,
            "gid": self.gid,
            "title": self.title,
            "sku": self.sku,
            "price": self.price,
            "compare_at_price": self.compare_at_price,
            "product_shopify": self.product_shopify__title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ProductShopee(models.Model):
    """ Model para o produto Shopee. """

    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="productVariantsShopee"
    )
    shopee_url = models.CharField(max_length=500, blank=True, null=True)
    quantity = models.IntegerField(blank=False)
    shop_id = models.BigIntegerField(blank=False, null=True)
    item_id = models.BigIntegerField(blank=False, null=False)
    model_id = models.CharField(max_length=150, blank=False, null=True)
    option_name = models.CharField(max_length=255, blank=True, null=True)
    vendor = VendorField()
    carrier_id = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.shopee_url

    def to_dict_json(self) -> t.Dict[str, t.Any]:
        """ Converte o objeto de dicionário para JSON.
        
        :returns: O dicionário convertido para JSON-like. """

        return {
            "shopee_url": self.shopee_url,
            "quantity": self.quantity,
            "shop_id": self.shop_id,
            "item_id": self.item_id,
            "model_id": self.model_id,
            "option_name": self.option_name,
        }



class Boleto(models.Model):
    """ O model para o boleto. """

    url = models.URLField(max_length=1750)
    number = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateField(default=timezone.now, blank=True, null=True)
    paid = models.BooleanField(default=False)
    value = PriceField(blank=False, null=False)
    created_at  = models.DateTimeField(auto_now_add=True)



class OrderLineItem(models.Model):
    """Represents an item from `line_items` of an Order in Shopify.

    Attributes
    ----------
    id: CharField
    order: ForeignKey[Order]
    product_variant: ForeignKey[ProductVariant]
    quantity: IntegerField, default=1
    title: CharField, optional
    name: CharField, optional
    product_variant_id_text: CharField, optional
    """
    id = models.CharField(max_length=70, primary_key=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderLineItens"
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="shopifyVariants",
        null=True,
    )
    quantity = models.IntegerField(blank=False, default=1)
    title = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    product_variant_id_text = models.CharField(max_length=70, blank=True, null=True)
    updated_date_ao = models.DateTimeField(blank=False, null=True)
    updated_date_ap = models.DateTimeField(blank=False, null=True)
    updated_date_aps = models.DateTimeField(blank=False, null=True)
    updated_date_as = models.DateTimeField(blank=False, null=True)
    updated_date_af = models.DateTimeField(blank=False, null=True)
    updated_date_f = models.DateTimeField(blank=False, null=True)
    updated_date_c = models.DateTimeField(blank=False, null=True)
    updated_date_fo = models.DateTimeField(blank=False, null=True)
    percentage_pay = models.ForeignKey(
        PercentagePay,
        on_delete=models.SET_NULL,
        related_name="percentagePayOrdersLineItem",
        blank=True,
        null=True,
    )
    canceled_at = models.DateTimeField(blank=True, null=True)
    free_shipping = models.BooleanField(default=False)
    sync_shopee = models.BooleanField(default=False)
    droplinkfy_created_date = models.DateTimeField(blank=True, null=True, default=None)
    droplinkfy_deleted_date = models.DateTimeField(blank=True, null=True, default=None)
    status = models.CharField(max_length=3, choices=Order.STATUS, default="AI")
    user_shopee = models.ForeignKey(
        UserShopee,
        on_delete=models.CASCADE,
        related_name="userShopeeOrdersLineItem",
        blank=True,
        null=True,
    )
    price = PriceField()
    cancellation_status = models.CharField(
        max_length=2,
        choices=CANCELLATTION_STATUS,
        default="NC",
    )
    vendor = VendorField(blank=True, null=True)
    error_date = models.DateTimeField(blank=True, null=True)
    error = models.CharField(max_length=500, blank=True, null=True)
    shopee_checkout_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.order) + " - " + str(self.product_variant)


class OrderPurchase(models.Model):
    """ Model para a OrderPurchase. """

    LIST_TYPE = (
        ("9", "A Pagar"),
        ("7", "A Enviar"),
        ("8", "A Receber"),
        ("3", "Concluído"),
        ("4", "Cancelado"),
    )
    SHOPEE_STATUS = (
        ("1", "A Pagar"),
        ("2", "A Enviar"),
        ("3", "A Receber"),
        ("4", "Concluído"),
        ("5", "Cancelado"),
    )
    user_shop = models.ForeignKey(
        UserShop, on_delete=models.CASCADE, related_name="userShopOrderPurchases"
    )
    user_shopee = models.ForeignKey(
        UserShopee, on_delete=models.CASCADE, related_name="userShopeeOrderPurchases"
    )
    shopee_order_id = models.CharField(max_length=70, primary_key=True)
    order_id = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderPurchases"
    )
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    list_type = models.CharField(max_length=1, choices=LIST_TYPE)
    status = models.CharField(max_length=1, choices=SHOPEE_STATUS)
    purchase_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    shopee_product_name = models.CharField(max_length=500, blank=True, null=True)
    shopee_product_variant = models.CharField(max_length=255, blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    canceled_status = models.CharField(max_length=500, blank=True, null=True)
    shipping_fee = models.BigIntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=70, blank=True, null=True)
    vendor = VendorField()
    paid = models.BooleanField(default=False)
    boleto_id = models.ForeignKey(
        Boleto,
        on_delete=models.CASCADE,
        default=None,
        null=True
    )



class OrderPurchaseLineItem(models.Model):
    """ Model para a OLI. """

    STATUS = (
        ("1", "A Pagar"),
        ("2", "A Enviar"),
        ("3", "A Receber"),
        ("4", "Concluído"),
        ("5", "Cancelado"),
    )
    user_shop = models.ForeignKey(
        UserShop,
        on_delete=models.CASCADE,
        related_name="userShopOrderPurchaseLineItems",
    )
    user_shopee = models.ForeignKey(
        UserShopee,
        on_delete=models.CASCADE,
        related_name="userShopeeOrderPurchaseLineItems",
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderPurchaseLineItems"
    )
    order_purchase = models.ForeignKey(
        OrderPurchase,
        on_delete=models.CASCADE,
        related_name="userShopeeOrderPurchaseLineItems",
    )
    status = models.CharField(max_length=1, choices=STATUS)
    purchase_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    shopee_product_name = models.CharField(max_length=500, blank=True, null=True)
    shopee_product_variant = models.CharField(max_length=255, blank=True, null=True)
    shopee_shop_id = models.BigIntegerField(blank=False, null=True)
    shopee_item_id = models.BigIntegerField(blank=False, null=False)
    shopee_model_id = models.CharField(max_length=150, blank=False, null=True)
    quantity = models.IntegerField(blank=False, default=1)
    shopee_original_price = models.BigIntegerField(blank=False, null=False)
    shopee_item_price = models.BigIntegerField(blank=False, null=False)
    shopee_order_price = models.BigIntegerField(blank=False, null=False)
    order_line_item = models.ForeignKey(
        OrderLineItem,
        on_delete=models.CASCADE,
        related_name="orderLineItemOrderPurchaseLineItems",
        blank=True,
        null=True,
    )
    vendor = VendorField()
    product_image = models.URLField(max_length=1750, null=True,
                                    blank=True, default=None)
    shipping_price = PriceField()
    carrier_id = models.ForeignKey(
        Carrier,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )


class Webhook(models.Model):
    """Represents a Shopify Webhook.

    Note
    ----
    This model is most used from AWS Lambdas.
    Check `createShopifyWebhooks`.

    Attributes
    ----------
    id: CharField
        The ID of Webhook.
    address: CharField, optional
    topic: CharField, optional
        Event that triggers the webhook. Check Shopify documentation.
    created_at: DateTimeField, optional
    updated_at: DateTimeField, optional
    format: CharField, optional
        Format of the Webhook. Useless field.
        This field is filled with only the value `"json"`.
    api_version: CharField, optional
        The Shopify API version.
    user_shop: ForeignKey[UserShop]
        The Shop owner of the webhook.
    """
    id = models.CharField(max_length=70, primary_key=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    format = models.CharField(max_length=50, null=True, blank=True)
    api_version = models.CharField(max_length=255, null=True, blank=True)
    user_shop = models.ForeignKey(
        UserShop, on_delete=models.CASCADE, related_name="webhooks"
    )

class Subscription(models.Model):
    """ Model para a inscrição. """

    id = models.CharField(max_length=70, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    default_payment_method = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    current_period_start = models.BigIntegerField(blank=True, null=True)
    current_period_end = models.BigIntegerField(blank=True, null=True)


class OrderRaw(models.Model):
    """ Model para os dados crus do pedido. """

    id = models.CharField(max_length=70, primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    user_shop = models.ForeignKey(
        UserShop, on_delete=models.CASCADE, related_name="userShopOrdersRaw"
    )
    address = models.CharField(max_length=500, blank=True, null=True)
    neighborhood = models.CharField(max_length=500, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_phone = models.CharField(max_length=255, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    updated_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    financial_status = models.CharField(max_length=255, blank=True, null=True)
    fulfillment_status = models.CharField(max_length=255, blank=True, null=True)
    gateway = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return self.name


class OrderRawLineItem(models.Model):
    """ Model para os dados crus da OLI. """

    id = models.CharField(max_length=70, primary_key=True)
    order = models.ForeignKey(
        OrderRaw, on_delete=models.CASCADE, related_name="orderRawLineItens"
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="orderRawShopifyVariants",
        null=True,
    )
    quantity = models.IntegerField(blank=False, default=1)
    title = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    product_variant_id_text = models.CharField(max_length=70, blank=True, null=True)

    def __str__(self) -> str:
        """ Retorna a representação string da instância do objeto. """

        return str(self.order) + " - " + str(self.product_variant)


class News(models.Model):
    """Represents a news.

    Note
    ----
    This model is used to "send" a notification for *all* users.

    Attributes
    ----------
    url: URLField, optional
        URL used to redirect the user when it clicks on the news.
    brief: CharField
        The short description of the news. Max 150 characters.
    icon: CharField, default="star"
        Icon of the news, choose one from https://feathericons.com.
    color: CharField, default="info"
        Color of the news, see `COLOR_CHOICES`.
    created_at: DateTimeField
    """
    url         = models.URLField(blank=True, help_text="Opcional.")
    brief       = models.CharField(max_length=150)
    icon        = models.CharField(max_length=15, default="star",
                                   help_text="https://feathericons.com")
    color       = models.CharField(max_length=9, default="info",
                                   choices=COLOR_CHOICES)
    created_at  = models.DateTimeField(auto_now_add=True)


class UserNewsNotification(models.Model):
    """Represents a news notification for a specified user.

    Note
    ----
    This model is used when the user read a `News`.

    Attributes
    ----------
    user: ForeignKey[User]
    news: ForeignKey[News]
    created_at: DateTimeField, optional
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    # viewed     = models.BooleanField(default=False)
    # last_view  = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    """Represents a message box that is showed for *all* users.

    Attributes
    ----------
    title: CharField
        The title of the alert. Max 75 characters.
    description: TextField
    color: CharField, default="info"
        See `COLOR_CHOICES`.
    active: BooleanField, default=True
        Says if the alert will be showed or not.
    expiration_date: DateField
        Date when alert will not be more showed.
    """
    title = models.CharField(max_length=75)
    description = models.TextField(
        help_text="Descrição sobre o alerta (aceita HTML).",
    )

    color = models.CharField(
        max_length=9,
        default="info",
        choices=COLOR_CHOICES,
    )

    active = models.BooleanField(
        default=True,
        help_text="Mostra o alerta ou não.",
    )
    expiration_date = models.DateField(
        help_text="Dia em que o alerta deixará de aparecer."
    )


    updated_at = models.DateTimeField(auto_now=True,)
    created_at = models.DateTimeField(auto_now_add=True,)


class Report(models.Model):
    """Represents a file report on Cloud.

    Attributes
    ----------
    url: CharField
        URL to download file on Cloud.
    status: TextField
    created_at: DateField
    """
    class Status(models.TextChoices):
        """ Model de escolhas de status do relatório. """

        FINISHED = "finished"
        PENDING = "pending"
        ERROR = "error"
    
    user_shop = ForeignKey(UserShop, models.CASCADE)
    url = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.PENDING)
    send_mail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderErrorLog(models.Model):
    """ A model for logging internal errors occurred within
    the order processing methods and systems.

    Attributes
    ----------
    created_date: DateTimeField
        The date when the error was thrown.
    order: CharField
        The order that has triggered the error.
    order_line_item: ForeignKey(OrderLineItem), blank=True, null=True
        The OLI that has triggered the error.
    traceback_message: TextField, blank=True, null=True
        Django's traceback message.
    error_message: CharField, blank=True, null=True
        The internal error message.
    user_shopee: ForeignKey(UserShopee), blank=True, null=True
        description
    user_shop: ForeignKey(UserShop), blank=True, null=True
        description
    """

    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderOrderError"
    )
    order_line_item = models.ForeignKey(
        OrderLineItem,
        on_delete=models.CASCADE,
        related_name="orderLineItemOrderError",
        blank=True,
        null=True,
    )
    traceback_message = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    user_shopee = models.ForeignKey(
        UserShopee,
        on_delete=models.CASCADE,
        related_name="userShopeeOrderError",
        blank=True,
        null=True,
    )
    user_shop = models.ForeignKey(
        UserShop,
        on_delete=models.CASCADE,
        related_name="userShopOrderError",
        blank=True,
        null=True,
    )