from django.core.management.base import BaseCommand
from django.db import transaction

from shopee.models import OrderLineItem


class DataRepairCommand(BaseCommand):
    """ Classe do comando de reparar os dados. """

    def handle(self, *args, **options) -> None:
        """ Handler do comando.
        :param args: Os args.
        :param options: As opções. """

        with transaction.atomic():
            (OrderLineItem.objects
                .filter(sync_shopee=True)
                .update(cancellation_status='C'))
