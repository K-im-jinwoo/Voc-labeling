def add_target_user(request):
    if request.user.is_authenticated:
        return {"target_user": request.user}
    else:
        return {}
