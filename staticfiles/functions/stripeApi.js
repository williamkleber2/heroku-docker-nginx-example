const buy_now_button = document.querySelector('#buy_now_btn')
const addCard = document.querySelector('#addCard')

var referral = null
rewardful('ready', function() {
    if(Rewardful.referral) {
        referral = Rewardful.referral
    } else {
    }
});

if (buy_now_button != null) {
    buy_now_button.addEventListener('click', event => {
        $("#overlayPro").show();
        fetch('/checkoutSession/',
            {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: window.location.href,
                        referral: referral
                    })
                }
            )
            .then((result) => {
                return result.json()
            })
            .then((data) => {
                var stripe = Stripe(data.stripe_public_key);
                stripe.redirectToCheckout({
                    sessionId: data.session_id
                }).then(function (result) {
            });
        })
    })
}
if (addCard != null) {
    addCard.addEventListener('click', event => {
        $("#overlayPro").show();
        fetch('/checkoutSetupSession/')
            .then((result) => {
                return result.json()
            })
            .then((data) => {
                var stripe = Stripe(data.stripe_public_key);
                stripe.redirectToCheckout({
                    sessionId: data.session_id
                }).then(function (result) {
                });
            })
    })
}