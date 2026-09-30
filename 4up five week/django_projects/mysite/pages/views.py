import sys
import asyncio
import json
from datetime import datetime
from django.utils import timezone
from pathlib import Path
import anthropic
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from .models import Submission,Post,Reply,UserProfile,ShopItem,UserItem,LevelUnlock,AiChatUsage,Announcement,DailyGoal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView,PasswordResetView
from django.views.generic.edit import FormView
from django.utils.crypto import get_random_string
from django import forms
from django.contrib.auth.models import User
from django.contrib import messages
from django.templatetags.static import static
from .level_loader import load_levels, get_levels_by_id
from pathlib import Path
from django.urls import reverse,reverse_lazy
from django.db import transaction
from django.db.models import F
from .unlocking import get_unlock_status,get_chapter_number
from .forms import AvatarUploadForm

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
PYBRYT_EXECUTION_TIMEOUT_SECONDS = 90


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

class EmailCheck(FormView):
    template_name ="registration/password_reset.html"
    form_class = UsernameResetForm
    success_url = reverse_lazy("password_reset")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        user = User.objects.filter(username=username).first()
        if user is None:
            messages.error(self.request, "該用戶不存在。")
            return self.form_invalid(form)

        #密碼以雜湊儲存無法取回原密碼，改為產生新密碼並顯示
        new_password = get_random_string(8)
        user.set_password(new_password)
        user.save()
        messages.success(self.request, f"帳號 {username} 的密碼為：{new_password}")
        return super().form_valid(form)

# class EmailCheck(PasswordResetView):
#     template_name ="registration/password_reset.html"
#     success_url = reverse_lazy("password_reset_done")
#
#     def form_valid(self, form):
#         username = form.cleaned_data["username"]
#         if not User.objects.filter(username=username).exists():
#             return JsonResponse({"message": "該用戶不存在。"}, status=400)
#
#         return JsonResponse({"message": "密碼重設郵件已發送。"}, status=200)
#         # return super().form_valid(form)

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
    return render(request, "pages/submissions.html", {
        "submissions": submissions
    })

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["email","username","password1","password2"]
        
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session["show_onboarding"] = True
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

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


def evaluate_student_file(file_path, level=None,test_code=None):
    level = level or _infer_level_from_filename(file_path.name)
    ref_path, reference_level = _find_reference_file(level)
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
        encoding="utf-8"
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
#老師查看檔案畫面
@login_required
def teacher_files(request):
    if not _teacher_required(request.user):
        raise PermissionDenied

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
    ]
    files.sort(key=lambda item: item["modified_at"], reverse=True)
    return render(request, "teacher/files.html", {
        "files": files,
        "review_results": [],
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

            system_prompt = """
            你是一個Python程式教學AI助手。請遵守以下規則:

            領域限制:
            只回答與Python相關的問題。若詢問非Python領域議題，一律回答:這不符合我們的關卡內容。

            程式碼格式規範:
            1. 絕對不要使用Markdown的反引號（```）或HTML標籤（<pre>）。
            2. 請直接輸出純文字程式碼，但「絕對要保留 Python 的標準空格縮排與換行」，讓使用者可以直接複製。

            指定關卡範本輸出:
            若詢問 Lv1-1-1（題目：蘋果價格與數量計算）：
            def value(x, y):
                if x == 0 or y == 0:
                    return "EOFError"
                else:
                    return x * y
            並且說明為何要這麼做。

            若詢問 Lv1-2-1（題目：BMI 測量）：
            def basic(h, w):
                bmi = w / (h * h)
                if bmi < 18.5:
                    return "過輕"
                elif bmi > 24:
                    return "過重"
                else:
                    return "正常"
            並且說明為何要這麼做。

            若詢問 Lv1-3-1：
            使用一個 for 迴圈來表示 row 的值再在裡面套個 for 迴圈表示 col 的值，像是這樣：
            def matrix_add(A, B):
                for i in range(row):
                    new_row = []
                    for j in range(col):
                        pass

            若詢問 Lv2-1-1：
            def sequence(a, d, n):
                result = []
                for i in range(n):
                    term = a + i * d
                    result.append(term)
                return result
            """
            try:
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=2048,
                    system=system_prompt,
                    thinking={"type": "enabled", "budget_tokens": 1024},
                    messages=[{"role": "user", "content": user_message}],
                )
            except Exception as model_err:
                err_msg = str(model_err)
                if "overloaded" in err_msg.lower() or "529" in err_msg or "503" in err_msg:
                    return JsonResponse({"error":"模型忙碌中，請稍後再試。"},status=503)
                raise

            reply_text = "".join(
                block.text for block in response.content if block.type == "text"
            )

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




