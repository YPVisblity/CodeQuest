from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.models import User

@receiver(user_signed_up)
def show_onboarding_for_new_user(request, user, **kwargs):
    # 用 Google 第一次登入（等於註冊）時，也顯示新手教學
    request.session["show_onboarding"] = True

@receiver(social_account_added)
def fill_email_from_google(request, sociallogin, **kwargs):
    # 沒填 email 的帳號連結 Google 時，順便把 Gmail 存進去，之後才能用 email 登入、忘記密碼
    user = sociallogin.user
    data = sociallogin.account.extra_data
    email = (data.get("email") or "").strip().lower()
    if user.email or not email or not data.get("email_verified"):
        return
    # 這個 Gmail 已經是別的帳號的 email，就不要寫入，避免 email 重複
    if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
        return
    user.email = email
    user.save(update_fields=["email"])
