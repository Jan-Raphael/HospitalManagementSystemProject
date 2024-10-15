
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'adminprofile') and user.adminprofile.is_admin

