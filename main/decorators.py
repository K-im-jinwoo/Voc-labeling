from django.http import HttpResponseForbidden

from . import models


def profile_ownership_required(func):
    def decorated(request, *args, **kwargs):
        profile = models.Profile.objects.get(pk=kwargs['pk'])
        if not profile.user == request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated