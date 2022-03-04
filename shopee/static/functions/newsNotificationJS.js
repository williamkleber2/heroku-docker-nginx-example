$(document).on("click", "._notification", function () {
    const self = $(this);

    self.css("opacity", "0.5");
    self.data("viewed", 1)

    $.ajax({
        type: "POST",
        url: "/updateUserNewsNotification/",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            "news_id": self.data("id"),
        },
        success: function (e) {
            if (e.status_code == 200) {}
            if (e.status_code == 404) {toastr.error(e.message)}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            Sentry.captureMessage(XMLHttpRequest.responseText)
            toastr.error("Deu erro")
        },
        complete: function() {
            const notifications = $("._notification");

            let remove = true;
            notifications.each(function() {
                if ($(this).data("viewed") === 0)
                    remove = false;
            });

            if (remove === true)
                $("#notification-red-dot").hide();
        }
    });

    return true;
});
