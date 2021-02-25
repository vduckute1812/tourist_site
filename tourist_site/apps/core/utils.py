from django.conf import settings


def get_public_url():
    return 'http://' + settings.PUBLIC_PAGE
