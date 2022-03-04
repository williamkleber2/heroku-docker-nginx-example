var tracking = false;

$(document).ready(function(){
    initializeDatePicker();
    refreshDatatables();    
});

$(document).on("keypress", "#orderNameFilter", function (e) {
    if (e.key === 'Enter') {
        refreshDatatables();
    }
});

$('#navigation li a').click(function() {
    var orderStatus = $(this).attr('id');
    getOrders(orderStatus);
});

$(document).on('change','.selectGeral',function() {
    var dataTableElement = getActiveDatatable();
    $('.custom-control-input', dataTableElement).prop("checked" , this.checked);
    
});

$(document).on('change','#dataTable-UPSELL td .custom-control-input',function() {

    console.log($(this)[0].checked);

    if($(this)[0].checked){
        var currentRowId = $(this)[0].id;
        var dataTableElement = $('#dataTable-UPSELL');
        var dataTable = dataTableElement.DataTable();
        removeOldSelection(dataTableElement, dataTable, currentRowId);
    } 
    
});

function removeOldSelection(dataTableElement, dataTable, currentRowId){
    var trs = $('tbody > tr', dataTableElement);
    var rows = [];

    for(i=0; i<trs.length; i++){
        tr = trs[i];
        if($('.custom-control-input' , tr).length > 0 && $('.custom-control-input' , tr)[0].id != currentRowId && $('.custom-control-input' , tr)[0].checked){
            $('.custom-control-input' , tr)[0].checked = false;
        }
    }
}

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

$(document).on("click", ".processedShopifyButton", function () {
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
            refreshDatatables();
        }
    });
});

$(document).on("click", ".paidButton", function () {
    $("#overlayPro").show();
    var dataTableElement = getActiveDatatable();
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);
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
                refreshDatatables();
            }
        });
    }
    else {
        $("#overlayPro").hide();
    }
    
});

$(document).on("click", ".cancelOrdersButton", function () {
    $("#overlayPro").show();
    var dataTableElement = getActiveDatatable();
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);
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
                    refreshDatatables();
                }
            });
        }       
    }
    else {
        $("#overlayPro").hide();
    }
    
});      
      

$(document).on("click", ".processOrdersButton", function () {
    $("#overlayPro").show();
    var dataTableElement = getActiveDatatable();
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);
    if(rows.length > 0){    
        processAIOrders(rows);
    }
    else{
        $("#overlayPro").hide();
    }
});

$(document).on("click", ".deleteOrdersButton", function () {
    $("#overlayPro").show();
    var dataTableElement = getActiveDatatable();
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);
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
                refreshDatatables();
            }
        });

    }
    else{
        $("#overlayPro").hide();
    }
});

$(document).on("click", ".syncOrdersButton", function () {
    $("#overlayPro").show();
    var dataTableElement = getActiveDatatable();
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);
    if(rows.length > 0){
        processAIOrders(rows);
    }
    else{
        $("#overlayPro").hide();
    }
});

$(document).on("click", "#searchOrder", function () {
    $("#overlayPro").show();
    refreshDatatables();
});

$(document).on("click", "#saveOrderModalBtn", function () {
    $("#overlaySearchModal").show();
    saveOrder();
});

function processAIOrders(rows){
    if (!confirm('Serão sincronizados ' + rows.length + ' pedido(s), deseja continuar?')) return false;
    dataToSend = JSON.stringify(rows);
    $.ajax({
        type: "POST",
        url: "/statusShopifyToAwaitingOrder/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'orders': dataToSend },
        success: function () {
            toastr.success("Pedidos sincronizados e enviados para processamento")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro")
            $("#overlayPro").hide()
        },
        complete: function() {
            refreshDatatables();
        }
    });
}

function saveOrder(){
    $("#overlayProModal").show();
    var order = {};
    order["client_name"] = $('#clientName').val();
    order["client_phone"] = $("#clientPhone").val();
    order["street"] = $('#street').val();
    order["street_number"] = $('#street_number').val();
    order["complement"] = $('#complement').val();
    order["zip_code"] = $('#zip_code').val();
    order["city"] = $('#city').val();
    order["state"] = $('#state').val();
    order["neighborhood"] = $('#neighborhood').val();
    order["cpf"] = $('#cpf').val();
    $.ajax({
        type: "POST",
        url: "/vendorOrderEdit/"+$('#orderId').val()+"/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'order': JSON.stringify(order) },
        success: function (e) {            
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro");
            $("#overlayProModal").hide();
            refreshDatatables();
        },
        complete: function() {
            $("#editOrderModal").modal('hide');
            $("#overlayProModal").hide();
            refreshDatatables();
        }
    });
}

function refreshDatatables(){
    getOrdersInfo();
    orderStatus = getActiveTab().id;
    getOrders(orderStatus);
}

function getActiveTab(){
    return $('#cardTab .nav-link.active')[0];
}

function getActiveDatatable(){
    tab = getActiveTab();
    orderStatus = tab.id;
    datatableId = '#dataTable-'+orderStatus;
    return $(datatableId);
}

function getSelectedDates(){
    var picker = $('#daterange').data('daterangepicker');
    var selectedDates = {
        startDate : picker.startDate.format('YYYY-MM-DD'),
        endDate : picker.endDate.format('YYYY-MM-DD')
    }
    
    return selectedDates;
}

function getOrdersInfo(){    
    var orderFilter = $('#orderNameFilter').val();
    if(orderFilter == ""){ orderFilter = "<empty>"; }

    var selectedDates = getSelectedDates();
    var dataToSend = JSON.stringify(selectedDates);

    $.ajax({
        type: "GET",
        url: "/ordersFilterJSON/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'selectedDates': dataToSend,
                'orderFilter': orderFilter,},
        success: function (response) {
            response.data.forEach(function(index){
                name = $('#'+index.status).html()
                nameSplit = name.split('<br>')
                $('#'+index.status).html(nameSplit[0] + "<br>("+index.dcount+")");
            })
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            console.log("erro")
            console.log(XMLHttpRequest)
            console.log(textStatus)
            console.log(errorThrown)
        }
    });
}

function setDateFilterCookie(picker){
    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth();
    var day = now.getDate();
    var expireDate = new Date(year + 1, month, day);
    var dateValues = picker.startDate.format('YYYY-MM-DD') + "_" + picker.endDate.format('YYYY-MM-DD');
    setCookie("dateFilterLabel", picker.chosenLabel, expireDate);
    setCookie("dateFilterValue", dateValues, expireDate);
}

function getDateFilterCookie(){
    var dateFilterObj = {
        dateFilterLabel: getCookie("dateFilterLabel"),
        dateFilterValue: getCookie("dateFilterValue")
    }

    return dateFilterObj;

}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

function getOrders(orderStatus){    
    $("#overlayPro").show();
    var orderFilter = $('#orderNameFilter').val();
    if(orderFilter == ""){ orderFilter = "<empty>"; }
    var selectedDates = getSelectedDates();
    var dataToSend = JSON.stringify(selectedDates);
    var tableSelector = $('#dataTable-' + orderStatus);

    tableSelector.DataTable().destroy();
    table = tableSelector.DataTable({
        "ajax":{ 
            "url": "/vendorOrdersJson/" + orderStatus+"/",
            "data": {
                "selectedDates": dataToSend,
                'orderFilter': orderFilter,
                'GMT': ((new Date()).getTimezoneOffset() / -60),
                'timezone': Intl.DateTimeFormat().resolvedOptions().timeZone,
                "tracking": orderStatus == "AS" ? tracking : undefined,
            },
        },
        "columns": columnsByStatus(orderStatus),
        "language": {
            "emptyTable": "Não existem pedidos",
            "loadingRecords": "Carregando os pedidos..."
        },
        "initComplete": function( settings, json ) {
            $("#overlayPro").hide();
        }
    });

    // Remove old event listener
    $('tbody', tableSelector).off('click');
    // Add event listener for opening and closing details
    $('tbody', tableSelector).on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var tdi = tr.find(".details-control a");
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
            tdi.first().removeClass('fa-icon-red');
            tdi.first().addClass('fa-icon-green');
        }
        else {
            // Open this row
            row.child(renderOLIs(row.data().olis)).show();
            tr.addClass('shown');
            tdi.first().removeClass('fa-icon-green');
            tdi.first().addClass('fa-icon-red');
        }
    } );

    // Remove old event listener
    $('thead', tableSelector).off('click');
    // Add event listener for opening and closing details
    $('thead', tableSelector).on('click', 'th.details-control', function () {
        var tdi = $(this);
        var tableHtml = $(this).closest('table')
        var trs = $('tbody > tr', tableHtml);

        for(i=0; i<trs.length; i++){
            tr = trs[i];
            var row = table.row(tr);
            var tdiInner = $('.details-control a', tr);
            if(tdi.hasClass( "shown" )){
                // This row is already open - close it
                row.child.hide();
                $(tr).removeClass('shown');
                tdiInner.first().removeClass('fa-icon-red');
                tdiInner.first().addClass('fa-icon-green');
            }
            else {
                // Open this row
                if(row.data() != null){
                    row.child(renderOLIs(row.data().olis)).show();
                }
                $(tr).addClass('shown');
                tdiInner.first().removeClass('fa-icon-green');
                tdiInner.first().addClass('fa-icon-red');
            }
        }

        var svg = $('svg', tdi);

        if(tdi.hasClass( "shown" )){
            tdi.removeClass('shown');
            svg.removeClass('fa-minus-square');
            svg.addClass('fa-plus-square');
            svg.attr('data-icon', 'plus-square');
        } else{
            tdi.addClass('shown');
            svg.removeClass('fa-plus-square');
            svg.addClass('fa-minus-square');
            svg.attr('data-icon', 'minus-square');
        }
        
    } );

    table.on("user-select", function (e, dt, type, cell, originalEvent) {
        if ($(cell.node()).hasClass("details-control")) {
            e.preventDefault();
        }
    });

    setUpsellButtonListeners(tableSelector);
}

$(document).on("click", "#unlinkParentOrder", function () {
    orderId = $(this).data('id');
    unlinkParentOrder(orderId);
});
$(document).on("click", "#attachOrder", function () {
    orderId = $(this).data('id');
    orderName = $(this).parent().parent().find("#orderName")[0].text
    searchPossibleParentOrders(orderId, orderName);
});

function searchPossibleParentOrders(orderId, orderName){
    $("#overlayPro").show();
    $("#upsellOrderModal").modal();
    $("#upsellOrderModal #h1MainOrderName").text(orderName);
    $("#upsellOrderModal #h1MainOrderName").attr('data-id' , orderId);
    $('#upsellOrderModal').on('hidden.bs.modal', function () {
        var tableSelector = $('#dataTable-UPSELL');
        tableSelector.DataTable().destroy();
        refreshDatatables();
      });
    dataToSend = JSON.stringify(orderId);
    var tableSelector = $('#dataTable-UPSELL');
    table = tableSelector.DataTable({
        "ajax":{ 
            "url": "/getPossibleParents/",
            "data": {
                "orderId": dataToSend
            },
        },
        "select": {
            style: 'single'
        },
        "columns": columnsByStatus('UPSELL'),
        "language": {
            "emptyTable": "Não existem pedidos com o mesmo endereço",
            "loadingRecords": "Carregando os pedidos..."
        },
        "initComplete": function( settings, json ) {
            $('.toggle-demo').bootstrapToggle();
        }
    });   

    // Remove old event listener
    $('tbody', tableSelector).off('click');
    // Add event listener for opening and closing details
    $('tbody', tableSelector).on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var tdi = tr.find(".details-control svg");
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
            //tdi.first().removeClass('fa-minus-square');
            //tdi.first().addClass('fa-plus-square');
            //tdi.first().attr('data-icon', 'plus-square');
        }
        else {
            // Open this row
            row.child(renderOLIs(row.data().olis)).show();
            tr.addClass('shown');
            //tdi.first().removeClass('fa-plus-square');
            //tdi.first().addClass('fa-minus-square');
            //tdi.first().attr('data-icon', 'minus-square');
        }
    } );

    // Remove old event listener
    $('thead', tableSelector).off('click');
    // Add event listener for opening and closing details
    $('thead', tableSelector).on('click', 'th.details-control', function () {
        var tdi = $(this);
        var tableHtml = $(this).closest('table')
        var trs = $('tbody > tr', tableHtml);

        for(i=0; i<trs.length; i++){
            tr = trs[i];
            var row = table.row(tr);
            var tdiInner = $('.details-control a', tr);
            if(tdi.hasClass( "shown" )){
                // This row is already open - close it
                row.child.hide();
                $(tr).removeClass('shown');
                tdiInner.first().removeClass('fa-icon-red');
                tdiInner.first().addClass('fa-icon-green');
            }
            else {
                // Open this row
                if(row.data() != null){
                    row.child(renderOLIs(row.data().olis)).show();
                }
                $(tr).addClass('shown');
                tdiInner.first().removeClass('fa-icon-green');
                tdiInner.first().addClass('fa-icon-red');
            }
        }

        var svg = $('svg', tdi);

        if(tdi.hasClass( "shown" )){
            tdi.removeClass('shown');
            svg.removeClass('fa-minus-square');
            svg.addClass('fa-plus-square');
            svg.attr('data-icon', 'plus-square');
        } else{
            tdi.addClass('shown');
            svg.removeClass('fa-plus-square');
            svg.addClass('fa-minus-square');
            svg.attr('data-icon', 'minus-square');
        }
        
    } );

    table.on("user-select", function (e, dt, type, cell, originalEvent) {
        if ($(cell.node()).hasClass("details-control")) {
            e.preventDefault();
        }
    });
}

$(document).on("click", "#confirmLinkButton", function () {
    $("#overlayProModalUpsell").show();
    childOrderId = $("#upsellOrderModal #h1MainOrderName").data('id');
    var dataTableElement = $('#dataTable-UPSELL');
    var dataTable = dataTableElement.DataTable();
    parentOrder = getSelectedRows(dataTableElement, dataTable)[0];
    parentOrderId = parentOrder['id'];
    confirmLinkButton(childOrderId, parentOrderId);
});

function confirmLinkButton(childOrderId, parentOrderId){
    $.ajax({
        type: "POST",
        url: "/linkParentOrder/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'parent_order_id': parentOrderId, 'child_order_id': JSON.stringify(childOrderId) },
        success: function (e) {            
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro");
            $("#overlayProModalUpsell").hide();            
            $("#upsellOrderModal").modal('hide');
            refreshDatatables();
        },
        complete: function() {
            $("#overlayProModalUpsell").hide();            
            $("#upsellOrderModal").modal('hide');
            refreshDatatables();
        }
    });
}

function unlinkParentOrder(orderId){
    $("#overlayPro").show();
    $.ajax({
        type: "POST",
        url: "/unlinkParentOrder/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'orderId': orderId },
        success: function (e) {            
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro");
            refreshDatatables();
        },
        complete: function() {
            refreshDatatables();
        }
    });
}

function attachOrder(orderId, parentOrderId){
    $("#overlayProModalUpsell").show()();
    $.ajax({
        type: "POST",
        url: "/attachOrder/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        data: { 'orderId': orderId, 'parentOrderId': parentOrderId },
        success: function (e) {            
            if (e.status_code == 200) {toastr.success(e.message)}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro");
            $("#overlayProModalUpsell").hide();
            refreshDatatables();
        },
        complete: function() {
            $("#overlayProModalUpsell").hide();
            refreshDatatables();
        }
    });
}

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
            { "data": "order_purchase__serial_number" },
        ],
        "language": {
            "emptyTable": "Não existem produtos neste pedido",
            "loadingRecords": "Carregando os produtos..."
        }
    });
}

function getSelectedRows(dataTableElement, dataTable){
    var trs = $('tbody > tr', dataTableElement);
    var rows = [];

    for(i=0; i<trs.length; i++){
        tr = trs[i];
        if($('.custom-control-input' , tr).length > 0 && $('.custom-control-input' , tr)[0].checked){
            rows.push(dataTable.row(tr).data());
        }
    }
    return rows;
}

function getUpsellSelectedRows(dataTableElement, dataTable){
    var trs = $('tbody > tr', dataTableElement);
    var rows = [];

    for(i=0; i<trs.length; i++){
        tr = trs[i];
        if($('.toggle-demo' , tr).length > 0 && $('.toggle-demo' , tr)[0].checked){
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

    return (
        dateTimeObj.getUTCFullYear() + '-'
        + formatDateNumber(dateTimeObj.getMonth() + 1) + '-'
        + formatDateNumber(dateTimeObj.getDate()) + ' '
        + formatDateNumber(dateTimeObj.getHours()) + ':'
        + formatDateNumber(dateTimeObj.getMinutes())
    );
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
        case 'AI':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "created_date" ,
                        "render": function(data, type, row, meta) {
                            return formatDateTime(data)
                        }
                    },
                    { "data": "client_name" },
                    { "data": "address" },
                    { "data": "state" },                    
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            if(row.has_child){
                                return '';
                            } else{
                                return '<a class="btn btn-xs fa-icon-grey attachOrder" data-id="'+data+'" id="attachOrder" type="button"><i class="fas fa-link" style="font-size: large"></i></a>';
                            }                            
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
                        } 
                    }
                ];
            break;
        case 'AO':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "address" ,
                        "render": function(data, type, row, meta) {
                            return '<td>'+row.street+', '+row.street_number+'</td>'
                        } 
                    },
                    { "data": "state" },
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
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
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
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
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
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
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
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
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
                        } 
                    }
                ];
            break;
        case 'AS':
            columns = [
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
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
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
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
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
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
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
                        } 
                    }
                ];
            break;
        case 'F':
            columns = [
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
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
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
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
                    {
                        "data": "otus",
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "canceled_at" ,
                        "render": function(data, type, row, meta) {
                            return formatDateTime(data)
                        }
                    },
                    { "data": "sync_shopee",
                        "render": function(data, type, row, meta) {
                            return getSyncShopeeHtml(data);
                        }
                    },
                    { "data": "value" },
                    { "data": "free_shipping",
                        render: function (data, type, row) {
                            return data ? 'Sim' : 'Não';
                        } 
                    },                    
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<a class="btn fa-icon-orange btn-xs" data-id="'+data+'" id="viewOrderPurchaseLineItems" type="button" data-toggle="modal" data-target="#modalOrderPurchaseLineItems"><i class="fas fa-grip-lines"></i></a>';
                        }
                    },
                    { "data": "id",
                       "render": function(data, type, row, meta) {
                           return '<a class="btn fa-icon-yellow btn-xs" data-id="'+data+'" id="editButton" type="button" data-toggle="modal" data-target="#editOrderModal"><i class="fas fa-edit"></i></a>';
                       }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
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
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                        }
                    },
                    { "data": "client_name" },
                    { "data": "user_shopee__email"},
                    { "data": "error_date",
                        "render": function(data, type, row, meta) {
                            return formatDateTime(data)
                        }
                    },
                    { "data": "error"},
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                       "render": function(data, type, row, meta) {
                           return '<a class="btn fa-icon-yellow btn-xs" data-id="'+data+'" id="editButton" type="button" data-toggle="modal" data-target="#editOrderModal"><i class="fas fa-edit"></i></a>';
                       }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
                        } 
                    }
                ];
            break;
        case 'DO':
            columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'" type="checkbox"><label class="custom-control-label" for="'+data+'"></label></div>'
                        }
                    },                    
                    {
                        "data": "otus",
                        "defaultContent": '',
                        "render": function (data, type, row, meta) {
                            return renderHasUpsell(data);
                        },
                        width:"15px"
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "client_name" },
                    { "data": "address" ,
                        "render": function(data, type, row, meta) {
                            return '<td>'+row.street+', '+row.street_number+'</td>'
                        }
                    },
                    { "data": "state" },                    
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "id",
                       "render": function(data, type, row, meta) {
                           return '<a class="btn fa-icon-yellow btn-xs" data-id="'+data+'" id="editButton" type="button" data-toggle="modal" data-target="#editOrderModal"><i class="fas fa-edit"></i></a>';
                       }
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    },
                    { "data": "otus", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOTUs(data);
                        } 
                    }
                ];
                break;
            case 'UPSELL':
                columns = [
                    { "data": "id",
                        "render": function(data, type, row, meta) {
                            return '<div class="custom-control custom-checkbox"><input class="custom-control-input" id="'+data+'_UPSELL" type="checkbox"><label class="custom-control-label" for="'+data+'_UPSELL"></label></div>'
                        }
                    },
                    { "data": "name",
                        "render": function(data, type, row, meta) {
                            return '<td><a data-id="'+data+'" id="orderName">'+data+'</a></td>'
                    }},
                    { "data": "created_date" ,
                        "render": function(data, type, row, meta) {
                            return formatDateTime(data)
                        }
                    },
                    { "data": "client_name" },
                    { "data": "address" },
                    { "data": "state" },
                    {
                        "className": 'details-control',
                        "orderable": false,
                        "data": null,
                        "defaultContent": '',
                        "render": function () {
                            return '<a class="btn fa-icon-green btn-xs" type="button"><i class="fab fa-shopify" aria-hidden="true" style="font-size: large"></i></a>';
                        },
                        width:"15px"
                    },
                    { "data": "olis", "visible": false,
                        "render": function(data, type, row, meta) {
                            return renderOLIs(data);
                        } 
                    }
                ];
            break;
    }
    return columns;
}

$(document).on("click", "#editButton", function () {
    orderId = $(this).data('id')
    loadEditOrderModal(orderId, orderName);
});

function loadEditOrderModal(orderId){
    $("#overlayProModal").show();
    $.ajax({
        type: "GET",
        url: "/vendorOrderEdit/"+orderId+"/",
        headers: { "X-CSRFToken": csrftoken },
        traditional: true,
        success: function (response) {
            orderToEdit = response.data[0];
            $("#h1OrderName").text(orderToEdit.name);
            loadModalInfo(orderToEdit);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            toastr.error("Deu erro");
            $("#overlayProModal").hide();
        },
        complete: function() {
            $("#overlayProModal").hide();
        }
    });
}

function loadModalInfo(order){
    $('#clientName').val(order.client_name);
    $('#clientPhone').val(order.client_phone);
    $('#street').val(order.street);
    $('#street_number').val(order.street_number);
    $('#complement').val(order.complement);
    $('#zip_code').val(order.zip_code);
    $('#city').val(order.city);
    $('#state').val(order.state);
    $('#neighborhood').val(order.neighborhood);
    $('#cpf').val(order.cpf);
    $('#orderId').val(order.id);
}

function setUpsellButtonListeners(tableSelector){

    $('tbody', tableSelector).on('click', 'button.upsellDetails', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
        }
        else {
            // Open this row
            row.child(renderOTUs(row.data().otus)).show();
        }
    } );
}

$(document).on("click", ".processUpsellButton", function () {
    $("#overlayProModal").show();
    var dataTableElement = $('#dataTable-AI');
    var dataTable = dataTableElement.DataTable();
    var rows = getSelectedRows(dataTableElement, dataTable);

    var dataTableElement = $('#dataTable-UPSELL');
    var dataTable = dataTableElement.DataTable();
    var rowsUpsell = getUpsellSelectedRows(dataTableElement, dataTable);
    if(rows.length > 0){    
        if (!confirm('Os seus pedidos serão processados, deseja continuar?')){
            $("#overlayProModal").hide()
            return false;
        } 
        dataToSend = JSON.stringify(rows);
        dataToSendUpsell = JSON.stringify(rowsUpsell);
        $.ajax({
            type: "POST",
            url: "/processUpsell/",
            headers: { "X-CSRFToken": csrftoken },
            traditional: true,
            data: { 'orders': dataToSend,
                    'ordersUpsell': dataToSendUpsell
            },
            success: function () {
                toastr.success("Pedidos enviados para processamento")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                toastr.error("Deu erro")
                $("#overlayProModal").hide()
            },
            complete: function() {
                refreshDatatables();
            }
        });

    }
    else{
        $("#overlayProModal").hide();
    }
});

function getSyncShopeeHtml(syncShopee){
    if(syncShopee){
        return '<div data-id="'+syncShopee+'"  id="sync_shopee" class="badge badge-warning badge-pill">A cancelar</div>'
    } else {
        return '<div data-id="'+syncShopee+'"  id="sync_shopee" class="badge badge-success badge-pill">Cancelado</div>'
    } 
}

function initializeDatePicker() {
    moment.locale('pt')

    start = moment().subtract(7, "days");
    end = moment();

    var dateFilterObj = getDateFilterCookie();
    var rangeLabel = dateFilterObj.dateFilterLabel;

    if(rangeLabel != null && rangeLabel != 'Personalizado'){
        var dateRange = getDateValueByRangeLabel(rangeLabel);
        start = dateRange[0];
        end = dateRange[1];
    } else if(rangeLabel == 'Personalizado'){
        var rangeValues = dateFilterObj.dateFilterValue;
        var aux = rangeValues.split('_')
        if(aux.length > 0){
            var startDateStr = aux[0];
            var endDateStr = aux[1];

            var startDate = new Date(startDateStr);
            var endDate = new Date(endDateStr);

            start = moment(startDate);
            end = moment(endDate);
        }        
    }

    function cb(start, end) {
        $("#daterange span").html(
            start.format("MMMM D, YYYY") + " - " + end.format("MMMM D, YYYY")
        );
    }

    $("#daterange").daterangepicker(
        {
          locale: {
                "format": "MM/DD/YYYY",
                "separator": " - ",
                "applyLabel": "Filtrar",
                "cancelLabel": "Cancelar",
                "fromLabel": "From",
                "toLabel": "To",
                "customRangeLabel": "Personalizado",
                "weekLabel": "S",
                "daysOfWeek": [
                    "Dom",
                    "Seg",
                    "Ter",
                    "Qua",
                    "Qui",
                    "Sex",
                    "Sab"
                ],
                "monthNames": [
                    "Janeiro",
                    "Fevereiro",
                    "Março",
                    "Abril",
                    "Maio",
                    "Junho",
                    "Julho",
                    "Agosto",
                    "Setembro",
                    "Outubro",
                    "Novembro",
                    "Dezembro"
                ],
                "firstDay": 1
            },
            startDate: start,
            endDate: end,
            ranges: {
                Hoje: getDateValueByRangeLabel('Hoje'),
                Ontem: getDateValueByRangeLabel('Ontem'),
                "Últimos 7 dias": getDateValueByRangeLabel('Últimos 7 dias'),
                "Últimos 30 dias": getDateValueByRangeLabel('Últimos 30 dias'),
                "Este mês": getDateValueByRangeLabel('Este mês'),
                "Mês passado": getDateValueByRangeLabel('Mês passado'),
                "Este ano": getDateValueByRangeLabel('Este ano'),
            },
        },
        cb
    );

    cb(start, end);

    $('#daterange').on('apply.daterangepicker', function(ev, picker) {
        refreshDatatables();
        setDateFilterCookie(picker);
    });
}

function getDateValueByRangeLabel(rangeLabel){
    switch(rangeLabel){
        case 'Hoje':
            return [moment(), moment()];
        case 'Ontem':
            return  [moment().subtract(1, "days"), moment().subtract(1, "days")];
        case 'Últimos 7 dias':
            return [moment().subtract(6, "days"), moment()];
        case 'Últimos 30 dias':
            return [moment().subtract(29, "days"), moment()];
        case 'Este mês':
            return [moment().startOf("month"), moment().endOf("month")];
        case 'Mês passado':
            return [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")];
        case 'Este ano':
            return [moment().startOf("year"), moment().endOf("year")];
        default:
            return [moment().subtract(6, "days"), moment()];
    }
}

/* Formatting function for OrderLineItems */
function renderOLIs ( d ) {
    if(d == null){
        return ''
    }
    // `d` is the original data object for the row
    var table = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';

    //header
    table = table + '<tr>' +
                        '<th>Produto</th>'+
                        '<th>Variante</th>'+
                        '<th>Mapeamento</th>'
                    '</tr>'


    for(var i = 0; i <d.length; i++) {
        oli = d[i];

        var innerHtml = '<tr>'+
                            '<td>'+oli.product_variant__product_shopify__title+'</td>'+
                            '<td>'+oli.product_variant__title+'</td>'
                            +`<td>
                                <a
                                    type="button"
                                    id="viewMappingBtn"
                                    class="btn btn-primary"

                                    data-pvid=${oli.product_variant__id}
                                    data-pvname="${oli.product_variant__product_shopify__title}"
                                    data-pvtitle="${oli.product_variant__title}"
                                    data-toggle="modal"
                                    data-target="#exampleModal"
                                >Ver mapeamento</a>
                            </td>`
                        '</tr>';
        table = table + innerHtml;
    }

    table = table + '</table>';
    return table;
}

/* Formatting function for Order with Upsell */
function renderOTUs ( d ) {
    if(d == null || d.length < 1){
        return '';
    }
    // `d` is the original data object for the row
    var table = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';

    if(d[0].status != 'AI'){        
        //header
        table = table + '<tr>' +
                            '<th>Nome</th>'+
                            '<th>Data criação</th>'+
                            '<th>Nome do cliente</th>'+
                            '<th>Endereço</th>'+
                            '<th>Estado</th>'+
                        '</tr>'
    } else{
        
        //header
        table = table + '<tr>' +
                            '<th>Remover ligação</th>'+
                            '<th>Nome</th>'+
                            '<th>Data criação</th>'+
                            '<th>Nome do cliente</th>'+
                            '<th>Endereço</th>'+
                            '<th>Estado</th>'+
                        '</tr>'
    }

    for(var i = 0; i <d.length; i++) {
        otu = d[i];
        var innerHtml = ''
        if(otu.status != 'AI'){ 
            innerHtml = '<tr>'+
                            '<td>'+otu.name+'</td>'+
                            '<td>'+formatDateTime(otu.created_date)+'</td>'+
                            '<td>'+otu.client_name+'</td>'+
                            '<td>'+otu.client_name+'</td>'+
                            '<td>'+otu.state+'</td>'
                        '</tr>';
        } else {
            innerHtml = '<tr>'+
                            '<td>'+'<a class="btn btn-xs unlinkParentOrder fa-icon-grey" data-id="'+otu.id+'" id="unlinkParentOrder" type="button"><i class="fas fa-unlink" style="font-size: large"></i></a>'+'</td>'+
                            '<td>'+otu.name+'</td>'+
                            '<td>'+formatDateTime(otu.created_date)+'</td>'+
                            '<td>'+otu.client_name+'</td>'+
                            '<td>'+otu.client_name+'</td>'+
                            '<td>'+otu.state+'</td>'
                        '</tr>';
        }
        table = table + innerHtml;
    }

    table = table + '</table>';
    return table;
}

function renderHasUpsell(data){
    var button =''
    if(data != null && data.length > 0){
        button = '<button class="btn btn-success upsellDetails">Sim <span class="badge bg-white text-dark">'+data.length+'</span></button>';
    }
    else{
        button = '<button class="btn btn-light">Não <span class="badge bg-white text-dark">0</span></button>';
    } 
    return button;
}

$(document).on("click", "#viewMappingBtn", function() {
    const id      = $(this).data("pvid");
    const name    = $(this).data("pvname");
    const variant = $(this).data("pvtitle");

    hideProductFormMappingModal();
    return showProductTableMappingModal(id, name, variant);
});

$("#trackingToggle").on("click", function() {
    tracking = !tracking;
    getOrders("AS");
});
