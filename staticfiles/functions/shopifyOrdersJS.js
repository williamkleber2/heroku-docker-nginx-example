$(document).ready(function() {
    $('#dataTable').DataTable({
        "ajax": "/vendorOrdersJson/"+orderStatus,
        "columns": columnsByStatus(orderStatus),
        "language": {
            "emptyTable": "Não existem pedidos",
            "loadingRecords": "Carregando os pedidos..."
        }
    });
});

$(document).on('change','input[id="selectGeral"]',function() {
    $('.custom-control-input').prop("checked" , this.checked);
});

$(document).on("click", "#viewLineItems", function () {
    orderId = $(this).data('id');
    orderName = $(this).parent().parent().find("#orderName")[0].text
    loadLineItemsModalData(orderId, orderName)
});

$(document).on("click", "#viewOrderPurchaseLineItems", function () {
    orderId = $(this).data('id');
    orderName = $(this).parent().parent().find("#orderName")[0].text
    loadOrderPurchaseLineItemsModalData(orderId, orderName)
});

$(document).on("click", "#processedShopifyButton", function () {
    $("#overlayPro").show();
    $.ajax({
        type: "POST",
        url: "/verifyShopifyOrdersFulfillment/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        success: function (e) {
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro")
            $("#overlayPro").hide()
        },
        complete: function() {
            $('#dataTable').DataTable().destroy()
            $('#dataTable').DataTable({
                "ajax": "/vendorOrdersJson/"+orderStatus,
                "columns": columnsByStatus(orderStatus),
                "language": {
                    "emptyTable": "Não existem pedidos",
                    "loadingRecords": "Carregando os pedidos..."
                }
            });
            $("#overlayPro").hide()
        }
    });
});

$(document).on("click", "#paidButton", function () {
    $("#overlayPro").show();
    var dataTable = $('#dataTable').DataTable()
    var rows = getSelectedRows(dataTable);
    if(rows.length > 0){
        if (!confirm('Deseja marcar como pago ' + rows.length + ' pedido(s) ?')) return false;
        dataToSend = JSON.stringify(rows);
        $.ajax({
            type: "POST",
            url: "/vendorOrdersBulkUpdateStatus/",
            headers: { "X-CSRFToken": csrftoken },
            traditional: true,
            data: { 'orders': dataToSend,
                    'status': 'APS'
                },
            success: function () {
                toastr.success("Salvo com sucesso")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                toastr.error("Deu erro")
                $("#overlayPro").hide()
            },
            complete: function() {
                $('#dataTable').DataTable().destroy()
                $('#dataTable').DataTable({
                    "ajax": "/vendorOrdersJson/"+orderStatus,
                    "columns": columnsByStatus(orderStatus),
                    "language": {
                        "emptyTable": "Não existem pedidos",
                        "loadingRecords": "Carregando os pedidos..."
                    }
                });
                $("#overlayPro").hide()
            }
        });
    }
    else {
        $("#overlayPro").hide();
    }
    
});

$(document).on("click", "#cancelOrdersButton", function () {
    $("#overlayPro").show();
    var dataTable = $('#dataTable').DataTable()
    var rows = getSelectedRows(dataTable);
    if(rows.length > 0){
        if (confirm('Serão cancelados ' + rows.length + ' pedido(s), deseja continuar?')) {
            dataToSend = JSON.stringify(rows);
            $.ajax({
                type: "POST",
                url: "/vendorOrdersBulkUpdateStatus/",
                headers: { "X-CSRFToken": csrftoken },
                traditional: true,
                data: { 'orders': dataToSend,
                        'status': 'C'
                    },
                success: function () {
                    toastr.success("Salvo com sucesso")
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    toastr.error("Deu erro")
                    $("#overlayPro").hide()
                },
                complete: function() {
                    $('#dataTable').DataTable().destroy()
                    $('#dataTable').DataTable({
                        "ajax": "/vendorOrdersJson/"+orderStatus,
                        "columns": columnsByStatus(orderStatus),
                        "language": {
                            "emptyTable": "Não existem pedidos",
                            "loadingRecords": "Carregando os pedidos..."
                        }
                    });
                    $("#overlayPro").hide()
                }
            });
        }       
    }
    else {
        $("#overlayPro").hide();
    }
    
});      
      

$(document).on("click", "#processOrdersButton", function () {
    $("#overlayPro").show();
    var dataTable = $('#dataTable').DataTable();
    var rows = getSelectedRows(dataTable);
    if(rows.length > 0){
        if (!confirm('Serão processado ' + rows.length + ' pedido(s), deseja continuar?')) return false;
        dataToSend = JSON.stringify(rows);
        $.ajax({
            type: "POST",
            url: "/vendorOrdersProcessManually/",
            headers: { "X-CSRFToken": csrftoken },
            traditional: true,
            data: { 'orders': dataToSend },
            success: function () {
                toastr.success("Pedidos enviados para processamento")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                toastr.error("Deu erro")
                $("#overlayPro").hide()
            },
            complete: function() {
                $('#dataTable').DataTable().destroy()
                $('#dataTable').DataTable({
                    "ajax": "/vendorOrdersJson/"+orderStatus,
                    "columns": columnsByStatus(orderStatus),
                    "language": {
                        "emptyTable": "Não existem pedidos",
                        "loadingRecords": "Carregando os pedidos..."
                    }
                });
                $("#overlayPro").hide()
            }
        });

    }
    else{
        $("#overlayPro").hide();
    }
});

$(document).on("click", "#deleteOrdersButton", function () {
    $("#overlayPro").show();
    var dataTable = $('#dataTable').DataTable();
    var rows = getSelectedRows(dataTable);
    if(rows.length > 0){
        if (!confirm('Serão deletados ' + rows.length + ' pedido(s), deseja continuar?')) return false;
        dataToSend = JSON.stringify(rows);
        $.ajax({
            type: "POST",
            url: "/vendorOrdersDelete/",
            headers: { "X-CSRFToken": csrftoken },
            traditional: true,
            data: { 'orders': dataToSend },
            success: function () {
                toastr.success("Pedidos deletados")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                toastr.error("Deu erro")
                $("#overlayPro").hide()
            },
            complete: function() {
                $('#dataTable').DataTable().destroy()
                $('#dataTable').DataTable({
                    "ajax": "/vendorOrdersJson/"+orderStatus,
                    "columns": columnsByStatus(orderStatus),
                    "language": {
                        "emptyTable": "Não existem pedidos",
                        "loadingRecords": "Carregando os pedidos..."
                    }
                });
                $("#overlayPro").hide()
            }
        });

    }
    else{
        $("#overlayPro").hide();
    }
});

function loadLineItemsModalData(orderId, orderName){
    $("#modalOrderLineItems #h1OrderName").text("Pedido: "+orderName)
    $('#dataTableOrderLineItems').DataTable().destroy()
    $('#dataTableOrderLineItems').DataTable({
        "ajax": "/vendorOrderLineItemsJson/"+orderId,
        "columns": [
            { "data": "product_variant__product_shopify__title" },
            { "data": "product_variant__title" },
            { "data": "quantity" },
        ],
        "language": {
            "emptyTable": "Não existem items neste pedido",
            "loadingRecords": "Carregando os items..."
        }
    });
}

function loadOrderPurchaseLineItemsModalData(orderId, orderName){
    $("#modalOrderPurchaseLineItems #h1OrderName").text("Pedido: "+orderName)
    $('#dataTableOrderPurchaseLineItems').DataTable().destroy()
    $('#dataTableOrderPurchaseLineItems').DataTable({
        "ajax": "/vendorOrderPurchaseLineItemsJson/"+orderId,
        "columns": [
            { "data": "user_shopee__email" },
            { "data": "order_purchase__shopee_order_id" ,
                "render": function(data, type, row, meta) {
                    return '<td><a target="_blank" href="https://shopee.com.br/user/purchase/order/' + data + '/" style="pointer-events: all;">' + data + '</a><td>'
                }
            },
            { "data": "shopee_product_name" },
            { "data": "shopee_product_variant" },
            { "data": "purchase_date" ,
                "render": function(data, type, row, meta) {
                    return formatDateTime(data)
                }
            },
            { "data": "order_purchase__shipping_fee" ,
                "render": function(data, type, row, meta) {
                    return formatMonetaryValue(data)
                }
            },
            { "data": "order_purchase__list_type" ,
                "render": function(data, type, row, meta) {
                    return getStatusLabel(data)
                }
            },
            { "data": "order_purchase__canceled_status" },
            { "data": "order_purchase__tracking_number" },
        ],
        "language": {
            "emptyTable": "Não existem produtos neste pedido",
            "loadingRecords": "Carregando os produtos..."
        }
    });
}

function getSelectedRows(dataTable){
    var trs = $('#dataTable > tbody > tr');
    var rows = [];

    for(i=0; i<trs.length; i++){
        tr = trs[i];
        if($('.custom-control-input' , tr)[0].checked){
            rows.push(dataTable.row(tr).data());
        }
    }
    return rows;
}

function formatDateTime (dateTimeStr) {
    if(dateTimeStr == null){
        return ''
    }

    var dateTimeObj = new Date(dateTimeStr);

    return dateTimeObj.getFullYear() + '-' + formatDateNumber(dateTimeObj.getMonth() + 1) + '-' + formatDateNumber(dateTimeObj.getDate()) + ' ' + formatDateNumber(dateTimeObj.getHours()) + ':' + formatDateNumber(dateTimeObj.getMinutes());
        
}

function formatDateNumber(dateNumber){
    if(dateNumber < 10){
        return '0' + dateNumber;
    } else{
        return dateNumber;
    }
}

function formatMonetaryValue(value){
    //1500000 -> 15,00 reais
    if(value){
        return value/100000;
    } else{
        return '';
    }
}

function getStatusLabel(statusKey){
    statusMap = {
        '9': 'A Pagar',
        '7': 'A Enviar',
        '8': 'A Receber',
        '3': 'Concluído',
        '4': 'Cancelado'
    }
    return statusMap[statusKey]    
}

function columnsByStatus(status){
    columns = [];

    switch(status){
        case 'AO':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "address" },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'AP':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "client_phone" },
                    { "data": "cpf" },
                    { "data": "user_shopee__email" },
                    { "data": "shopee_checkout_id" ,
                        "render": function(data, type, row, meta) {
                            return '<td><a target="_blank" href="https://shopee.com.br/user/purchase/checkout/' + data + '/" style="pointer-events: all;">' + data + '</a><td>'
                        }
                    }, 
                    { "data": "boleto_number" , 
                        "render": function(data, type, row, meta) {
                            if(data){return '<td>'+data.replaceAll('.','').replaceAll(' ','')+'</td>'}
                            else{ return '<td></td>'}
                    }},
                    { "data": "boleto_due_date" },
                    { "data": "value" },
                    { "data": "free_shipping", 
                        render: function (data, type, row) {
                          return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'APS':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "client_phone" },
                    { "data": "cpf" },
                    { "data": "user_shopee__email" },
                    { "data": "shopee_checkout_id" ,
                        "render": function(data, type, row, meta) {
                            return '<td><a target="_blank" href="https://shopee.com.br/user/purchase/checkout/' + data + '/" style="pointer-events: all;">' + data + '</a><td>'
                        }
                    }, 
                    { "data": "boleto_number" , 
                        "render": function(data, type, row, meta) {
                            if(data){return '<td>'+data.replaceAll('.','').replaceAll(' ','')+'</td>'}
                            else{ return '<td></td>'}
                    }},
                    { "data": "boleto_due_date" },
                    { "data": "value" },
                    { "data": "free_shipping", 
                        render: function (data, type, row) {
                          return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'AS':
            columns = [
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "client_phone" },
                    { "data": "cpf" },
                    { "data": "user_shopee__email" },
                    { "data": "value" },
                    { "data": "free_shipping", 
                        render: function (data, type, row) {
                            return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'AF':
            columns = [
                { "data": "id",
                    "render": function(data, type, row, meta) {
                        return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                    }
                },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "client_phone" },
                    { "data": "cpf" },
                    { "data": "user_shopee__email" },
                    { "data": "value" },
                    { "data": "free_shipping", 
                        render: function (data, type, row) {
                            return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'F':
            columns = [
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "client_phone" },
                    { "data": "cpf" },
                    { "data": "user_shopee__email" },
                    { "data": "value" },
                    { "data": "free_shipping", 
                        render: function (data, type, row) {
                            return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'C': 
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "canceled_at" },
                    { "data": "value" },
                    { "data": "free_shipping",
                        render: function (data, type, row) {
                            return data ? 'Sim' : 'Não';
                        } 
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
        case 'FO':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "user_shopee__email"},
                    { "data": "error_date",
                        "render": function(data, type, row, meta) {
                            return formatDateTime(data)
                        }
                    },
                    { "data": "error"},
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn btn-primary btn-xs" data-id="'+data+'" id="viewLineItems" type="button" data-toggle="modal" data-target="#modalOrderLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    }
                ];
            break;
    }
    return columns;
}