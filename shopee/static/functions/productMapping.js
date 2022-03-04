const _ModalFormID           = "#modalFormMapping";
const _ModalTableID          = "#modalTableMapping";
const _ProductFormID         = "#productMappingForm";
const _MappingDataTableID    = "#mappingDataTable";
const _SaveProductButtonID   = "#saveMappingModalBtn";
const _DeleteProductButtonID = "#deleteProductButton";
const _CreateMappingButtonID = "#createMappingButton";
const _FormOverlayID         = "#mappingFormOverlay";
const _TableOverlayID        = "#mappingTableOverlay";
const _LabelVendorURL        = "#url";
const _BackToTableButtonID   = "#backToTableButton";
const _VariationOptionsID    = "#variationOptions";
const _VariationErrorID      = "variationError";
const _VariationOptionClassName = "0x1a";
const _CarrierOptionClassName   = "0x1b";
const _OptionIDPrefix        = "op-";
const _SelectClassName       = "0x1d";
const _CarriersDivID            = "#carriersOptions";

var _vendor;
var gId,
    gName,
    gVariant,
    gCarriers,
    gVariations;

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
        "ajax": `/vendorProductsJson/${id}/`,
        "columns": [
            {
                "data": "vendor",
                "render": function(data, type, row) {
                    return `<div style="text-align: center;"><img src="/static/assets/img/vendors/${data}.png" width="50" height="50"/></div>`
                }
            },
            {"data": "shopee_url", "render": _renderProductURL},
            {"data": "quantity"},
            {"data": "option_name"},
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

function getVendorProductURLSample(vendor) {
    const BASE = "URL para um produto do fornecedor";
    const URLs = {
        shopee:     "https://shopee.com.br/",
        aliexpress: "https://pt.aliexpress.com/item/"
    };

    return URLs[vendor] || BASE;
};

function showProductTableMappingModal(id, name, variant) {
    $(_TableOverlayID).hide();
    _resetProductTableMappingModal();
    _loadProductDataTableMappingModal(id);
    _showProductTableMappingModal(id, name, variant);

    hideProductFormMappingModal();
};

function hideProductTableMappingModal() {
    _resetProductTableMappingModal();
    _hideProductTableMappingModal();
};

function showProductFormMappingModal(id, name, variant) {
    $(_FormOverlayID).hide();

    url = getVendorProductURLSample(_vendor);
    $(_LabelVendorURL).attr("placeholder", url);

    _resetProductFormMappingModal();
    _showProductFormMappingModal(id, name, variant);
};

function hideProductFormMappingModal() {
    _resetProductFormMappingModal();
    _hideProductFormMappingModal();
};

function resetFormErrors() {
    $("#url-errors").text('');
    $("#vendor-errors").text('');
    $("#amount-errors").text('');
};

function resetVariationOptions() {
    $(_VariationOptionsID).text('');
};

function isEquivalent(a, b) {
    // http://adripofjavascript.com/blog/drips/object-equality-in-javascript.html

    const aProps = Object.getOwnPropertyNames(a);
    const bProps = Object.getOwnPropertyNames(b);

    if (aProps.length != bProps.length) return false;

    for (const propName of aProps)
        if (a[propName] !== b[propName]) return false;

    return true;
};

function showVariationError(type, text, clear=true) {
    const error = $('#' + _VariationErrorID);
    if (error) error.remove();

    const element = $(_VariationOptionsID);

    if (clear) element.empty();
    element.append(`
        <div
            class="alert alert-${type} mt-1"
            role="alert"
            id="${_VariationErrorID}"
        >
            ${text}
        </div>`
    );
};

function showVariations(store_id, product_id, variations) {

    variations = variations.map(e => {
        return {...e, store_id, product_id}
    });

    const variationOptionsElement = $(_VariationOptionsID);

    // Reset
    variationOptionsElement.empty();

    if (!variations)
        return showVariationError("warning",
                                  "Não há variações para este produto!");

    const option = text => `<option class="${_VariationOptionClassName}">
                                ${text}
                            </option>`;

    const options = {};

    for (const variation of variations) {
        const entries = Object.entries(variation.values);

        for (let [name, value] of entries) {
            if (!(name in options))
                options[name] = new Set();

            options[name].add(value);
        };
    };

    for (const [name, values] of Object.entries(options)) {
        const identifier = (_OptionIDPrefix + name).replaceAll(' ', '_');

        variationOptionsElement.append(`
            <label class="small mb-1 ${_SelectClassName}"
                    for="${identifier}">
                ${name}
            </label>
            <select class="form-control"
                    id="${identifier}"
                    name="${identifier}">
            </select>
        `);

        values.forEach(v => $('#' + identifier).append(option(v)))
    };

    gVariations = variations;
};

function prepareMappingSystem(id, name, variant) {
    gId = id;
    gName = name;
    gVariant = variant;

    showProductTableMappingModal(id, name, variant);
};

function getSelectedVariation() {
    const values = {};

    for (const item of document.getElementsByClassName(_VariationOptionClassName)) {

        if (item.selected) {
            values[item.parentElement.id.substring(_OptionIDPrefix.length)] = item.value;
        }
    }

    return gVariations.find(e => isEquivalent(e.values, values));
};

function getSelectedCarrier() {
    var values = {};

    if ([[], undefined, null].includes(gCarriers)) {
        return null;
    }

    for (const item of document.getElementsByClassName(_CarrierOptionClassName)) {
        if (item.selected) {
            values = { "id": item.value, "name": item.text };
        }
    }

    return gCarriers.find(e => isEquivalent(e.company, values));
}

function showCarriersError(type, text) {
    const div = $(_CarriersDivID);
    div.empty();
    div.append(`
        <div class="alert alert-${type}">
            ${text}
        </div>
    `);
};

function showCarriersSelect(carriers) {
    const carriersDiv = $(_CarriersDivID);
    carriersDiv.empty();

    if (carriers.length == 0)
        return showCarriersError(
            "warning",
            "Não há transportadoras disponíveis para este produto!",
        );

    const id = "carriers-select";
    carriersDiv.append(`
        <select
            class="form-control"
            id="${id}"
        >
        </select>
    `);
    const carriersSelect = $('#' + id);

    carriers.forEach(c => carriersSelect.append(`
        <option
            class="${_CarrierOptionClassName}"
            value="${c.company.id}"
        >
            ${c.company.name}
        </option>`
    ));

    gCarriers = carriers;

    return;
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
    $(_TableOverlayID).show();

    // See `_renderProductID`.
    const productID = self.data("id");

    return $.ajax({
        type: "POST",
        url: `/vendorProductDeleteJson/`,
        data: {"shopeeProductId": productID},
        headers: {"X-CSRFToken": csrftoken},

        success: () => {
            toastr.success("Deletado com sucesso!");
            showProductTableMappingModal(gId, gName, gVariant);
        },
        error: (XMLHttpRequest, textStatus, errorThrown) => {
            if (XMLHttpRequest.status === 404) {
                Sentry.captureMessage(XMLHttpRequest.responseText);
                return toastr.error(XMLHttpRequest.responseText);
            }

            toastr.error("Não foi possível deletar o produto.");

            console.log(XMLHttpRequest, textStatus, errorThrown);
        },
        complete: () => {
            self.data("locked", false);
            $(_TableOverlayID).hide();
        },
    });
});

$(document).on("click", _SaveProductButtonID, function () {
    $(_FormOverlayID).show();

    const id      = $(_ModalFormID).data("id");
    const name    = $(_ModalFormID).data("name");
    const variant = $(_ModalFormID).data("variant");

    const carrier = getSelectedCarrier();
    const variation = getSelectedVariation();

    if (!variation || variation.disabled) {
        $(_FormOverlayID).hide();

        showVariationError(
            "danger",
            "A variação não existe, está desabilitada e/ou não está em estoque!",
            false,
        );

        return false;
    };

    $.ajax({
        type: "POST",
        url: "/vendorProductCreate/",
        headers: { "X-CSRFToken": csrftoken },
        contentType: 'application/json',
        data: JSON.stringify( {
            "vendor": $("#vendor").val(),
            "url": $("#url").val(),
            "amount": $("#amount").val(),
            "variant_id": id,
            "option_name": Object.values(variation.values).join(','), 
            "option_value": variation.identifier,
            "variation": variation,
            "carrier": carrier,
            "carriers": gCarriers,
        }),

        success: () => {
            toastr.success("Registrado com sucesso!")
            resetVariationOptions();
            showProductFormMappingModal(id, name, variant);
        },

        error: (XMLHttpRequest, textStatus, errorThrown) => { 
            if (XMLHttpRequest.status === 403)
                return toastr.error(
                    "O produto não possui transportadoras disponíveis ou selecionadas. " +
                    "Não é possível salvar o mapeamento.",
                );

            toastr.error("Não foi possível salvar o mapemaento.");
            Sentry.captureMessage(XMLHttpRequest.responseText)
        },
        complete: () => $(_FormOverlayID).hide(),
    });

    return false;
});

$("#searchOptionsBtn").click(function (event) {
    event.preventDefault();

    resetFormErrors();
    $(_FormOverlayID).show();

    return $.ajax({
        type: "POST",
        url: `/vendorProductGetVariant/${gId}/`,
        headers: { "X-CSRFToken": csrftoken },
        data: $(_ProductFormID).serialize(),

        success: function (data) {
            data = JSON.parse(data.body);
            // showVariations(data.variations);
            showVariations(data['store_id'], data['product_id'], data.variations);
            showCarriersSelect(data.carriers);

            $("#saveMappingModalBtn").prop("disabled", false);
            $("#searchOptionsBtn")   .prop("disabled", true );

            toastr.success("Carregado com sucesso.")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if ([400, 404].includes(XMLHttpRequest.status)) {
                resetFormErrors();

                let json;
                try {
                    json = JSON.parse(XMLHttpRequest.responseText);
                } catch {
                    toastr.error("Não foi possível completar a operação.");
                    return toastr.error(XMLHttpRequest.responseText);
                }

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
            Sentry.captureMessage(XMLHttpRequest.responseText)
        },
        complete: () => $(_FormOverlayID).hide(),
    });
});

$("input[name=url]").on("change", function(e) {
    $(_SaveProductButtonID).prop("disabled", true);
    $("#searchOptionsBtn").prop("disabled", false);

    showVariationError(
        "success",
        "Clique em `Procurar opções` para ver as variantes do produto.",
    );

    showCarriersError(
        "success",
        "Clique em `Procurar opções` para ver as transportadoras do produto.",
    );
});

$(document).on("click", _BackToTableButtonID, function() {
    hideProductFormMappingModal();
    showProductTableMappingModal(gId, gName, gVariant);
});

$("#vendor").on("change", function({target}) {
    _vendor = $(target).val()

    if (_vendor === "shopee")
        $(".carriers").hide()
    else
        $(".carriers").show();
});
