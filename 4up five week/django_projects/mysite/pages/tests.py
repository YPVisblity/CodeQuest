from pathlib import Path
from tempfile import TemporaryDirectory
import json

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings

from .models import Post, Reply, ShopItem, UserItem
from .unlocking import is_level_cleared
from .views import _find_reference_file, _parent_level_for_topic


class StoryOnlyLevelTests(SimpleTestCase):
    def test_story_only_level_is_cleared_without_a_submission(self):
        self.assertTrue(
            is_level_cleared(
                "chapter-2-level-0",
                {"story_only": True, "topics": []},
                passed_ids=set(),
            )
        )

    def test_regular_empty_level_still_requires_a_submission(self):
        self.assertFalse(
            is_level_cleared(
                "chapter-2-level-1",
                {"topics": []},
                passed_ids=set(),
            )
        )


class ReferenceFileLookupTests(SimpleTestCase):
    def test_parent_level_for_topic_supports_old_submission_names(self):
        levels_by_id = {
            "chapter-1-level-1": {
                "topics": [{"id": "chapter-1-level-1-1"}],
            },
        }
        self.assertEqual(
            _parent_level_for_topic("chapter-1-level-1-1", levels_by_id),
            "chapter-1-level-1",
        )

    def test_find_reference_file_resolves_matching_parent_level_file(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            references_dir = base_dir / "references"
            references_dir.mkdir()
            ref_file = references_dir / "chapter-1-level-1.pkl"
            ref_file.write_bytes(b"reference")

            with override_settings(BASE_DIR=base_dir):
                found_path, found_level = _find_reference_file("chapter-1-level-1")

        self.assertEqual(found_path, ref_file)
        self.assertEqual(found_level, "chapter-1-level-1")

    def test_find_reference_file_resolves_old_topic_level_to_parent_file(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            references_dir = base_dir / "references"
            references_dir.mkdir()
            ref_file = references_dir / "chapter-1-level-1.pkl"
            ref_file.write_bytes(b"reference")

            with override_settings(BASE_DIR=base_dir):
                found_path, found_level = _find_reference_file("chapter-1-level-1-1")

        self.assertEqual(found_path, ref_file)
        self.assertEqual(found_level, "chapter-1-level-1")

    def test_find_reference_file_keeps_old_fallback_for_non_level_one_names(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            references_dir = base_dir / "references"
            references_dir.mkdir()
            ref_file = references_dir / "chapter-1-level-2-1.pkl"
            ref_file.write_bytes(b"reference")

            with override_settings(BASE_DIR=base_dir):
                found_path, found_level = _find_reference_file("chapter-1-level-2")

        self.assertEqual(found_path, ref_file)
        self.assertEqual(found_level, "chapter-1-level-2-1")


class CommentEmojiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="test-pass")
        self.other_user = User.objects.create_user(username="other", password="test-pass")
        self.emoji = ShopItem.objects.create(
            name="開心",
            category="emoji",
            image="pages/images/happy.png",
            is_active=True,
        )
        UserItem.objects.create(user=self.user, item=self.emoji)
        self.client.force_login(self.user)

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_owned_emojis_only_returns_purchased_active_emojis(self):
        response = self.client.get("/api/emojis/owned/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["emojis"], [{
            "id": self.emoji.id,
            "name": "開心",
            "image_url": "/static/pages/images/happy.png",
        }])

    def test_create_post_can_use_owned_emoji_without_text(self):
        response = self.post_json("/api/posts/create/", {
            "level_id": "chapter-1-level-1-1",
            "content": "",
            "emoji_id": self.emoji.id,
        })

        self.assertEqual(response.status_code, 200)
        post = Post.objects.get()
        self.assertEqual(post.emoji, self.emoji)
        self.assertEqual(response.json()["emoji"]["id"], self.emoji.id)

    def test_create_post_rejects_unowned_emoji(self):
        unowned = ShopItem.objects.create(
            name="哭哭",
            category="emoji",
            image="pages/images/cry.png",
            is_active=True,
        )

        response = self.post_json("/api/posts/create/", {
            "level_id": "chapter-1-level-1-1",
            "content": "偽造表情",
            "emoji_id": unowned.id,
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Post.objects.exists())

    def test_reply_emoji_is_returned_by_posts_api(self):
        post = Post.objects.create(
            author=self.other_user,
            level_id="chapter-1-level-1-1",
            content="原留言",
        )
        response = self.post_json(f"/api/posts/{post.id}/reply/", {
            "content": "",
            "emoji_id": self.emoji.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reply.objects.get().emoji, self.emoji)
        posts = self.client.get("/api/posts/", {
            "level_id": "chapter-1-level-1-1",
        }).json()["posts"]
        self.assertEqual(posts[0]["replies"][0]["emoji"]["id"], self.emoji.id)
