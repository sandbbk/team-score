from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from user_authenticate.models import (User, Key)


def send_mail(to_email, subject, template, context):

    from_email = 'djangoandrest@gmail.com'
    html_content = render_to_string(template, {'context': context})
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def key_expired(obj):
    #  Checks that users key is expired.
    if isinstance(obj, User):
        key = Key.objects.get(user=obj)
    else:
        key = Key.objects.get(data=obj)
    return (True, key) if key.expire_time <= timezone.now() else (False, key)


def is_zombie(user):
    """
        Checks if user is active, and if it False checks user's key for expiration,
        returns True if key is expired.
    """
    try:
        if user.is_active:
            return False
        expired, key = key_expired(user)
        if expired:
            return True
        else:
            return False
    except Key.DoesNotExist:
        return True


def cap_to_player(request):

    # Auto update players field with captain.pk and team.admin with user.

    players = request.data.get('players')
    captain = request.data.get('captain')

    if players is None:
        players = []
    if captain not in players:
        players.append(captain)
    request.data.update(admin=request.user.pk, players=players)
    return request.data

