import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0008_userprofile_avatar_userprofile_avatar_choice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="reply",
            name="content",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="post",
            name="emoji",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="emoji_posts",
                to="pages.shopitem",
            ),
        ),
        migrations.AddField(
            model_name="reply",
            name="emoji",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="emoji_replies",
                to="pages.shopitem",
            ),
        ),
    ]
