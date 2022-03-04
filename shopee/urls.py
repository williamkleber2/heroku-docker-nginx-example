from django.conf import settings
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

manualNotionUrl = settings.MANUAL_NOTION_URL
suporteNotionUrl = settings.SUPORTE_NOTION_URL
affiliates = settings.AFFILIATES_URL
bonanzaUrl = settings.BONANZA_URL
blazingUrl = settings.BLAZING_URL
droplinkfyV2Tutorial = settings.ATUALIZACAO_V2
manualAssinatura = settings.MANUAL_ASSINATURA
smsRussoUrl = settings.SMS_RUSSO_URL
manualFaturamento = settings.MANUAL_FATURAMENTO

urlpatterns = [
    path('', views.shopifyInfo, name='index'),
    path('vendorUsers/', views.vendorUsers, name='vendorUsers'),
    path('shopifyProducts/', views.shopifyProducts, name='shopifyProducts'),
    path('shopifyOrders/<str:pk>/', views.shopifyOrders, name='shopifyOrders'),
    path('shopifyInfo/', views.shopifyInfo, name='shopifyInfo'),
    path('charges/', views.charges, name='charges'),
    path('billing_data/', views.billing_data, name='billingData'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
    path('percentagePaysJson/', views.percentagePaysJson, name='percentagePaysJson'),
    path('userShopeeCredentials/', views.userShopeeCredentials, name='userShopeeCredentials'),
    
    path("graphs/", views.graphs.graphs),
    path("graphs/users/", views.graphs.graphs_users),
    path("graphs/upsell/", views.graphs.graphs_upsell),
    path("graphs/value_orders/", views.graphs.graphs_value_orders),
    path("graphs/total_orders/", views.graphs.graphs_total_orders),

    path('shopifyInfoUpdate/', views.shopifyInfoUpdate, name='shopifyInfoUpdate'),

    path("updateUserNewsNotification/", views.updateUserNewsNotification, name="updateUserNewsNotification"),

    path('vendorUserCreate/<str:ctype>/', views.vendorUserCreate, name='vendorUserCreate'),
    path('reactivateGoogleAccount/', views.reactivateGoogleAccount, name='reactivateGoogleAccount'),
    path('vendorUserCreate/', views.vendorUserCreate, name='vendorUserCreateSelect'),
    path('sendValidatePhoneSms/', views.sendValidatePhoneSms, name='sendValidatePhoneSms'),
    path('vendorUserValidateJson/', views.vendorUserValidateJson, name='vendorUserValidateJson'),
    path('aliUserValidateJson/', views.aliUserValidateJson, name='aliUserValidateJson'),
    path('vendorUserValidateSmsJson/', views.vendorUserValidateSmsJson, name='vendorUserValidateSmsJson'),
    path('vendorUserValidateSmsGoogleJson/', views.vendorUserValidateSmsGoogleJson, name='vendorUserValidateSmsGoogleJson'),
    path('vendorUserResendSmsApi/', views.vendorUserResendSmsApi, name='vendorUserResendSmsApi'),
    path('vendorUserEdit/<str:pk>/', views.vendorUserEdit, name="vendorUserEdit"),
    path('vendorUserErrorsJson/<str:pk>/', views.vendorUserErrorsJson, name="vendorUserErrorsJson"),
    path('createUserOnVendor/', views.createUserOnVendor, name='createUserOnVendor'),
    path('vendorUsers/createUserOnVendor/', views.createUserOnVendorFromVendorUsers, name='createUserOnVendorFromVendorUsers'),

    path('createUserOnVendorAPI/', views.createUserOnVendorAPI, name='createUserOnVendorAPI'),
    path('associateUserVendorToShop/', views.associateUserVendorToShop, name='associateUserVendorToShop'),
    path('vendorUserJson/<str:pk>/', views.vendorUserJson, name="vendorUserJson"),
    path('vendorUserValidateEmail/<str:pk>/', views.vendorUserValidateEmail, name="vendorUserValidateEmail"),
    
    path('vendorProductDeleteJson/', views.vendorProductDeleteJson, name='vendorProductDeleteJson'),

    path('vendorProductsJson/<int:variant_id>/', views.vendorProductsJson, name='vendorProductsJson'),
    path('shopifyProductsJson/', views.shopifyProductsJson, name='shopifyProductsJson'),
    path('vendorSyncProducts/', views.vendorSyncProducts, name='vendorSyncProducts'),

    path('vendorOrdersByPercentagePayJson/<str:pk>/', views.vendorOrdersByPercentagePayJson, name='vendorOrdersByPercentagePayJson'),

    path('vendorOrdersJson/<str:pk>/', views.vendorOrdersJson, name='vendorOrdersJson'),
    path('vendorOrderLineItemsJson/<str:pk>/', views.vendorOrderLineItemsJson, name='vendorOrderLineItemsJson'),

    path('vendorOrderPurchaseLineItemsJson/<str:pk>/', views.vendorOrderPurchaseLineItemsJson, name='vendorOrderPurchaseLineItemsJson'),

    path(
        "vendorOrdersBulkUpdateStatus/",
        views.vendor_order_line_item_bulk_update_status,
        name="vendorOrdersBulkUpdateStatus",
    ),
    path('verifyShopifyOrdersFulfillment/', views.verifyShopifyOrdersFulfillment, name='verifyShopifyOrdersFulfillment'),

    path('vendorOrdersProcessManually/', views.vendorOrdersProcessManually, name='vendorOrdersProcessManually'),

    path('vendorOrdersDelete/', views.vendorOrdersDelete, name='vendorOrdersDelete'),
    path('vendorOrderEdit/<str:pk>/', views.vendorOrderEdit, name='vendorOrderEdit'),

    path('vendorProductCreate/', views.vendorProductCreate, name='vendorProductCreate'),
    path('processableProduct/', views.processableProduct, name='processableProduct'),

    path('vendorProductGetVariant/<int:variant_id>/', views.vendorProductGetVariant, name='vendorProductGetVariant'),

    path('datatable/', views.datatable, name='datatable'),

    path('doneOrders/', views.doneOrders, name='doneOrders'),

    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name="logout"),

    path('plans/', views.plans, name="plans"),
    path('plans/'+affiliates+'/', views.affiliates, name="affiliates"),

    path('checkoutSession/', views.checkoutSession, name="checkoutSession"),
    path('checkoutThanks/', views.checkoutThanks, name='checkoutThanks'),
    path('checkoutSetup/', views.checkoutSetup, name="checkoutSetup"),
    path('checkoutSetupSession/', views.checkoutSetupSession, name="checkoutSetupSession"),
    path('checkoutSetupThanks/', views.checkoutSetupThanks, name='checkoutSetupThanks'),
    path('checkoutCustomerTax/', views.checkoutCustomerTax, name='checkoutCustomerTax'),
    
    path('termsOfService/', views.termsOfService, name='termsOfService'),
    path('privacyPolicy/', views.privacyPolicy, name='privacyPolicy'),

    path('portal/', views.portal, name='portal'),

    path('orders/', views.orders, name='orders'),
    path('ordersFilterJSON/', views.ordersFilterJSON, name='ordersFilterJSON'),
    path('manualRetryPercentagePay/', views.manualRetryPercentagePay, name='manualRetryPercentagePay'),

    path('statusShopifyToAwaitingOrder/', views.statusShopifyToAwaitingOrder, name='statusShopifyToAwaitingOrder'),

    path('upsellOrders/', views.upsellOrders, name='upsellOrders'),
    path('upsellOrders/check/', views.upsellOrdersCheck, name='upsellOrdersCheck'),
    path('processUpsell/', views.processUpsell, name='processUpsell'),
    
    path('unlinkParentOrder/', views.unlinkParentOrder, name='unlinkParentOrder'),
    path('getPossibleParents/', views.getPossibleParents, name='getPossibleParents'),    
    path('linkParentOrder/', views.linkParentOrder, name='linkParentOrder'),
   

    path('forgotPassword/',
         auth_views.PasswordResetView.as_view(template_name="auth-password-basic.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="auth-password-reset-sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="auth-password-reset-form.html"),
        name="password_reset_confirm"),

    path('reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name="auth-password-reset-complete.html"),
        name="password_reset_complete"),

    path('manual/', RedirectView.as_view(url=manualNotionUrl)),

    path('manual/suporte/', RedirectView.as_view(url=suporteNotionUrl)),

    path('proxy/bonanza/', RedirectView.as_view(url=bonanzaUrl)),

    path('proxy/blazing/', RedirectView.as_view(url=blazingUrl)),

    path('getTokenCrisp/', views.getTokenCrisp, name='getTokenCrisp'),
    
    path('droplinkfyV2Tutorial/', RedirectView.as_view(url=droplinkfyV2Tutorial)),

    path('manual/assinatura/', RedirectView.as_view(url=manualAssinatura)),

    path('manual/faturamento/', RedirectView.as_view(url=manualFaturamento)),

    path('sms/russo/', RedirectView.as_view(url=smsRussoUrl)),
    
    path('orders_report/', views.orders_report, name="orders_report"),

]
