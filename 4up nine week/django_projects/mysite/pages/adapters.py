from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # 已經綁定過的 Google 帳號、或在個人頁按「連結 Google」，都照常進行
        if sociallogin.is_existing or sociallogin.state.get("process") == "connect":
            return
        email = (sociallogin.user.email or "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "這個 Gmail 已經有 CodeQuest 帳號了。請先用帳號密碼登入，"
                "再到「個人頁面」連結 Google，之後就能直接用 Google 登入。",
            )
            raise ImmediateHttpResponse(redirect("login"))
