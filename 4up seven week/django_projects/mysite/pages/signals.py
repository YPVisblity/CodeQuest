from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def show_onboarding_for_new_user(request, user, **kwargs):
    # 用 Google 第一次登入（等於註冊）時，也顯示新手教學
    request.session["show_onboarding"] = True
