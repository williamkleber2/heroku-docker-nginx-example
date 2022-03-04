$(document).ready(function() {
    $('#dataTable').DataTable({ data: shopeeUsersData });
    $('#dataTable').on('page.dt', function () {
        setTimeout(() => {
            feather.replace();
            var load_event = document.createEvent('Event');  
            load_event.initEvent('load', false, false);  
            window.dispatchEvent(load_event);
        }, 1000)
    });
    $('#dataTable').on('search.dt', function () {
        setTimeout(() => {
            feather.replace();
            var load_event = document.createEvent('Event');  
            load_event.initEvent('load', false, false);  
            window.dispatchEvent(load_event);
        }, 1000)
    });
    feather.replace();
});

$("#saveUser").click(function (event) {
    $("#overlayPro").show();

    activatedWasChangedManually = false;
    if(userShopee['activated'] != $("#activated").is(":checked")){
        activatedWasChangedManually = true;
    }
    
    $.ajax({
        type: "POST",
        url: "/vendorUserEdit/" + userShopee_pk +"/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "email": $("#email").val(),
            "phone": $("#phone").val(),
            "password": $("#password").val(),
            "proxy": $("#proxy").val(),
            "port": $("#port").val(),
            "proxy_login": $("#proxy_login").val(),
            "proxy_password": $("#proxy_password").val(),
            "activated": $("#activated").is(":checked"),
            "activatedWasChangedManually": activatedWasChangedManually
        },
        success: function (e) {
            if (e.status_code == 200) {
                toastr.success(e.message)
                window.location.replace("/vendorUsers/");
            }
            if (e.status_code == 302) {
                toastr.warning(e.message)
                $("#overlayPro").hide();
            }
            if (e.status_code == 404) {
                toastr.error(e.message)
                $("#overlayPro").hide();
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Erro não tratado")
            $("#overlayPro").hide();
        },
        complete: function() {

        }
    });
    return false;
});

$(document).on("click", "#viewUserShopeeUsers", function () {
    userId = $(this).data('id');
    email = $(this).parent().parent().find("#email")[0].text;
    loadUserShopeeErrorsModalData(userId, email);
});

function loadUserShopeeErrorsModalData(userId, email){
    $("#h1UserEmail").text("Usuário: "+email);
    $('#dataTableErrors').DataTable().destroy();
    $('#dataTableErrors').DataTable({
        "ajax": "/vendorUserErrorsJson/"+userId,
        "columns": [
            { "data": "user_shopee__email"},
            { "data": "date" },
            { "data": "message" }
        ],
        "language": {
            "emptyTable": "Não existem erros",
            "loadingRecords": "Carregando os erros..."
        }
    });
}

document.addEventListener("reactivateButton", (e) => {
    console.log("reactivateButton", e)
});
// $(document).on();
// $(document).on();
