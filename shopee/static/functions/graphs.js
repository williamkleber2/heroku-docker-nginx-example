(() => {
    (Chart.defaults.global.defaultFontFamily = "Metropolis"),
    '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = "#858796";

    const usersChartElement = document.getElementById("usersChart");
    const upsellChartElement = document.getElementById("upsellChart");
    const valueOrdersChartElement = document.getElementById("valueOrdersChart");
    const totalOrdersChartElement = document.getElementById("totalOrdersChart");

    const usersChartErrorElement = $("#usersChartError");
    const upsellChartErrorElement = $("#upsellChartError");
    const valueOrdersChartErrorElement = $("#valueOrdersChartError");
    const totalOrdersChartErrorElement = $("#totalOrdersChartError");

    const usersChartOverlayID = "#usersOverlay";
    const upsellChartOverlayID = "#upsellOverlay";
    const valueOrdersChartOverlayID = "#valueOrdersOverlay";
    const totalOrdersChartOverlayID = "#totalOrdersOverlay";

    const closureToShowOverlayByID = id => () => $(id).show();
    const closureToHideOverlayByID = id => () => $(id).hide();

    function number_format(number, decimals, dec_point, thousands_sep) {
        // *     example: number_format(1234.56, 2, ',', ' ');
        // *     return: '1 234,56'
        number = (number + "").replace(",", "").replace(" ", "");
        var n = !isFinite(+number) ? 0 : +number,
            prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
            sep = typeof thousands_sep === "undefined" ? "," : thousands_sep,
            dec = typeof dec_point === "undefined" ? "." : dec_point,
            s = "",
            toFixedFix = function(n, prec) {
                var k = Math.pow(10, prec);
                return "" + Math.round(n * k) / k;
            };
        // Fix for IE parseFloat(0.55).toFixed(0) = 0;
        s = (prec ? toFixedFix(n, prec) : "" + Math.round(n)).split(".");
        if (s[0].length > 3) {
            s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
        }
        if ((s[1] || "").length < prec) {
            s[1] = s[1] || "";
            s[1] += new Array(prec - s[1].length + 1).join("0");
        }
        return s.join(dec);
    };

    function drawBarValues() {
        // render the value of the chart above the bar
        var ctx = this.chart.ctx;
        ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, 'normal', Chart.defaults.global.defaultFontFamily);
        ctx.fillStyle = this.chart.config.options.defaultFontColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        this.data.datasets.forEach(function (dataset) {
            for (var i = 0; i < dataset.data.length; i++) {
            if(dataset.hidden === true && dataset._meta[Object.keys(dataset._meta)[0]].hidden !== false){ continue; }
            var model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model;
            if(dataset.data[i] !== null){
                ctx.fillText('$' + dataset.data[i], model.x - 1, model.y - 5);
            }
            }
        });
    };

    const _charts = [];
    const _valueOrdersChartIndex = 0;
    const _totalOrdersChartIndex = 1;
    const _upsellChartIndex = 2;

    const createUsersChart = (data) => {
        const users = $("#users");
        users.html('');

        const text = (value, title, color, warning, href, tooltip) => {
            if (!warning)
                warning = '';
            else
                warning = `
                <div class="card-footer d-flex align-items-center justify-content-between small">
                    <div class="text-white">
                        <a class="text-white stretched-link" href="${href}">
                            ${warning}
                        </a>
                    </div>
                </div>
                `;

            if (!tooltip)
                tooltip = '';

            return `
                <div class="col-sm mb-3">
                    <div class="card bg-${color} text-white h-100"
                    data-toggle="tooltip" data-placement="top" title="${tooltip}"
                    >
                        <div class="card-body" data-toggle="tooltip" data-placement="top">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="me-3">
                                    <div class="text-white-75 small">${title}</div>
                                    <div class="text-lg fw-bold" id="savedValue">${value}</div>
                                </div>
                            </div>
                        </div>

                        ${warning}
                    </div>
                </div>`
        }

        data.forEach(values => {
            let texts = '';
            for (const value of values)
                texts += text(...value);

            if (texts)
                users.append(`<div class="d-flex w-100">${texts}<div>`);
        });

        $(() => $("[data-toggle='tooltip']").tooltip());
    };

    const createValueOrdersChart = (data) => new Chart(valueOrdersChartElement, {
        type: "bar",
        data: data,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    time: {
                        unit: "month"
                    },
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        // Include a dollar sign in the ticks
                        callback: function(value, index, values) {
                            return "$" + number_format(value);
                        }
                    },
                    gridLines: {
                        color: "rgb(234, 236, 244)",
                        zeroLineColor: "rgb(234, 236, 244)",
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    }
                }]
            },
            legend: {
                display: true
            },
            tooltips: {
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
                callbacks: {
                    label: function(tooltipItem, chart) {
                        var datasetLabel =
                            chart.datasets[tooltipItem.datasetIndex].label || "";
                        return datasetLabel + ": $" + number_format(tooltipItem.yLabel);
                    }
                }
            }
        }
    });

    const createTotalOrdersChart = (data) => new Chart(totalOrdersChartElement, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Total",
                lineTension: 0.2,
                backgroundColor: "rgba(0, 97, 242, 0.05)",
                borderColor: "rgba(0, 97, 242, 1)",
                pointRadius: 3,
                pointBackgroundColor: "rgba(0, 97, 242, 1)",
                pointBorderColor: "rgba(0, 97, 242, 1)",
                pointHoverRadius: 3,
                pointHoverBackgroundColor: "rgba(0, 97, 242, 1)",
                pointHoverBorderColor: "rgba(0, 97, 242, 1)",
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: data.values,
            }]
        },
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    time: {
                        unit: "date"
                    },
                    gridLines: {
                        display: true,
                        drawBorder: false
                    },
                }],
                yAxes: [{
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                    },
                    gridLines: {
                        color: "rgb(234, 236, 244)",
                        zeroLineColor: "rgb(234, 236, 244)",
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    }
                }]
            },
            legend: {
                display: false
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function(tooltipItem, chart) {
                        var datasetLabel =
                            chart.datasets[tooltipItem.datasetIndex].label || "";
                        return datasetLabel + ": " + tooltipItem.yLabel;
                    }
                }
            }
        }
    });

    const createUpsellChart = data => new Chart(upsellChartElement, {
        type: "bar",
        data: data,
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    time: {
                        unit: "month"
                    },
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                }],
                yAxes: [{
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        // Include a dollar sign in the ticks
                        callback: function(value, index, values) {
                            return "$" + number_format(value);
                        }
                    },
                    gridLines: {
                        color: "rgb(234, 236, 244)",
                        zeroLineColor: "rgb(234, 236, 244)",
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    }
                }]
            },
            legend: {
                display: true
            },
            tooltips: {
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
            },
            animation: {
                onProgress: drawBarValues,
                onComplete: drawBarValues
            },
            hover: {
                animationDuration: 0
            },
        }
    });

    const chartError = (e, m) => {
        if (!e)
            return

        e.html(`<div class='alert alert-light'>${m}</div>`);
        e.show();
    };

    function doAjax (url, overlayID, elementError, createChart, chartIndex) {
        $.ajax({url,
                type: "POST",
                headers: {"X-CSRFToken": csrftoken},

                error: () => chartError(
                    elementError, "Não foi possível carregar este gráfico.",
                ),
                success: (data) => {
                    if (elementError)
                        elementError.hide();

                    if (!data || data.empty)
                        return chartError(elementError, "Não há dados suficientes.");

                    if (chartIndex !== undefined) {
                        if (_charts[chartIndex] !== undefined) {
                            _charts[chartIndex].destroy();
                            _charts[chartIndex] = undefined;
                        };

                        _charts[chartIndex] = createChart(data);
                    };
                },
                complete  : closureToHideOverlayByID(overlayID),
                beforeSend: closureToShowOverlayByID(overlayID),}
        );
    };

    const loadUsersChart = () =>
        doAjax("/graphs/users/", usersChartOverlayID,
               usersChartErrorElement, createUsersChart);

    const loadValueOrdersChart = () =>
        doAjax("/graphs/value_orders/", valueOrdersChartOverlayID,
               valueOrdersChartErrorElement, createValueOrdersChart,
               _valueOrdersChartIndex,);

    const loadTotalOrdersChart = () =>
        doAjax("/graphs/total_orders/", totalOrdersChartOverlayID,
                totalOrdersChartErrorElement, createTotalOrdersChart,
                _totalOrdersChartIndex,);

    const loadUpsellChart = () => {
        doAjax("/graphs/upsell/", upsellChartOverlayID,
            upsellChartErrorElement, createUpsellChart,
            _upsellChartIndex,);
    };

    $("#refreshUpsell")     .on("click", loadUpsellChart);
    $("#refreshValueOrders").on("click", loadValueOrdersChart);
    $("#refreshTotalOrders").on("click", loadTotalOrdersChart);

    loadUsersChart();
    loadUpsellChart();
    loadValueOrdersChart();
    loadTotalOrdersChart();
})();
