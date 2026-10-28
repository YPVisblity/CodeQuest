import nbformat
import subprocess
import tempfile
from django.core.files.base import ContentFile
from .models import GroupAssignment, AssignmentSubmission, assignment_storage
import sys
import asyncio
import json
import base64
from io import BytesIO
from zoneinfo import ZoneInfo
from django.db.models.functions import TruncDate
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MaxNLocator
from datetime import datetime, timedelta
from django.utils import timezone
from pathlib import Path
import anthropic
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.shortcuts import render,redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from .models import Submission,Post,Reply,UserProfile,ShopItem,UserItem,LevelUnlock,AiChatUsage,AiTopicCode,Announcement,DailyGoal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView,PasswordResetView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic.edit import FormView
from django.utils.crypto import get_random_string
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.templatetags.static import static
from .level_loader import load_levels, get_levels_by_id
from .ai_rules import (
    FIXED_CODE_PLACEHOLDER,
    build_ai_code_prompt,
    build_ai_system_prompt,
    clean_ai_reply,
    needs_fixed_code,
)
from pathlib import Path
from django.urls import reverse,reverse_lazy
from django.db import transaction
from django.db.models import F, Count, Q
from .unlocking import get_unlock_status,get_chapter_number
from .forms import (AvatarUploadForm, TeacherGroupForm, TeacherGroupMembersForm,
                    GroupAssignmentForm, AssignmentSubmissionForm)
from django.shortcuts import get_object_or_404

import pybryt
from .pybryt_patch import patch_pybryt_execute_notebook

patch_pybryt_execute_notebook()
client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

DEFAULT_AVATAR_IDS = ["default1", "default2", "default3", "default4"] #預設圖片
AI_CHAT_FREE_DAILY_LIMIT = 3
AI_CHAT_POINT_COST = 5
Day_Goal_Point = {1:5,2:10,3:15}
EDITABLE_STUDENT_FILE_TYPES = {".ipynb", ".py", ".txt", ".json", ".md"}
EVALUATABLE_STUDENT_FILE_TYPES = {".ipynb"}
PYBRYT_EXECUTION_TIMEOUT_SECONDS = 120


def _apply_unlock_status(level_dict, unlock_status):
    info = unlock_status.get(level_dict.get("id"), {"unlocked": False, "reason": "login_required", "cost": None})
    level_dict["unlocked"] = info["unlocked"]
    level_dict["unlock_reason"] = info["reason"]
    level_dict["unlock_cost"] = info.get("cost")
    level_dict["unlock_test_level"] = info.get("test_level")
    level_dict["unlock_prev_chapter_gate"] = info.get("prev_chapter_gate", False)

def home(request):

    profile=None
    user_avatar_url = None
    levels = load_levels()
    levels_by_id = get_levels_by_id()
    unlock_status = get_unlock_status(request.user, levels_by_id)

    for level in levels:
        _apply_unlock_status(level, unlock_status)
    for level in levels_by_id.values():
        _apply_unlock_status(level, unlock_status)

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_avatar_url = profile.get_avatar_url()   
    

    user_points = 0 
    shop_enabled = getattr(settings, "SHOP_ENABLED", False)
    background_music_enabled = getattr(settings, "BACKGROUND_MUSIC_ENABLED", False)
    shop_items = (
        ShopItem.objects.filter(is_active=True).order_by("category", "price", "name")
        if shop_enabled
        else ShopItem.objects.none()
    )
    owned_item_ids = set()
    owned_items = []
    profile=None
    if request.user.is_authenticated:
        user_points = (
            UserProfile.objects.filter(user=request.user)
            .values_list("points", flat=True)
            .first()
            or 0
        )
        profile,created=UserProfile.objects.get_or_create(user=request.user)
        owned_item_ids=set(
            UserItem.objects.filter(user=request.user)
            .values_list("item_id",flat=True)
        )
        owned_items = UserItem.objects.filter(user=request.user).select_related("item").order_by("-purchased_at")
    background_url = None
    if profile and profile.selected_background_id:
        item = profile.selected_background
        if (item.category == "background"and item.image and UserItem.objects.filter(user=request.user, item=item).exists()):
            background_url = static(item.image)

    ai_chat_remaining_free = AI_CHAT_FREE_DAILY_LIMIT
    if request.user.is_authenticated:
        today = timezone.localdate()
        ai_chat_usage_count = (
            AiChatUsage.objects.filter(user=request.user, date=today)
            .values_list("count", flat=True)
            .first()
            or 0
        )
        ai_chat_remaining_free = max(AI_CHAT_FREE_DAILY_LIMIT - ai_chat_usage_count, 0)
    announcements = Announcement.objects.filter(is_active=True)[:5]

    day_complete = 0
    if request.user.is_authenticated:
        day_complete =min(DailyGoal.objects.filter(
            user = request.user,
            date = timezone.localdate(),
        ).count(),3)

    ai_pet = (
        ShopItem.objects
        .filter(category="pet", is_active=True)
        .exclude(image="")
        .order_by("id")
        .first()
    )

    # 沒有寵物時，使用預設圖片
    ai_avatar_url = static(
        ai_pet.image if ai_pet
        else "pages/images/avatars/default1.png"
    )

    return render(request,"pages/home.html",{
            "levels": levels,
            "levels_json": json.dumps(levels_by_id, ensure_ascii=False),
            "user_name": request.user.username if request.user.is_authenticated else "Guest",
            "user_points": user_points,
            "is_teacher": _teacher_required(request.user),
            "shop_items":shop_items,
            "shop_categories": ShopItem.CATEGORY_CHOICES,
            "shop_enabled": shop_enabled,
            "background_music_enabled": background_music_enabled,
            "owned_item_ids":owned_item_ids,
            "owned_items":owned_items,
            "profile":profile,
            "show_onboarding":request.session.pop("show_onboarding",False),
            "user_avatar_url": user_avatar_url,
            "background_url": background_url,
            "ai_chat_free_daily_limit": AI_CHAT_FREE_DAILY_LIMIT, #免費次數上限及剩餘次數
            "ai_chat_remaining_free": ai_chat_remaining_free,
            "announcements": announcements,
            "session_age": settings.SESSION_COOKIE_AGE, #登入逾時倒數用
            "day_complete" : day_complete,
            "day_goal_point" : Day_Goal_Point,
            "ai_avatar_url": ai_avatar_url,
        },)

def session_keepalive(request):
    #前端「重新計時」與執行程式時呼叫；SESSION_SAVE_EVERY_REQUEST 會在這次請求重設過期時間
    if request.method != "POST":
        return JsonResponse({"message": "Only POST requests are accepted."}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "登入已逾時，請重新登入。"}, status=401)
    return JsonResponse({"remaining": settings.SESSION_COOKIE_AGE})

class UsernameResetForm(forms.Form):
    username = forms.CharField(max_length=150)

class ResetForAllUsersForm(PasswordResetForm):
    # Django 預設會略過「沒有密碼」的帳號（Google 註冊／連結過的），這裡改成都寄
    def get_users(self, email):
        return User.objects.filter(email__iexact=email, is_active=True)
    
class EmailCheck(PasswordResetView):
    form_class = ResetForAllUsersForm
    template_name ="registration/password_reset.html"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            return redirect("password_reset_not_email")

        return super().form_valid(form)

def password_reset_not_email(request):
    return render(request, "registration/password_reset_not_email.html")


@login_required
def owned_emojis(request):
    items = (
        ShopItem.objects.filter(
            category="emoji",
            is_active=True,
            useritem__user=request.user,
        )
        .distinct()
        .order_by("name")
    )
    return JsonResponse({"emojis": [emoji_data(item) for item in items]})


def get_owned_emoji(user, emoji_id):
    if emoji_id in (None, ""):
        return None
    return (
        ShopItem.objects.filter(
            id=emoji_id,
            category="emoji",
            is_active=True,
            useritem__user=user,
        )
        .first()
    )


def emoji_data(item):
    if item is None:
        return None
    return {
        "id": item.id,
        "name": item.name,
        "image_url": static(item.image),
    }


def get_posts(request):
    level_id = request.GET.get("level_id", "")
    posts = (
        Post.objects.filter(level_id=level_id)
        .select_related("author", "emoji")
        .prefetch_related("likes", "replies__author", "replies__emoji")
    )
    data = []
    for post in posts:
        author_profile, _ = UserProfile.objects.get_or_create(user=post.author)
        data.append({
            "id": post.id,
            "author": post.author.username,
            "avatar_url":author_profile.get_avatar_url(),
            "content": post.content,
            "emoji": emoji_data(post.emoji),
            "created_at": post.created_at.strftime("%Y/%m/%d %H:%M"),
            "likes": post.likes.count(),
            "liked": request.user in post.likes.all() if request.user.is_authenticated else False,
            "replies": [
                {
                    "id": r.id,
                    "author": r.author.username,
                    "avatar_url": UserProfile.objects.get_or_create(user=r.author)[0].get_avatar_url(),
                    "content": r.content,
                    "emoji": emoji_data(r.emoji),
                    "created_at": r.created_at.strftime("%Y/%m/%d %H:%M"),
                }
                for r in post.replies.all()
            ]
        })
    return JsonResponse({"posts": data})

@csrf_exempt
@login_required
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    data = json.loads(request.body)
    level_id = data.get("level_id", "")
    content = data.get("content", "").strip()
    emoji_id = data.get("emoji_id")
    emoji = get_owned_emoji(request.user, emoji_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if emoji_id not in (None, "") and emoji is None:
        return JsonResponse({"error": "你尚未擁有這個表情"}, status=403)
    if not content and emoji is None:
        return JsonResponse({"error": "請輸入內容或選擇表情"}, status=400)
    post = Post.objects.create(
        author=request.user,
        level_id=level_id,
        content=content,
        emoji=emoji,
    )
    return JsonResponse({
        "id": post.id,
        "author": post.author.username,
        "avatar_url": profile.get_avatar_url(),
        "content": post.content,
        "emoji": emoji_data(post.emoji),
        "created_at": post.created_at.strftime("%Y/%m/%d %H:%M"),
        "likes": 0,
        "liked": False,
        "replies": []
    })

@login_required
def create_reply(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "找不到文章"}, status=404)
    data = json.loads(request.body)
    content = data.get("content", "").strip()
    emoji_id = data.get("emoji_id")
    emoji = get_owned_emoji(request.user, emoji_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if emoji_id not in (None, "") and emoji is None:
        return JsonResponse({"error": "你尚未擁有這個表情"}, status=403)
    if not content and emoji is None:
        return JsonResponse({"error": "請輸入回覆或選擇表情"}, status=400)
    reply = Reply.objects.create(
        post=post,
        author=request.user,
        content=content,
        emoji=emoji,
    )
    return JsonResponse({
        "id": reply.id,
        "author": reply.author.username,
        "avatar_url": profile.get_avatar_url(),
        "content": reply.content,
        "emoji": emoji_data(reply.emoji),
        "created_at": reply.created_at.strftime("%Y/%m/%d %H:%M"),
    })

@login_required
def unlock_level(request, level_id):
    if request.method != "POST":
        return JsonResponse({"error":"不允許"}, status=405)

    levels_by_id = get_levels_by_id()
    level_data = levels_by_id.get(level_id)
    if not level_data:
        return JsonResponse({"error":"找不到關卡"}, status=404)

    rule = level_data.get("unlock_rule")
    if not (isinstance(rule, dict) and rule.get("cost") is not None):
        return JsonResponse({"error":"此關卡不可用點數解鎖"}, status=400)

    if LevelUnlock.objects.filter(user=request.user, level=level_id).exists():
        return JsonResponse({"error":"已經解鎖過了"}, status=400)

    cost = rule.get("cost", 0)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.points < cost:
        return JsonResponse({"error":"點數不足"}, status=400)

    profile.points -= cost
    profile.save()
    LevelUnlock.objects.create(user=request.user, level=level_id)

    return JsonResponse({"message":"解鎖成功", "points": profile.points, "level": level_id})

@login_required
def levels_unlock_status(request):
    levels_by_id = get_levels_by_id()
    return JsonResponse(get_unlock_status(request.user, levels_by_id))

@login_required
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "找不到文章"}, status=404)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({"likes": post.likes.count(), "liked": liked})


@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(user=request.user)
    day_options = (7, 14, 30, 90)
    requested_days = request.GET.get("days", "30")
    days = int(requested_days) if requested_days in {str(value) for value in day_options} else 30
    chart_type = request.GET.get("chart", "submissions")
    if chart_type not in ("submissions", "ai"):
        chart_type = "submissions"
    taipei = ZoneInfo("Asia/Taipei")
    today = timezone.localdate() if chart_type == "ai" else timezone.localdate(timezone=taipei)
    start_date = today - timedelta(days=days - 1)
    start_at = datetime.combine(start_date, datetime.min.time(), tzinfo=taipei)
    end_at = datetime.combine(
        today + timedelta(days=1), datetime.min.time(), tzinfo=taipei
    )

    counts_by_day = {}
    ai_by_day = {}
    if chart_type == "ai":
        ai_by_day = dict(AiChatUsage.objects.filter(
            user=request.user, date__gte=start_date, date__lte=today
        ).values_list("date", "count"))
    else:
        daily_counts = (
            submissions.filter(submitted_at__gte=start_at, submitted_at__lt=end_at)
            .order_by()
            .annotate(day=TruncDate("submitted_at", tzinfo=taipei))
            .values("day")
            .annotate(
                attempts=Count("id"),
                solved=Count("level", filter=Q(passed=True), distinct=True),
            )
        )
        counts_by_day = {row["day"]: row for row in daily_counts}
    trend = []
    for index in range(days):
        day = start_date + timedelta(days=index)
        counts = counts_by_day.get(day, {})
        trend.append({
            "date": day.strftime("%Y/%m/%d"),
            "label": day.strftime("%m/%d"),
            "attempts": counts.get("attempts", 0),
            "solved": counts.get("solved", 0),
            "ai_count": ai_by_day.get(day, 0),
        })

    attempts = [row["attempts"] for row in trend]
    solved = [row["solved"] for row in trend]
    if chart_type == "ai":
        values = [row["ai_count"] for row in trend]
    else: 
        values = attempts
    total_count = sum(values)
    active_days = sum(count > 0 for count in values)
    #圖表的描述
    if chart_type == "ai":
        chart_details = {
            "title": f"近 {days} 天 AI 使用次數折線圖",
            "note": f"近日 AI 使用紀錄統計（{timezone.get_current_timezone_name()})",
            "summary": f"AI 使用次數：{total_count} 次　使用天數：{active_days} 天",
            "empty_message": f"近 {days} 天無 AI 使用紀錄。",
            "legend_label": "━ AI 使用次數",
            "legend_color": "#c4b5fd",
        }
    else:
        chart_details = {
            "title": f"近 {days} 天做題折線圖",
            "note": "一天內同一題目通過只算一次",
            "summary": f"提交數：{total_count}　使用天數：{active_days} 天",
            "empty_message": f"近 {days} 天無提交紀錄。",
            "legend_label": "━ 提交次數",
            "legend_color": "#7dd3fc",
        }
    #x軸
    x = list(range(days))
    #圖
    fig = Figure(figsize=(10, 3.8), dpi=140)
    #可以在背景畫圖
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    #背景顏色
    fig.patch.set_facecolor("#132b3d")
    ax.set_facecolor("#132b3d")
    ax.plot(x, values,"-o", color=chart_details["legend_color"], lw=2, ms=4)
    if chart_type == "submissions":
        ax.plot(x, solved,"--o" ,color="#34d399", lw=2, markersize=3,)
    #x軸刻度
    tick_positions = [round(index * (days - 1) / 6) for index in range(7)]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([trend[index]["label"] for index in tick_positions])
    #y軸範圍
    ax.set_ylim(0, max(4, max(values) * 1.2))
    #整數
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    #x軸範圍
    ax.set_xlim(-0.5, days - 0.5)
    #x軸y軸刻度&u刻度文字顏色
    ax.tick_params(colors="#cbd5e1")
    ax.grid(axis="y", color="#355064", alpha=0.7)
    ax.set_axisbelow(True)
    #邊框顏色
    for spine in ax.spines.values():spine.set_color("#355064")
    #x軸y軸文字
    ax.set_xlabel("日期", color="#cbd5e1", fontfamily="Microsoft JhengHei")
    if chart_type == "ai" :
        ax.set_ylabel("次數",color="#cbd5e1", fontfamily="Microsoft JhengHei",)
    else:
        ax.set_ylabel("題數",color="#cbd5e1", fontfamily="Microsoft JhengHei",)
    fig.tight_layout()
    #圖
    with BytesIO() as buffer:
        fig.savefig(buffer, format="png", facecolor=fig.get_facecolor())
        chart_image = base64.b64encode(buffer.getvalue()).decode("ascii")
    fig.clear()
    #切換圖表(題數&AI)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "days": days,
            "chart_type": chart_type,
            "chart_details": chart_details,
            "total_count": total_count,
            "chart_image": chart_image,
            "trend_start": start_date.strftime("%Y/%m/%d"),
            "trend_end": today.strftime("%Y/%m/%d"),
            "total_attempts": sum(attempts),
            "active_days": active_days,
        }, headers={"Cache-Control": "private, no-store"})

    return render(request, "pages/submissions.html", {
        "submissions": submissions,
        "chart_image": chart_image,
        "trend": trend,
        "days": days,
        "chart_type": chart_type,
        "chart_details": chart_details,
        "total_count": total_count,
        "day_options": day_options,
        "trend_start": start_date,
        "trend_end": today,
        "total_attempts": sum(attempts),
        "active_days": active_days,
    })

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["email","username","password1","password2"]
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("這個Email已經註冊過了，請直接登入，或使用忘記密碼。")
        return email        
    
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 設定裡有兩個驗證後端（帳密 + Google），剛註冊的使用者沒經過 authenticate()，要指定用哪一個
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session["show_onboarding"] = True
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def set_password(request):
    # Google 註冊的帳號沒有 CodeQuest 密碼，在這裡設一組，之後也能用「帳號或 Email + 密碼」登入
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = "/"

    # 已經有密碼的人不能用這頁改密碼，要改請走「忘記密碼」
    if request.user.has_usable_password():
        return redirect(next_url)

    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # 改了密碼 Django 會讓其他 session 失效，這行讓目前這個 session 保持登入
            update_session_auth_hash(request, form.user)
            return redirect(next_url)
    else:
        form = SetPasswordForm(request.user)

    return render(request, "registration/set_password.html", {"form": form, "next": next_url})

def _teacher_required(user):
    return (
        user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name="Teachers").exists()
        )
    )
@login_required
def profile_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "choose_default":
            chosen = request.POST.get("avatar_choice")
            if chosen in DEFAULT_AVATAR_IDS:
                profile.avatar_choice = chosen
                profile.save()
            return redirect("profile_page")

        elif action == "upload_custom":
            form = AvatarUploadForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.avatar_choice = "custom"
                profile.save()
            return redirect("profile_page")

        elif action == "choose_background":
            background_id = request.POST.get("background_id", "")

            if background_id == "":
                profile.selected_background = None
            elif background_id.isdigit():
                owned = UserItem.objects.filter(
                    user=request.user,
                    item_id=background_id,
                    item__category="background",
                ).select_related("item").first()

                if owned and owned.item.image:
                    profile.selected_background = owned.item

            profile.save(update_fields=["selected_background"])
            return redirect("profile_page")
    owned_backgrounds = [owned.item for owned in 
                         UserItem.objects.filter(user=request.user,item__category="background",).select_related("item")if owned.item.image]
    return render(request, "pages/profile.html", {
        "profile": profile,
        "default_avatars": DEFAULT_AVATAR_IDS,
        "owned_backgrounds": owned_backgrounds,
        
    })

class RoleLoginView(LoginView):
    template_name = "registration/login.html"
    # 登入後優先回到 next 指定的頁面，否則回首頁。
    def get_success_url(self):
        return self.get_redirect_url() or settings.LOGIN_REDIRECT_URL

def _student_files_dir():
    submissions_dir = Path(settings.BASE_DIR) / "submissions"
    submissions_dir.mkdir(exist_ok=True)
    return submissions_dir

def _safe_student_file(filename):
    submissions_dir = _student_files_dir().resolve()
    file_path = (submissions_dir / filename).resolve()
    if submissions_dir not in file_path.parents or file_path.suffix not in EDITABLE_STUDENT_FILE_TYPES:
        raise PermissionDenied
    return file_path

def _infer_level_from_filename(filename):
    parts = filename.split("_", 2)
    if len(parts) >= 2:
        return parts[1]
    return "unknown-level"

def _parent_level_for_topic(topic_id,levels_by_id):

    for level_id, chapter in levels_by_id.items():
            for topic in chapter.get("topics", []):
                if topic.get("id") == topic_id:
                    return level_id
                    
    return None


def _test_code_for_level(level):
    levels_by_id = get_levels_by_id()
    level_data = levels_by_id.get(level)
    if level_data:
        return level_data.get("test_code")

    for lvl in levels_by_id.values():
        for topic in lvl.get("topics", []):
            if topic.get("id") == level:
                return topic.get("test_code")

    return None

def _find_reference_file(level):
    references_dir = Path(settings.BASE_DIR) / "references"
    candidate_levels = [level]

    levels_by_id = get_levels_by_id()
    parent_level = _parent_level_for_topic(level,levels_by_id)
    if parent_level and parent_level not in candidate_levels:
        candidate_levels.append(parent_level)

    if not level.endswith("-1"):
        candidate_levels.append(f"{level}-1")

    for candidate_level in candidate_levels:
        ref_path = references_dir / f"{candidate_level}.pkl"
        if ref_path.exists():
            return ref_path, candidate_level
    return None, candidate_levels[-1]


def evaluate_student_file(file_path, level=None,test_code=None, reference_path=None):
    level = level or _infer_level_from_filename(file_path.name)
    if reference_path is None:
        ref_path, reference_level = _find_reference_file(level)
    else:
        ref_path, reference_level = Path(reference_path), level
    if file_path.suffix not in EVALUATABLE_STUDENT_FILE_TYPES:
        return {
            "filename": file_path.name,
            "level": level,
            "passed": None,
            "steps": None,
            "messages": "此檔案類型不能使用 PyBryt 評測。",
            "feedback": [],
        }

    if ref_path is None:
        return {
            "filename": file_path.name,
            "level": level,
            "passed": None,
            "steps": None,
            "messages": f"找不到 {level} 或 {reference_level} 的參考答案。",
            "feedback": [],
        }

    import nbformat
    nb = nbformat.read(str(file_path), as_version=4)
    
    if test_code:
        test_cell = nbformat.v4.new_code_cell(test_code)
        nb.cells.append(test_cell)
    
    #寫入暫存檔案給PyBryt執行
    import tempfile
    with tempfile.NamedTemporaryFile(
        suffix=".ipynb", 
        delete=False, 
        mode="w", 
        encoding="utf-8",
        dir=file_path.parent,
    ) as tmp:
        nbformat.write(nb, tmp)
        tmp_path = Path(tmp.name)

    try:
        reference = pybryt.ReferenceImplementation.load(str(ref_path))
        student_impl = pybryt.StudentImplementation(
                str(tmp_path),
                timeout=PYBRYT_EXECUTION_TIMEOUT_SECONDS,
                output=str(tmp_path).replace(".ipynb", "_executed.ipynb")
        )
        results = student_impl.check(reference)
    finally:
        tmp_path.unlink(missing_ok=True)  # 清除暫存檔
        tmp_path.with_name(tmp_path.stem + "_executed.ipynb").unlink(missing_ok=True)

    result_list = results if isinstance(results, list) else [results]
    first_result = result_list[0]

    feedback = []
    all_passed = True
    for result in result_list:
        if not result.correct:
            all_passed = False
        for ann_res in result.to_dict()["results"]:
            ann = ann_res["annotation"]
            satisfied = ann_res["satisfied"]
            feedback.append({
                "name": ann.get("name", "檢查點"),
                "passed": satisfied,
                "message": ann.get("success_message") if satisfied else ann.get("failure_message"),
            })

    return {
        "filename": file_path.name,
        "level": reference_level,
        "passed": all_passed,
        "steps": student_impl.footprint.num_steps,
        "messages": "\n".join(first_result.messages),
        "feedback": feedback,
    }
# 群組作業與教師參考檔轉檔
def _compile_assignment_reference(source, destination):
    """CLI worker used by manage.py; executes the teacher reference in a child process."""
    notebook = nbformat.read(source, as_version=4)
    reference = pybryt.ReferenceImplementation.compile(notebook, name="group-assignment")
    if not isinstance(reference, pybryt.ReferenceImplementation) or not reference.annotations:
        raise ValueError("參考 Notebook 必須包含一份含 pybryt.Value 等檢查點的參考答案。")
    reference.dump(destination)


def compile_notebook_reference(upload):
    storage = assignment_storage()
    Path(storage.location).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=storage.location) as folder:
        source = Path(folder) / "reference.ipynb"
        destination = Path(folder) / "reference.pkl"
        source.write_bytes(upload.read())
        upload.seek(0)
        try:
            result = subprocess.run(
                [sys.executable, str(Path(settings.BASE_DIR) / "manage.py"),
                 "compile-assignment-reference", str(source), str(destination)],
                cwd=settings.BASE_DIR, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=120,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError("參考 Notebook 轉檔超過 120 秒，請檢查是否有無窮迴圈或等待輸入。") from exc
        if result.returncode or not destination.exists():
            lines = (result.stderr or result.stdout).strip().splitlines()
            detail = lines[-1][:500] if lines else "未產生參考檔。"
            raise ValueError("參考 Notebook 轉檔失敗：" + detail)
        return destination.read_bytes()




def check_group_access(user, group):
    teacher = _teacher_required(user)
    if group.name == "Teachers" or (not teacher and not user.groups.filter(pk=group.pk).exists()):
        raise PermissionDenied
    return teacher


@login_required
def assignment_groups(request):
    teacher = _teacher_required(request.user)
    groups = Group.objects.exclude(name="Teachers")
    if not teacher:
        groups = groups.filter(user=request.user)
    return render(request, "teacher/files.html", {"teacher_page": "assignment_groups", "groups": groups.order_by("name"), "teacher": teacher})


@login_required
def group_assignments(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    teacher = check_group_access(request.user, group)
    form = GroupAssignmentForm()
    if request.method == "POST":
        if not teacher:
            raise PermissionDenied
        form = GroupAssignmentForm(request.POST, request.FILES)
        valid = form.is_valid()
        if valid:
            try:
                compiled = compile_notebook_reference(form.cleaned_data["reference_file"])
            except ValueError as exc:
                form.add_error("reference_file", str(exc))
                valid = False
        if valid:
            assignment = form.save(commit=False)
            assignment.group = group
            assignment.created_by = request.user
            try:
                assignment.compiled_reference.save("reference.pkl", ContentFile(compiled), save=False)
                assignment.save()
            except Exception:
                for field in [assignment.prompt_file, assignment.reference_file, assignment.compiled_reference]:
                    if field and getattr(field, "_committed", False):
                        field.delete(save=False)
                raise
            messages.success(request, "作業已建立，群組成員現在可以繳交作業。")
            return redirect("group_assignment_detail", assignment_id=assignment.pk)
    return render(request, "teacher/files.html", {
        "teacher_page": "group_assignments",
        "group": group, "teacher": teacher, "form": form, "assignments": group.assignments.all(),
    })


def grade_submission(submission):
    try:
        result = evaluate_student_file(
            Path(submission.notebook.path), level=f"assignment-{submission.assignment_id}",
            test_code=submission.assignment.test_code,
            reference_path=submission.assignment.compiled_reference.path,
        )
    except Exception as exc:
        result = {"passed": None, "messages": f"批改未完成，可請教師重新批改。原因：{str(exc)[:500]}", "feedback": []}
    submission.result = result
    submission.save(update_fields=["result"])


@login_required
def group_assignment_detail(request, assignment_id):
    assignment = get_object_or_404(GroupAssignment.objects.select_related("group"), pk=assignment_id)
    teacher = check_group_access(request.user, assignment.group)
    form = AssignmentSubmissionForm(group=assignment.group, teacher=teacher)
    if request.method == "POST":
        if request.POST.get("action") == "regrade":
            if not teacher:
                raise PermissionDenied
            submission_id = request.POST.get("submission", "")
            if not submission_id.isdigit():
                raise Http404
            submission = get_object_or_404(assignment.submissions, pk=submission_id)
            grade_submission(submission)
            messages.success(request, "已重新批改，請查看下方結果。")
            return redirect("group_assignment_detail", assignment_id=assignment.pk)
        form = AssignmentSubmissionForm(request.POST, request.FILES, group=assignment.group, teacher=teacher)
        if form.is_valid():
            submission = AssignmentSubmission.objects.create(
                assignment=assignment, uploaded_by=request.user,
                student=form.cleaned_data["student"] if teacher else request.user,
                notebook=form.cleaned_data["notebook"],
            )
            grade_submission(submission)
            messages.success(request, "作業已儲存，請查看下方批改結果。")
            return redirect("group_assignment_detail", assignment_id=assignment.pk)
    submissions = assignment.submissions.select_related("student", "uploaded_by")
    if not teacher:
        submissions = submissions.filter(student=request.user)
    return render(request, "teacher/files.html", {
        "teacher_page": "assignment_detail",
        "assignment": assignment, "teacher": teacher, "form": form, "submissions": submissions,
    })


@login_required
def assignment_download(request, assignment_id, kind):
    assignment = get_object_or_404(GroupAssignment.objects.select_related("group"), pk=assignment_id)
    teacher = check_group_access(request.user, assignment.group)
    if kind == "prompt":
        field, filename = assignment.prompt_file, f"題目-{assignment.pk}"
    elif kind == "reference" and teacher:
        field, filename = assignment.reference_file, f"參考檔-{assignment.pk}"
    else:
        raise PermissionDenied
    if not field:
        raise Http404
    return FileResponse(field.open("rb"), as_attachment=True, filename=filename + Path(field.name).suffix)


@login_required
def assignment_submission_download(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission.objects.select_related("assignment__group"), pk=submission_id)
    teacher = check_group_access(request.user, submission.assignment.group)
    if not teacher and submission.student_id != request.user.pk:
        raise PermissionDenied
    return FileResponse(submission.notebook.open("rb"), as_attachment=True, filename=f"作業-{submission.pk}.ipynb")


@login_required
def assignment_reference_example(request):
    if not _teacher_required(request.user):
        raise PermissionDenied
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell("# 教師參考答案\n後台會執行此 Notebook 並產生 PyBryt 參考檔。學生 Notebook 應包含相同測資的呼叫，才能比對執行結果。"),
        nbformat.v4.new_code_cell("import pybryt\n\ndef value(x, y):\n    return x * y if x > 0 and y > 0 else 'ERROR'"),
        nbformat.v4.new_code_cell("result1 = value(26, 6)\nresult2 = value(5, 0)"),
        nbformat.v4.new_code_cell("pybryt.Value(result1, name='一般乘法', success_message='乘法正確', failure_message='請檢查 value(26, 6)')\npybryt.Value(result2, name='零值處理', success_message='零值處理正確', failure_message='請檢查零值處理')"),
    ])
    response = HttpResponse(nbformat.writes(notebook), content_type="application/x-ipynb+json")
    response["Content-Disposition"] = 'attachment; filename="reference-example.ipynb"'
    return response


@login_required
def teacher_groups(request):
    if not _teacher_required(request.user):
        raise PermissionDenied

    groups = Group.objects.exclude(name="Teachers").order_by("name")
    selected_id = request.POST.get("group") if request.method == "POST" else request.GET.get("group")
    selected = get_object_or_404(groups, pk=selected_id) if str(selected_id or "").isdigit() else None
    group_form = TeacherGroupForm()
    add_form = TeacherGroupMembersForm(group=selected, prefix="add") if selected else None
    remove_form = TeacherGroupMembersForm(group=selected, removing=True, prefix="remove") if selected else None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            group_form = TeacherGroupForm(request.POST)
            if group_form.is_valid():
                selected = group_form.save()
                messages.success(request, "群組已建立，可以開始加入使用者。")
                return redirect(f"{reverse('teacher_groups')}?group={selected.pk}")
        elif action in {"add", "remove"} and selected:
            form = TeacherGroupMembersForm(
                request.POST, group=selected, removing=action == "remove", prefix=action,
            )
            if form.is_valid():
                users = list(form.cleaned_data["users"])
                if action == "add":
                    selected.user_set.add(*users)
                else:
                    selected.user_set.remove(*users)
                messages.success(request, f"已{'加入' if action == 'add' else '移除'} {len(users)} 位使用者。")
                return redirect(f"{reverse('teacher_groups')}?group={selected.pk}")
            if action == "add":
                add_form = form
            else:
                remove_form = form
        else:
            raise PermissionDenied("請選擇有效的群組與操作。")

    return render(request, "teacher/files.html", {
        "teacher_page": "groups",
        "groups": groups.annotate(member_count=Count("user")),
        "selected": selected, "group_form": group_form,
        "add_form": add_form, "remove_form": remove_form,
    })


#老師查看檔案畫面
@login_required
def teacher_files(request):
    if not _teacher_required(request.user):
        raise PermissionDenied

    groups = list(Group.objects.exclude(name="Teachers").order_by("name"))
    selected_group = request.GET.get("group", "").strip()
    selected_user = request.GET.get("user", "").strip()
    users_query = User.objects.order_by("username")
    submissions = Submission.objects.all()

    if selected_group:
        if selected_group not in {str(group.pk) for group in groups}:
            raise PermissionDenied("找不到可篩選的群組")
        users_query = users_query.filter(groups__id=selected_group).distinct()
        submissions = submissions.filter(user__groups__id=selected_group)

    users = list(users_query)
    if selected_user:
        if selected_user not in {str(user.pk) for user in users}:
            raise PermissionDenied("找不到該使用者")
        submissions = submissions.filter(user_id=selected_user)

    filenames = None
    if selected_group or selected_user:
        filenames = set(submissions.values_list("filename", flat=True))

    submissions_dir = _student_files_dir()

    files = [
        {
            "name": path.name,
            "size": path.stat().st_size,
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime),
            "can_review": path.suffix in EVALUATABLE_STUDENT_FILE_TYPES,
        }
        for path in submissions_dir.iterdir()
        if path.is_file() and path.suffix in EDITABLE_STUDENT_FILE_TYPES
        and (filenames is None or path.name in filenames)
    ]
    files.sort(key=lambda item: item["modified_at"], reverse=True)
    return render(request, "teacher/files.html", {
        "teacher_page": "files",
        "files": files,
        "review_results": [],
        "groups": groups,
        "users": users,
        "selected_group": selected_group,
        "selected_user": selected_user,
    })
#老師審查、評測檔案
@login_required
def teacher_review_one_file(request, filename):
    if not _teacher_required(request.user):
        raise PermissionDenied

    file_path = _safe_student_file(filename)
    if not file_path.exists() or not file_path.is_file():
        raise PermissionDenied

    try:
        level = _infer_level_from_filename(file_path.name)
        result = evaluate_student_file(file_path, level, _test_code_for_level(level))
    except Exception as e:
        result = {
            "filename": file_path.name,
            "level": _infer_level_from_filename(file_path.name),
            "passed": False,
            "steps": None,
            "messages": f"評測錯誤：{str(e)}",
            "feedback": [],
        }

    return JsonResponse(result)

@login_required
def teacher_file_edit(request, filename):
    if not _teacher_required(request.user):
        raise PermissionDenied

    file_path = _safe_student_file(filename)
    if not file_path.exists() or not file_path.is_file():
        raise PermissionDenied

    message = ""
    review_result = None
    if request.method == "POST":
        try:
            level = _infer_level_from_filename(file_path.name)
            review_result = evaluate_student_file(file_path, level, _test_code_for_level(level))
            message = "已完成 PyBryt 評測。"
        except Exception as e:
            review_result = {
                "filename": file_path.name,
                "level": _infer_level_from_filename(file_path.name),
                "passed": False,
                "steps": None,
                "messages": f"評測錯誤：{str(e)}",
                "feedback": [],
            }
            message = "PyBryt 評測失敗。"

    content = file_path.read_text(encoding="utf-8")
    return render(
        request,
        "teacher/file_edit.html",
        {
            "filename": file_path.name,
            "content": content,
            "message": message,
            "review_result": review_result,
        },
    )

#商店購買
@login_required
def shop(request,item_id):
    if not getattr(settings, "SHOP_ENABLED", False):
        return JsonResponse({"error":"商店目前暫停開放"},status=503)
    if request.method != "POST":
        return JsonResponse({"error":"不允許"},status=405)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    try:
        item = ShopItem.objects.get(id=item_id,is_active=True)
    except ShopItem.DoesNotExist:
        return JsonResponse({"error":"找不到商品"},status=404)
    if UserItem.objects.filter(user=request.user,item=item).exists():
        return JsonResponse({"error":"你已經購買這件物品"},status=400)
    if profile.points < item.price:
        return JsonResponse({"error":"你沒有可以支付這件物品的費用"},status=400)
    profile.points -=item.price
    profile.save()

    UserItem.objects.create(user=request.user,item=item)

    return JsonResponse({
        "message":"購買成功",
        "points":profile.points,
        "item":{
            "id":item.id,
            "name":item.name,
            "price":item.price,
        }
    })



def _fixed_ai_code(level, topic):
    """取得本題固定的 AI 程式碼；第一次有人問這題時才產生並存起來，所有學生共用同一段。"""
    saved = AiTopicCode.objects.filter(topic_id=topic["id"]).first()
    if saved:
        return saved.code

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=16000,
        system=build_ai_code_prompt(level, topic),
        # 要在心裡逐一驗證埋的錯誤，思考預算給多一點；每題只會跑一次
        thinking={"type": "enabled", "budget_tokens": 4096},
        messages=[{"role": "user", "content": "請寫出本題的程式碼。"}],
    )
    code = clean_ai_reply("".join(
        block.text for block in response.content if block.type == "text"
    ))
    if not code:
        return None
    # 兩個人同時第一次問同一題時，以先存進去的那段為準
    saved, _ = AiTopicCode.objects.get_or_create(topic_id=topic["id"], defaults={"code": code})
    return saved.code


@login_required
def ai_chat(request):
    if request.method =="POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            if not user_message:
                return JsonResponse({"error":"輸入內容不能為空"},status=400)

            today = timezone.localdate()
            usage, _ = AiChatUsage.objects.get_or_create(user=request.user, date=today)
            profile, _ = UserProfile.objects.get_or_create(user=request.user)

            uses_free_chance = usage.count < AI_CHAT_FREE_DAILY_LIMIT
            if not uses_free_chance and profile.points < AI_CHAT_POINT_COST:
                return JsonResponse(
                    {"error": f"今日免費次數已用完，且點數不足（需要 {AI_CHAT_POINT_COST} 點）。"},
                    status=402,
                )

            # 依目前關卡與題目決定 AI 協助程度；關卡資料一律由後端查，不採用前端傳來的難度
            levels_by_id = get_levels_by_id()
            level = levels_by_id.get(data.get("level_id") or "")
            topic = None
            topic_id = data.get("topic_id") or ""
            parent_level_id = _parent_level_for_topic(topic_id, levels_by_id) if topic_id else None
            if parent_level_id:
                level = levels_by_id[parent_level_id]
                topic = next(t for t in level["topics"] if t.get("id") == topic_id)
            try:
                fixed_code = None
                if needs_fixed_code(level, topic):
                    fixed_code = _fixed_ai_code(level, topic)
                    if not fixed_code:
                        return JsonResponse({"error": "AI 這次沒有產生回答，請再問一次（不會扣次數）。"}, status=502)
                system_prompt, help_level = build_ai_system_prompt(level, topic, fixed_code)
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    # budget_tokens 只是建議值，思考可能超過；max_tokens 要留足空間，否則回答會被切掉或變成空的
                    max_tokens=16000,
                    system=system_prompt,
                    thinking={"type": "enabled", "budget_tokens": 1024},
                    messages=[{"role": "user", "content": user_message}],
                )
            except Exception as model_err:
                err_msg = str(model_err)
                if "overloaded" in err_msg.lower() or "529" in err_msg or "503" in err_msg:
                    return JsonResponse({"error":"模型忙碌中，請稍後再試。"},status=503)
                raise

            reply_text = clean_ai_reply("".join(
                block.text for block in response.content if block.type == "text"
            ))
            if fixed_code:
                reply_text = reply_text.replace(FIXED_CODE_PLACEHOLDER, fixed_code)
            # 沒有產生回答時直接回錯誤，不扣免費次數和點數
            if not reply_text:
                return JsonResponse({"error": "AI 這次沒有產生回答，請再問一次（不會扣次數）。"}, status=502)

            usage.count += 1
            usage.save()
            if not uses_free_chance:
                profile.points -= AI_CHAT_POINT_COST
                profile.save()

            remaining_free = max(AI_CHAT_FREE_DAILY_LIMIT - usage.count, 0)
            return JsonResponse({
                "reply": reply_text,
                "remaining_free_uses": remaining_free,
                "points": profile.points,
                "help_level": help_level,
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"error":"無效的 JSON 格式"},status=400)
        
        except anthropic.AuthenticationError:
            return JsonResponse({"error":"Claude API 驗證失敗，請檢查 API Key。"},status=500)
        except anthropic.APIError:
            return JsonResponse({"error":"Claude API 暫時無法使用，請稍後再試。"},status=502)
            
    today = timezone.localdate()
    usage, _ = AiChatUsage.objects.get_or_create(user=request.user, date=today)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    remaining_free = max(AI_CHAT_FREE_DAILY_LIMIT - usage.count, 0)
    return render(request, 'ai/ai_chat.html', {
        "remaining_free_uses": remaining_free,
        "points": profile.points,
        "free_daily_limit": AI_CHAT_FREE_DAILY_LIMIT,
    })
    
@csrf_exempt
def submit_solution(request):
    if request.method != "POST":
        return JsonResponse({"message": "Only POST requests are accepted."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"message": "請先登入才能提交關卡。"}, status=401)

    raw_level = request.POST.get("level", "unknown-level").replace("/", "-").replace("\\", "-")
    level = raw_level

    player = request.POST.get("player", "player").replace("/", "-").replace("\\", "-")
    notebook_json = request.POST.get("notebook", "").strip()

    levels_by_id = get_levels_by_id()
    parent_level_id = _parent_level_for_topic(level, levels_by_id) or level

    unlock_status = get_unlock_status(request.user, levels_by_id)
    level_unlock_info = unlock_status.get(parent_level_id)
    if level_unlock_info and not level_unlock_info["unlocked"]:
        return JsonResponse({"message": "此關卡尚未解鎖，無法提交。"}, status=403)
    
    if not notebook_json:
        return JsonResponse({"message": "請先輸入要提交的程式碼。"}, status=400)

    try:
        notebook_data = json.loads(notebook_json)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Notebook 格式錯誤。"}, status=400)

    submitted_at = datetime.now().strftime("%Y%m%d-%H%M%S")
    submissions_dir = Path(settings.BASE_DIR) / "submissions"
    submissions_dir.mkdir(exist_ok=True)
    filename = f"{submitted_at}_{level}_{player}.ipynb"
    file_path = submissions_dir / filename
    file_path.write_text(
        json.dumps(notebook_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    try:
        levels_by_id = get_levels_by_id()
        test_code = None
        level_data = levels_by_id.get(level)
        
        if level_data:
            test_code = level_data.get("test_code")
        else:
            for lvl in levels_by_id.values():
                for topic in lvl.get("topics", []):
                    if topic.get("id") == level:
                        test_code = topic.get("test_code")
                        break
        
        review_result = evaluate_student_file(file_path, level, test_code)
        all_passed = review_result["passed"]
        reward_points = 0
        total_points = None
        daily_point = 0
        day_complete = None

        if request.user.is_authenticated:
            #更改資料，有問題就回復紀錄
            with transaction.atomic():
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                today = timezone.localdate()
                already_passed = Submission.objects.filter(
                    user=request.user,
                    level=level,
                    passed=True,
                ).exists()

                if all_passed:
                    if not already_passed:
                        reward_points = 10

                    # 通過測試才計入每日任務，同一題每天只建立一次紀錄。
                    _, goal_created = DailyGoal.objects.get_or_create(
                        user=request.user,
                        date=today,
                        level=level,
                    )
                    if goal_created:
                        final_count = DailyGoal.objects.filter(
                            user=request.user,
                            date=today,
                        ).count()
                        daily_point = Day_Goal_Point.get(final_count, 0)

                add_point = reward_points + daily_point
                if add_point:
                    UserProfile.objects.filter(pk=profile.pk).update(points=F("points") + add_point)
                profile.refresh_from_db(fields=["points"])
                total_points = profile.points

                Submission.objects.create(
                    user=request.user,
                    level=level,
                    filename=filename,
                    passed=all_passed,
                )

                #顯示使用者今日完成題數最多三筆
                day_complete = min(DailyGoal.objects.filter(
                    user=request.user,
                    date=today,
                ).count(), 3)

        return JsonResponse({
            "message": "全部通過！" if all_passed else "部分未通過",
            "filename": filename,
            "passed": all_passed,
            "reward_points": reward_points,
            "total_points": total_points,
            "steps": review_result["steps"],
            "messages": review_result["messages"],
            "feedback": review_result["feedback"],
            "daily_point": daily_point,
            "day_complete": day_complete,
        })

    except Exception as e:
        return JsonResponse({
            "message": f"已儲存 {filename}，鑑定錯誤：{str(e)}",
            "filename": filename,
            "passed": False,
            "feedback": []
        })



