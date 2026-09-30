from django.db import models
from django.contrib.auth.models import User
# Create your models here

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=100)
    filename = models.CharField(max_length=200)
    passed = models.BooleanField(null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username}-{self.level}-{self.submitted_at}"
    
DEFAULT_AVATAR_CHOICES = [
    ("default1", "預設頭像 1"),
    ("default2", "預設頭像 2"),
    ("default3", "預設頭像 3"),
    ("default4", "預設頭像 4"),
    ("custom", "自訂頭像"),
]
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    avatar_choice = models.CharField(max_length=20, choices=DEFAULT_AVATAR_CHOICES, default="default1")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    selected_background = models.ForeignKey("ShopItem",null=True,blank=True,on_delete=models.SET_NULL,)

    def get_avatar_url(self):
        if self.avatar_choice == "custom" and self.avatar:
            return self.avatar.url
        return f"/static/pages/images/avatars/{self.avatar_choice}.png"

    def __str__(self):
        return f"{self.user.username} 的個人檔案"
    def __str__(self):
        return f"{self.user.username} - {self.points} points"
        
class ShopItem(models.Model):
    CATEGORY_CHOICES = [
        ("general", "一般"),
        ("avatar", "角色"),
        ("pet", "寵物"),
        ("emoji", "表情"),
        ("background", "背景"),
        ("badge", "徽章"),
        ("powerup", "道具"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="general")
    price = models.IntegerField(default=0)
    image = models.CharField(max_length=200,blank=True)
    is_active = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} - {self.price} points"
class UserItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem,on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=("user","item")
    def __str__(self):
        return f"{self.user.username} 擁有 {self.item.name}"

    
class Post(models.Model):
    level_id = models.CharField(max_length=100)  # e.g. chapter-1-level-1-1
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    emoji = models.ForeignKey(
        ShopItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emoji_posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} - {self.level_id}"

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    emoji = models.ForeignKey(
        ShopItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emoji_replies",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        
class LevelUnlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=100)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "level")

    def __str__(self):
        return f"{self.user.username} 解鎖 {self.level}"

class AiChatUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.count} 次"

class Announcement(models.Model):
    title = models.CharField("公告標題", max_length=100)
    content = models.TextField("公告內容")
    is_active = models.BooleanField("顯示公告", default=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "公告"
        verbose_name_plural = "公告"

    def __str__(self):
        return self.title

class DailyGoal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    level = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user","date","level"],
                name = "user-cannot-repeatlevel"
            )
        ]
