var dt, isAliFiltered = false;
$(document).ready(function() {
    const urlSearchParams = new URLSearchParams(window.location.search);
    dt = $('#dataTable').DataTable({ 
        data: shopeeUsersData.filter(function(e) {
            return e[0] !== 'ali'
        }),
    })

    $('#aliToggle').on('click', function(e) {
        isAliFiltered = !isAliFiltered;

        if(isAliFiltered) {
            dt.destroy();
            dt = $('#dataTable').DataTable({ 
                data: shopeeUsersData.filter(function(e) {
                    return e[0] === 'ali' 
                }),
            })
            dt.column(0).visible(false);
            dt.column(1).visible(false);
            dt.column(3).visible(false);
            dt.column(5).visible(false);
            dt.column(6).visible(false);
            dt.column(7).visible(false);
            dt.column(8).visible(false);
            dt.column(9).visible(false);
            dt.column(10).visible(false);
            dt.column(11).visible(false);
            dt.column(13).visible(false);
        }
        else {
            dt.destroy();
            dt = $('#dataTable').DataTable({ 
                data: shopeeUsersData.filter(function(e) {
                    return e[0] !== 'ali' 
                }),
            })
        }
        dt.column(0).visible(false);
    })
    
    dt.column(0).visible(false);
    
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

    const email = urlSearchParams.get('email');
    const vendor = urlSearchParams.get('vendor');

    if(email) {
        if(vendor === "ali") {
            $('#aliToggle').click();
        }
        dt.search(email).draw();
    }
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
                Sentry.captureMessage(e.message)
                $("#overlayPro").hide();
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Erro não tratado")
            Sentry.captureMessage(XMLHttpRequest.responseText)
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
