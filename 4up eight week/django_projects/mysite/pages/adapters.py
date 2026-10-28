from urllib.parse import urlencode

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse


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

        # 走到這裡代表是「第一次用 Google 登入」，接下來會自動建立新帳號。
        # 建好後先帶去設定 CodeQuest 密碼，設定完（或跳過）再回到原本要去的頁面。
        next_url = sociallogin.state.get("next") or "/"
        sociallogin.state["next"] = reverse("set_password") + "?" + urlencode({"next": next_url})
