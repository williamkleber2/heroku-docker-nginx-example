function phone(phoneNumber, errorsMessage) {
  function clearString(str) {
    return str.replace(/[^0-9]/gi, "");
  }

  this.phoneNumber = clearString(phoneNumber);
  this.ddi = "55";
  this.dddList = [
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "21",
    "22",
    "24",
    "27",
    "28",
    "31",
    "32",
    "33",
    "34",
    "35",
    "37",
    "38",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "51",
    "53",
    "54",
    "55",
    "61",
    "63",
    "64",
    "65",
    "66",
    "67",
    "68",
    "69",
    "71",
    "73",
    "74",
    "75",
    "77",
    "79",
    "81",
    "82",
    "83",
    "84",
    "85",
    "86",
    "87",
    "88",
    "89",
    "91",
    "92",
    "93",
    "94",
    "95",
    "96",
    "97",
    "98",
    "99",
  ];

  this.getDDI = function () {
    return this.phoneNumber.slice(0, 2);
  };

  this.getDDD = function () {
    return this.phoneNumber.slice(2, 4);
  };

  this.getPhone = function () {
    return this.phoneNumber.slice(4);
  };

  this.validate = function () {
    if (this.getDDI() !== "55") {
      throw Error(errorsMessage.PHONE_VALIDATION_ERROR_DDI_MSG);
    } else if (this.dddList.indexOf(this.getDDD()) === -1) {
      throw Error(errorsMessage.PHONE_VALIDATION_ERROR_DDD_MSG);
    } else if ([8, 9].indexOf(this.getPhone().length) === -1) {
      throw Error(errorsMessage.PHONE_VALIDATION_ERROR_PHONE_MSG);
    } else if (this.getPhone().length === 9 && this.getPhone()[0] !== "9") {
      throw Error(errorsMessage.PHONE_VALIDATION_ERROR_PHONE_MSG);
    }

    return this;
  };

  return this;
}
