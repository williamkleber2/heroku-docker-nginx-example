from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from typing import Union

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """ Modelo Backend do Email. """

    def authenticate(self, request, username=None, password=None, **kwargs) -> Union[UserModel, User]:
        """ Autentica o email.
        :param request: O objeto da request.
        :param username: O username. [Default = None]
        :param password: A senha: [Default = None]
        :param kwargs: As kwargs.
        
        :returns: O modelo do usuário, ou o objeto do usuário em si. """

        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        except MultipleObjectsReturned:
            return User.objects.filter(email=username).order_by("id").first()
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id) -> UserModel:
        """ Pega o usuário.
        :param user_id: O ID do usuário.
        
        :returns: O usuário. """

        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
