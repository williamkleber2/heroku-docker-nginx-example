const _ModalFormID           = "#modalFormMapping";
const _ModalTableID          = "#modalTableMapping";
const _ProductFormID         = "#productMappingForm";
const _MappingDataTableID    = "#mappingDataTable";
const _SaveProductButtonID   = "#saveMappingModalBtn";
const _DeleteProductButtonID = "#deleteProductButton";
const _CreateMappingButtonID = "#createMappingButton";
const _FormOverlayID         = "#mappingFormOverlay";

// Functions

function _setProductMappingData(id, name, variant) {
    $(_ModalTableID).data("id", id);
    $(_ModalTableID).data("name", name);
    $(_ModalTableID).data("variant", variant);

    $(`${_ModalTableID} .page-header-title`).text("Produto: " + name);
    $(`${_ModalTableID} .page-header-subtitle`).text("Variante: " + variant);
};

function _setProductFormData(id, name, variant) {
    $(_ModalFormID).data("id", id);
    $(_ModalFormID).data("name", name);
    $(_ModalFormID).data("variant", variant);

    $(`${_ModalFormID} .page-header-title`).text("Produto: " + name);
    $(`${_ModalFormID} .page-header-subtitle`).text("Variante: " + variant);
};

function _showProductTableMappingModal(id, name, variant) {
    _setProductMappingData(id, name, variant)
    return $(_ModalTableID).show();
};

function _showProductFormMappingModal(id, name, variant) {
    _setProductFormData(id, name, variant);
    return $(_ModalFormID).show();
};

function _hideProductTableMappingModal() {
    return $(_ModalTableID).hide();
};

function _hideProductFormMappingModal() {
    return $(_ModalFormID).hide();
};

function _resetProductTableMappingModal() {
    _setProductMappingData('', '', '');
    $(_MappingDataTableID).DataTable().destroy();
};

function _loadProductDataTableMappingModal(id) {
    $(_MappingDataTableID).DataTable({
        "ajax": `/vendorProductsJson/${id}`,
        "columns": [
            {"data": "shopee_url", "render": _renderProductURL},
            {"data": "quantity"}, {"data": "option_name"},
            {"data": "id", "render": _renderProductID},
        ],
    });
};

function _renderProductURL(data, type, row, meta) {
    return `<td>
                <a href="${data}" target="_blank">
                    ${data}
                </a>
            </td>`
};

function _renderProductID(data, type, row, meta) {
    return `<a
                class="btn btn-danger btn-xs"
                id="${_DeleteProductButtonID.slice(1)}"
                data-id="${data}"
                type="button"
                data-toggle="modal"
            ><i class="fas fa-trash"></i></a>`
};

function _resetProductFormMappingModal() {
    $(_ProductFormID).trigger("reset");
    _setProductFormData('', '', '');

    resetFormErrors();

    $("#optionsName").empty().prop("disabled", true);
    $("#saveMappingModalBtn").prop("disabled", true);
    $("#searchOptionsBtn")   .prop("disabled", false);
};

function showProductTableMappingModal(id, name, variant) {
    _resetProductTableMappingModal();
    _loadProductDataTableMappingModal(id);
    _showProductTableMappingModal(id, name, variant);
};

function hideProductTableMappingModal() {
    _resetProductTableMappingModal();
    _hideProductTableMappingModal();
};

function showProductFormMappingModal(id, name, variant) {
    $(_FormOverlayID).hide();

    _resetProductFormMappingModal();
    _showProductFormMappingModal(id, name, variant);
};

function hideProductFormMappingModal() {
    _resetProductFormMappingModal();
    _hideProductFormMappingModal();
};

function resetFormErrors() {
    $("#shopeeUrl-errors").text('');
    $("#quantity-errors").text('');
};

function showVariants(variants) {
    $('#optionsName').empty();

    for (const variant in variants){
        if (variants.length == 1){
            $('#optionsName').append('<option value="'+variants[variant][1]+'">Sem opção</option>');
        } else {
            $('#optionsName').append('<option value="'+variants[variant][1]+'">'+variants[variant][0]+'</option>');
        }
    };

    $("#optionsName").prop("disabled", false);
};

// Listeners

$(document).on("click", _CreateMappingButtonID, function() {
    const id      = $(_ModalTableID).data("id");
    const name    = $(_ModalTableID).data("name");
    const variant = $(_ModalTableID).data("variant");

    hideProductTableMappingModal();
    showProductFormMappingModal(id, name, variant);
});

$(document).on("click", _DeleteProductButtonID, function() {
    const self = $(this);

    if (self.data("locked"))
        return toastr.warning("Este produto já está sendo excluído.")

    if (!confirm("Deseja excluir este mapeamento?"))
        return;

    self.data("locked", true);
    $(_FormOverlayID).show();

    // See `_renderProductID`.
    const productID = self.data("id");

    return $.ajax({
        type: "POST",
        url: "/vendorProductDeleteJson/",
        data: {"shopeeProductId": productID},
        headers: {"X-CSRFToken": csrftoken},

        success: () => {
            toastr.success("Deletado com sucesso!")
        },
        error: (XMLHttpRequest, textStatus, errorThrown) => {
            if (XMLHttpRequest.status === 404)
                return toastr.error(XMLHttpRequest.responseText);

            toastr.error("Não foi possível deletar o produto.");

            console.log(XMLHttpRequest, textStatus, errorThrown);
        },
        complete: () => {
            self.data("locked", false);
            $(_FormOverlayID).hide();
        },
    });
});

$(document).on("click", _SaveProductButtonID, function () {
    $("#overlayProModal").show()

    const id      = $(_ModalFormID).data("id");
    const name    = $(_ModalFormID).data("name");
    const variant = $(_ModalFormID).data("variant");

    $.ajax({
        type: "POST",
        url: "/vendorProductCreate/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "shopeeUrl": $("#shopeeUrl").val(),
            "quantity": $("#quantity").val(),
            "variantId": id,
            "optionsNameText": $("#optionsName").find(":selected").text(),
            "optionsNameValue": $("#optionsName").val()
        },

        success: () => {
            toastr.success("Registrado com sucesso!")
            showProductFormMappingModal(id, name, variant);
        },
        error: (XMLHttpRequest, textStatus, errorThrown) => toastr.error("Deu erro"),
        complete: () => $("#overlayProModal").hide(),
    });

    return false;
});

$("#searchOptionsBtn").click(function (event) {
    event.preventDefault();

    $(_FormOverlayID).show();

    return $.ajax({
        type: "POST",
        url: "/vendorProductGetVariant/",
        headers: { "X-CSRFToken": csrftoken },
        data: $(_ProductFormID).serialize(),

        success: function (data) {
            $('#shopeeUrl').val(data['shopeeUrl']);
            showVariants(data['variants']);

            $("#saveMappingModalBtn").prop("disabled", false);
            $("#searchOptionsBtn")   .prop("disabled", true );

            toastr.success("Carregado com sucesso.")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if (XMLHttpRequest.status === 400) {
                const json = JSON.parse(XMLHttpRequest.responseText);

                console.log(XMLHttpRequest.responseText);
                console.log(json);

                resetFormErrors();

                for (const key in json) {
                    const alertHTML = text => `
                        <div class="alert alert-danger p-3 mt-1" role="alert">
                            ${text}
                        </div>`;

                    const reducer = (acc, el) => acc + alertHTML(el.message);
                    const alerts = json[key].reduce(reducer, '');

                    $(`#${key}-errors`).show().html(alerts);
                };

                return toastr.warning("Preencha os campos corretamente.");
            };

            toastr.error("Não foi possível completar a operação.");

            console.log(textStatus, errorThrown);
            console.log(XMLHttpRequest);
        },
        complete: () => $(_FormOverlayID).hide(),
    });
});
