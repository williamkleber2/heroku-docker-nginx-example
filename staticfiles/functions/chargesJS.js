$(document).ready(function() {
    $('#dataTablePercentage').DataTable({
        "ajax": "/percentagePaysJson/",
        "columns": [
            { "data": "status" ,
                "defaultContent": "",
                "render": function(data, type, row, meta) {
                    return getStatusLabel(data)
                }
            },
            { "data": "start_date" ,
                "render": function(data, type, row, meta) {
                    return formatDateTime(data)
                }
            },
            { "data": "end_date" ,
                "render": function(data, type, row, meta) {
                    return formatDateTime(data)
                }
            },
            { "data": "orders_count" },
            { "data": "value" ,
                "render": function(data, type, row, meta) {
                    return 'R$' + data
                }
            },
            { "data": "id",
                "render": function(data, type, row, meta) {
                    return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrders" type="button" data-toggle="modal" data-target="#modalOrders"><i class="fas fa-grip-lines"></i></a>';
                }
            },
            { "data": "id",
                "render": function(data, type, row, meta) {
                    return '<a class="btn btn-success btn-xs" data-id="'+data+'" id="payPercentage" type="button"><i class="far fa-credit-card"></i></a>';
                }
            }
        ],
        "language": {
            "emptyTable": "Não existem cobranças de porcentagem",
            "loadingRecords": "Carregando as cobranças de porcentagem..."
        }
    });
});

$(document).on("click", "#payPercentage", function () {
    console.log("payPercentage")
    percentagePayId = $(this).data('id');
    $("#overlayPro").show()
    $.ajax({
        type: "POST",
        url: "/manualRetryPercentagePay/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "percentagePayId": percentagePayId
        },
        success: function (response) {
            console.log("response")
            console.log(response)
            if (response.status_code == 200) {
                toastr.success(response.message)
            }
            if (response.status_code == 404) {
                toastr.error(response.message)
            }
            $('#dataTablePercentage').DataTable().ajax.reload(function(){
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

$(document).on("click", "#viewOrders", function () {
    percentagePay = $(this).data('id');
    loadOrdersModalData(percentagePay)
});

function loadOrdersModalData(percentagePay){
    $('#dataTableOrders').DataTable().destroy()
    $('#dataTableOrders').DataTable({
        "ajax": "/vendorOrdersByPercentagePayJson/"+percentagePay,
        "columns": [
            { "data": "name" },
            { "data": "dropshopee_created_date"  ,
                "render": function(data, type, row, meta) {
                    return formatDateTime(data)
                }
            },
            { "data": "total_price" ,
                "render": function(data, type, row, meta) {
                    return data + ' R$'
                }
            },
        ],
        "language": {
            "emptyTable": "Não existem pedidos nesta cobrança",
            "loadingRecords": "Carregando os pedidos..."
        }
    });
}

function formatDateTime (dateTimeStr) {
    if(dateTimeStr == null){
        return ''
    }

    var dateTimeObj = new Date(dateTimeStr);


    
    return dateTimeObj.getFullYear() + '-' + formatDateNumber(dateTimeObj.getMonth() + 1) + '-' + formatDateNumber(dateTimeObj.getDate());
        
}

function formatDateNumber(dateNumber){
    if(dateNumber < 10){
        return '0' + dateNumber;
    } else{
        return dateNumber;
    }
}

function getStatusLabel(statusKey){
    statusMap = {
        'paid': '<div data-id="'+statusKey+'"  id="created_status" class="badge badge-success badge-pill">Pago</div>',
        'unpaid': '<div data-id="'+statusKey+'"  id="created_status" class="badge badge-danger badge-pill">Não Pago</div>',
        'past_due': '<div data-id="'+statusKey+'"  id="created_status" class="badge badge-warning badge-pill">Pagamento atrasado</div>',
        'refunded': '<div data-id="'+statusKey+'"  id="created_status" class="badge badge-primary badge-pill">Reembolsado</div>'
    }
    return statusMap[statusKey]    
}