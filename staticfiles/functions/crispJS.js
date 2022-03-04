$(document).ready(
    function(){
        $.ajax({
            type: "POST",
            url: "/getTokenCrisp/",
            headers: { "X-CSRFToken": csrftoken },
            data: {},
            success: function (response) {
                $crisp = [];
                CRISP_WEBSITE_ID = response.crispWebsiteId;
                CRISP_TOKEN_ID = response.token;
                (function(){d=document;s=d.createElement('script');s.src='//client.crisp.chat/l.js';s.async=1;d.getElementsByTagName('head')[0].appendChild(s);})();
                $crisp.push(["set", "user:email", response.email]);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Erro ao iniciar o crisp")
            },
            complete: function() {
            }
        });
    }
);