$(document).on("click", "#updateShopifyInfo", function () {
    $("#overlayPro").show();
    $.ajax({
        type: "POST",
        url: "/shopifyInfoUpdate/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "checkout": $("#exampleFormControlSelect1").val(),
            "shopify_name": $("#shopifyName").val(),
            "shopify_key": $("#confirmPassword").val(),
            "tracking_url": $("#tracking_url").val(),
            "order_memo": $("#order_memo").val(),
            "shopify_shared_secret": $("#shared_secret").val(),
            "free_shipping": $("#checkFreeShipping")[0].checked,
            "working": $("#checkAccountChanges")[0].checked,
            "automatic_upsell": $("#checkAutomaticUpsell")[0].checked,
            "notify_order_fulfillment": $("#checkNotify")[0].checked,
        },
        success: function (e) {
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {
                toastr.error(e.message)
                Sentry.captureMessage(e.message)
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro")
            Sentry.captureMessage(XMLHttpRequest.responseText)
        },
        complete: function() {
            $("#overlayPro").hide()

        }
    });
    return false;
});