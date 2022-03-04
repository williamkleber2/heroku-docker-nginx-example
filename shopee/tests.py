from django.test import SimpleTestCase
from .views.order import fmt_gmt

class OrderUtilsTestCase(SimpleTestCase):
    """ Testa os métodos utilitários de formatação de hora. """

    def test_fmt_gmt(self):
        self.assertEquals("-08:00", fmt_gmt("480"))
        self.assertEquals("-03:00", fmt_gmt("180"))
        self.assertEquals("+00:00", fmt_gmt("0"))
        self.assertEquals("+03:00", fmt_gmt("-180")) 