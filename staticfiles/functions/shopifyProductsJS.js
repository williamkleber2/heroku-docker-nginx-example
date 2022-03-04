$(document).ready(function() {
    loadDatable();
});

function loadDatable(){
    $('#dataTable').DataTable({
        "ajax": "/shopifyProductsJson/",
        "columns": [
             { "data": "product_shopify__title",
                "render": function(data, type, row, meta) {
                    return '<td><a data-id="'+data+'" id="productName">'+data+'</a></td>'
                }
             },
             { "data": "id" },
             { "data": "title",
                 "render": function(data, type, row, meta) {
                    return '<td><a data-id="'+data+'" id="variantName">'+data+'</a></td>'
                }
             },
             { "data": "sku" },
             { "data": "price"},
             { "data": "productVariantsShopee__count" },
             { "data": "id",
                "render": function(data, type, row, meta) {
                    return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewMapButton" type="button" data-toggle="modal" data-target="#exampleModal"><i class="fas fa-link"></i></a>';
                }
             },
             { "data": "is_processable" ,
                "defaultContent": "",
                "render": function(data, type, row, meta) {
                    return getTrueOrFalse(data, row.id)
                }
            },
        ]
    });
}

function getTrueOrFalse(statusKey, rowId){
    if(statusKey == null){ statusKey = true; }
    statusMap = {
        'true': '<a class="btn btn-success btn-xs" data-id="'+rowId+'" data-status="'+statusKey+'" id="processableProduct" type="button" data-toggle="modal" ><i class="fas fa-toggle-on"></i></a>',
        'false': '<a class="btn btn-danger btn-xs" data-id="'+rowId+'" data-status="'+statusKey+'" id="processableProduct" type="button" data-toggle="modal" ><i class="fas fa-toggle-off"></i></a>'
    }
    return statusMap[statusKey]
}

$(document).on("click", "#processableProduct", function () {
    variantId = $(this).data('id');
    status = $(this).data('status');
    if(status == 'true'){
        if (!confirm('Tem certeza que NÃO quer processar esse produto?')) return false;
    }else{
        if (!confirm('Tem certeza que quer processar esse produto?')) return false;
    }
    $("#overlayPro").show()
    var me = $(this);
    event.preventDefault();
    if (me.data('requestRunning')) return;
    me.data('requestRunning', true);
    $.ajax({
        type: "POST",
        url: "/processableProduct/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "variantId": variantId,
            "status": status
        },
        success: function () {
            toastr.success("Alteração concluída!")
            $('#dataTable').DataTable().ajax.reload(function(){
                $("#overlayPro").hide();
            });
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro")
            $("#overlayPro").hide();
        }
    });
    return false;
});

$(document).on("click", "#syncProductsButton",function () {
    if(available_syncs == 0){
        alert('Excedeu o número máximo de sincronizações.');
        return false;
    } 
    if (!confirm('Tem apenas '+ available_syncs +' disponiveis para hoje. Deseja continuar?')) return false;
    $.ajax({
        type: "POST",
        url: "/vendorSyncProducts/",
        headers: { "X-CSRFToken": csrftoken },
        success: function (response) {
            if (response.status_code == 200) {
                toastr.success(response.message)
            }
            if (response.status_code == 404) {
                toastr.error(response.message)
            }
            available_syncs = response.available_syncs
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error('Deu erro')
        },
        complete: function() {
        }
    });
    return false;
});

$(document).on("click", "#viewMapButton", function() {
    const id      = $(this).data('id');
    const name    = $(this).parent().parent().find("#productName")[0].text
    const variant = $(this).parent().parent().find("#variantName")[0].text

    hideProductFormMappingModal();
    return showProductTableMappingModal(id, name, variant);
});
