var csrftoken2 = "";
var spc_f = "";
var spc_si = "";
var spc_ec = "";
var spc_u = "";
var seed;
var returned = "";
var ctype = window.location.href.indexOf("google") != -1;
var email = null;
var counterInterval;

function startSmsResendCounter() {
  var counter = parseInt(counterSeconds);
  var counterInterval = setInterval(() => {
    counter--;
    $("#resend_sms").text("Aguarde " + counter + " segundos para reenviar.");
    if (counter === 0) {
      clearInterval(counterInterval);
      addResendMessage();
    }
  }, 1000);
}

function addResendMessage() {
  $("#resend_sms").html(
    "Não recebeu o código? <button id='resend_button'>Reenviar</button>"
  );

  $("#resend_button").click(function (e) {
    e.preventDefault();
    $("#resend_button").attr("disabled", "disabled");
    startSmsResendCounter();

    $.ajax({
      type: "POST",
      url: "/vendorUserResendSmsApi/",
      headers: { "X-CSRFToken": csrftoken },
      data: {
        email: $("#email").val(),
        captcha_signature: $("#captcha_signature").val(),
        csrftoken: csrftoken2,
        spc_f: spc_f,
        spc_si: spc_si,
        spc_ec: spc_ec,
        proxy: $("#proxy").val(),
        phone: ctype ? $("#g_phone").val() : $("#phone").val(),
        ctype: ctype,
        port: $("#port").val(),
        proxy_login: $("#proxy_login").val(),
        proxy_password: $("#proxy_password").val(),
      },
      success: function (e) {
        if (e.status_code == 200) {
          toastr.success(e.message);
        }
        if (e.status_code == 404) {
          toastr.error(e.message);
        }
      },
      error: function (XMLHttpRequest, textStatus, errorThrown) {
        toastr.error("Deu erro");
        $("#overlayPro").hide();
        $("#overlayProSms").hide();
      },
      complete: function () {},
    });
  });
}

$(".btn-confirm-phone").on("click", function (e) {
  e.preventDefault();
  var data = $(e.target).data();

  if (Object.keys(data).length < 2) {
    data = $(e.target).parent().data();
  }
  ctype = data.ctype == "G";
  email = data.email;
  $("#exampleModal").modal();
  if (ctype) {
    document.querySelector("#shopeeFormPhone").hidden = false;
    document.querySelector("#shopeeForm").hidden = true;
  }
  $("#overlayProSms").hide();
  $("#overlayPro").hide();
});

$(document).on("click", "#btnValidateUserShopee", function () {
  if (
    (ctype &&
      (!$("#proxy").val() ||
        !$("#port").val() ||
        !$("#captcha_signature").val())) ||
    (!ctype &&
      (!$("#email").val() ||
        !$("#phone").val() ||
        !$("#password").val() ||
        !$("#proxy").val() ||
        !$("#port").val() ||
        !$("#captcha_signature").val()))
  ) {
    toastr.error(FILL_ALL_FIELDS_VALIDATION_MSG);
    return;
  }
  if (!ctype) {
    try {
      $("#phone").val(
        phone($("#phone").val(), phoneErrorsMessage).validate().phoneNumber
      );
    } catch (e) {
      toastr.error(e);
      return;
    }
  }

  $("#overlayPro").show();

  $.ajax({
    type: "POST",
    url: "/vendorUserValidateJson/",
    headers: { "X-CSRFToken": csrftoken },
    data: $("#userShopeeForm").serialize(),
    success: function (response) {
      console.log(response);
      if (response.status == false) {
        if (response.code == 201) {
          console.log("error");

          if (response.message.indexOf("duplicate key value violates") > -1) {
            console.log("DUPLICATE: ");
            console.log(
              response.message.indexOf("duplicate key value violates")
            );
            toastr.error("Já existe uma conta com esse e-mail.");
          } else {
            toastr.error(response.message);
          }

          return;
        } else {
          console.log("warning");
          toastr.warning(response.message);
        }
      }

      $("#exampleModal").modal();

      if (ctype) {
        document.querySelector("#shopeeFormPhone").hidden = false;
        document.querySelector("#shopeeForm").hidden = true;
      }
      console.log({ response });
      csrftoken2 = response.csrftoken;
      spc_f = response.spc_f;
      spc_si = response.spc_si;
      spc_u = response.spc_u;
      spc_ec = response.spc_ec;
      seed = response.seed;

      $("#overlayProSms").hide();
      $("#overlayPro").hide();
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      toastr.error("Deu erro");
      $("#overlayPro").hide();
    },
    complete: function () {
      $("#overlayProSms").hide();
      $("#overlayPro").hide();
      if (!ctype) startSmsResendCounter()
    },
  });
  return false;
});

$(document).on("click", "#btnSendPhone", function (e) {
  e.preventDefault();
  console.log(e.target);
  e.target.disabled = true;
  $("#overlayProSms").show();
  $("#overlayPro").show();
  if (ctype) {
    console.log($("#g_phone").val());
    try {
      $("#g_phone").val(
        phone($("#g_phone").val(), phoneErrorsMessage).validate().phoneNumber
      );
    } catch (ex) {
      toastr.error("Telefone inválido.");
      e.target.disabled = false;
      $("#overlayProSms").hide();
      $("#overlayPro").hide();
      return;
    }
  }

  $.ajax({
    type: "POST",
    url: "/sendValidatePhoneSms/",
    headers: { "X-CSRFToken": csrftoken },
    data: {
      identity_token: $("#captcha_signature").val(),
      phone: $("#g_phone").val(),
      spc_f: spc_f,
      spc_si: spc_si,
      spc_ec: spc_ec,
      spc_u: spc_u,
      csrftoken: csrftoken2,
      email: email,
    },
    success: function (response) {
      console.log(response);
      if (response.status == false) {
        if (response.code == 201) {
          console.log("error");
          toastr.error(response.message);
          return
        } else {
          console.log("warning");
          toastr.warning(response.message);
        }
      }
      document.querySelector("#shopeeFormPhone").hidden = true;
      document.querySelector("#shopeeForm").hidden = false;
      startSmsResendCounter();

      var responseJson = JSON.parse(response);
      console.log(responseJson);

      csrftoken2 = responseJson.sessionObj.csrftoken;
      spc_f = responseJson.sessionObj.SPC_F;
      spc_si = responseJson.sessionObj.SPC_SI;
      spc_u = responseJson.sessionObj.SPC_U;
      spc_ec = responseJson.sessionObj.SPC_EC;
      seed = responseJson.sessionObj.seed;
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      toastr.error("Deu erro");
      $("#overlayPro").hide();
    },
    complete: function () {
      e.target.disabled = false;
      $("#overlayProSms").hide();
      $("#overlayPro").hide();
    },
  });
  return false;
});

$(document).on("click", "#btnValidateSms", function (e) {
  e.preventDefault();
  e.target.disabled = true;
  $("#overlayProSms").show();

  if (!ctype) {
    $.ajax({
      type: "POST",
      url: "/vendorUserValidateSmsJson/",
      headers: { "X-CSRFToken": csrftoken },
      data: {
        email: $("#email").val(),
        phone: $("#phone").val(),
        password: $("#password").val(),
        proxy: $("#proxy").val(),
        port: $("#port").val(),
        proxy_login: $("#proxy_login").val(),
        proxy_password: $("#proxy_password").val(),
        sms_code: $("#sms_code").val(),
        captcha_signature: $("#captcha_signature").val(),
        csrftoken: csrftoken2,
        spc_f: spc_f,
        spc_si: spc_si,
        activated: $("#activated").is(":checked"),
      },
      success: function (e) {
        if (e.status_code == 200) {
          toastr.success(e.message);
          window.location.replace("/vendorUsers/");
        }
        if (e.status_code == 404) {
          toastr.error(e.message);
        }
      },
      error: function (XMLHttpRequest, textStatus, errorThrown) {
        toastr.error("Deu erro");
        $("#exampleModal").modal("toggle");
      },
      complete: function () {
        e.target.disabled = false;
        $("#overlayPro").hide();
        $("#overlayProSms").hide();
      },
    });
  } else {
    console.log("[vendorUserValidateSmsGoogleJson]");
    console.log($("#g_phone").val());
    $.ajax({
      type: "POST",
      url: "/vendorUserValidateSmsGoogleJson/",
      headers: { "X-CSRFToken": csrftoken },
      data: {
        identity_token: $("#captcha_signature").val(),
        sms_code: $("#sms_code").val(),
        seed: seed,
        email: email,
        phone: $("#g_phone").val(),
        spc_f: spc_f,
        spc_si: spc_si,
        spc_ec: spc_ec,
        spc_u: spc_u,
        csrftoken: csrftoken2,
      },
      success: function (e) {
        if (e.status_code == 200) {
          toastr.success(e.message);
          window.location.replace("/vendorUsers/");
        }
        if (e.status_code == 404) {
          toastr.error(e.message);
        }
      },
      error: function (XMLHttpRequest, textStatus, errorThrown) {
        toastr.error("Deu erro");
        $("#exampleModal").modal("toggle");
      },
      complete: function () {
        e.target.disabled = false;
        $("#overlayPro").hide();
        $("#overlayProSms").hide();
      },
    });
  }

  return false;
});

$(document).on("click", "#createUser", function () {
  $("#overlayPro").show();
  $.ajax({
    type: "POST",
    url: "/createUserOnVendorAPI/",
    headers: { "X-CSRFToken": csrftoken },
    data: $("#userShopeeForm").serialize(),
    success: function (e) {
      if (e.status_code == 200) {
        toastr.success(e.message);
          window.location.replace("/vendorUsers/");
      }
      if (e.status_code == 404) {
        toastr.error(e.message);
        $("#overlayPro").hide();
      }
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      toastr.error("Deu erro");
      $("#overlayPro").hide();
    },
    complete: function () {},
  });
  return false;
});
