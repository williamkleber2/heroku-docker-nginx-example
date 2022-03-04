from .models import News, UserNewsNotification
from django.conf import settings

from datetime import timedelta
from typing import List, Tuple, Dict, Union

from django.utils import timezone

from . import models

Alerts = models.Alert.objects


def get_enviroment_variables(request) -> Dict[str, str]:
    """ Pega as variáveis de ambiente.
    :param request: O objeto da request.
    
    :returns: As variáveis de ambiente em um dicionário. """

    return { 
        "REPORT_CHECK_STATUS_INTERVAL": settings.REPORT_CHECK_STATUS_INTERVAL,
        "REPORT_TIMEOUT_MS": settings.REPORT_TIMEOUT_MS,
    }


def get_sentry_dsn(request) -> Dict[str, str]:
    """ Pega a variável de ambiente do Sentry DSN.
    :param request: O objeto da request.
    
    :returns: Um dicionário contento a varíavel de ambiente. """

    return { "SENTRY_DSN": settings.SENTRY_DSN }


def google_analytics(request) -> Dict[str, str]:
    """ Pega a variável de ambiente do Google Analytics.
    :param request: O objeto da request.
    
    :returns: Um dicionário contendo a variável de ambiente. """

    if settings.DEBUG:
        return {}

    return {
        "GOOGLE_ANALYTICS_ID": settings.GOOGLE_ANALYTICS_ID,
    }

def get_alerts(request) -> Dict[str, List[models.Alert]]:
    """ Pega os alertas.
    :param request: O objeto da request.
    
    :returns: Um dicionário contendo uma lista de alertas. """

    now = timezone.localdate()

    alerts = Alerts.filter(active=True, expiration_date__gte=now)
    alerts = alerts.order_by("-updated_at")
    alerts = list(alerts)

    return {
        "alerts": alerts,
    }


def get_user_news(request) -> Dict[str, Union[Tuple[List[News], List[UserNewsNotification]], str]]:
    """ Pega as novidades do usuário.
    :param request: O objeto da request.
    
    :returns: Um dicionário com as novidades, notificações e o URL de todas as novidades. """

    user = request.user

    if not user.is_authenticated:
        return {}

    news, nots = _get_news(user)
    return {
        "news": news,
        "nots": nots,
        "all_news_notion_link": settings.NOTION_NEWS_URL,
    }


def _get_news(user) -> Tuple[List[News], List[UserNewsNotification]]:
    """ Pega as novidades e notificações do usuário.
    :param user: O usuário para quem pegar.
    
    :returns: Duas listas contendo as notícias e notificações, respectivamente. """

    MAX_NOTIFICATIONS = 5

    us = UserNewsNotification.objects.filter(user=user)
    us = us.order_by("created_at")
    us_id = us.values_list("news__id")

    ns = News.objects.filter(created_at__gt=user.date_joined)
    ns = ns.order_by("-created_at")
    ns = ns.exclude(id__in=us_id)[:MAX_NOTIFICATIONS]

    ns = list(ns)

    us = []
    if len(ns) < MAX_NOTIFICATIONS:
        us = UserNewsNotification.objects.filter(user=user)
        us = us.order_by("-created_at")
        us = us.exclude(news__in=ns)[: MAX_NOTIFICATIONS - len(ns)]
        us = list(us)

    return ns, us
