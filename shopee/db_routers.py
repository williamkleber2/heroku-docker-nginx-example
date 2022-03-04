from typing import Optional, TypedDict
from django.db.models import Model


class Hints(TypedDict, total=False):
    """ Classe de hints. """

    instance: Model


class ReplicaRouter:
    """ Classe do router replica. """

    def db_for_read(
        self,
        model: type[Model],
        **hints: Hints,  # `instance` not exist in this method
    ) -> str:
        """
        Sugere o banco `replica` para as operações de leitura sobre
        `model`.
        """
        return "replica"
