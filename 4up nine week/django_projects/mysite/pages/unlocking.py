import re
from .models import Submission, LevelUnlock

CHAPTER_RE = re.compile(r"^chapter-(\d+)-level-(\d+)$")


def get_chapter_number(level_id):
    m = CHAPTER_RE.match(level_id)
    return int(m.group(1)) if m else None


def _level_topic_ids(level_data):
    return [t["id"] for t in (level_data.get("topics") or []) if "id" in t]


def is_level_cleared(level_id, level_data, passed_ids):
    # 純劇情關卡沒有題目可提交，不應阻擋後續章節解鎖。
    if level_data.get("story_only") is True:
        return True

    topic_ids = _level_topic_ids(level_data)
    if topic_ids:
        return all(tid in passed_ids for tid in topic_ids)
    return level_id in passed_ids


def get_unlock_status(user, levels_by_id):
    """
    回傳 { level_id: {"unlocked": bool, "reason": str, "cost": int|None} }
    """
    if not user or not user.is_authenticated:
        return {lid: {"unlocked": False, "reason": "login_required", "cost": None}
                for lid in levels_by_id}

    if user.is_superuser:
        return {
            lid: {
                "unlocked": True,
                "reason": "superuser",
                "cost": None,
                "test_level": None,
                "prev_chapter_gate": False,
            }
            for lid in levels_by_id
        }

    passed_ids = set(
        Submission.objects.filter(user=user, passed=True).values_list("level", flat=True)
    )
    manually_unlocked = set(
        LevelUnlock.objects.filter(user=user).values_list("level", flat=True)
    )

    # 依章節分組，計算每一章是否全破
    chapters = {}
    for lid in levels_by_id:
        c = get_chapter_number(lid)
        chapters.setdefault(c, []).append(lid)

    chapter_cleared = {
        c: all(is_level_cleared(lid, levels_by_id[lid], passed_ids) for lid in lids)
        for c, lids in chapters.items()
    }

    status = {}
    for lid, ldata in levels_by_id.items():
        c = get_chapter_number(lid)
        rule = ldata.get("unlock_rule")

        # 這一關本身可能開放的解鎖管道，不管最後鎖不鎖，都先算出來給前端顯示選項用
        test_level_id = rule.get("test_level") if isinstance(rule, dict) else None
        cost = rule.get("cost") if isinstance(rule, dict) else None
        prev_chapter_gate = bool(c) and c > 1

        def build(unlocked, reason, extra_cost=None):
            return {
                "unlocked": unlocked,
                "reason": reason,
                "cost": extra_cost,
                "test_level": test_level_id,
                "prev_chapter_gate": prev_chapter_gate,
            }

        if lid in manually_unlocked:
            status[lid] = build(True, "purchased")
            continue

        if rule == "free" or c == 1:
            status[lid] = build(True, "free")
            continue

        # 方法一：前一章是否已經全破 -> 自動解鎖
        prev_cleared = chapter_cleared.get(c - 1, False) if c else False
        if prev_cleared:
            status[lid] = build(True, "prev_chapter_cleared")
            continue

        # 方法二：是否通過指定的「額外題目」(test_level) -> 自動解鎖
        if test_level_id:
            test_level_data = levels_by_id.get(test_level_id)
            if test_level_data and is_level_cleared(test_level_id, test_level_data, passed_ids):
                status[lid] = build(True, "test_level_cleared")
                continue

        # 方法三：前一章還沒全破、額外題目也還沒過時，看這關是否允許用點數提前解鎖
        if cost is not None:
            status[lid] = build(False, "points", extra_cost=cost)
            continue

        status[lid] = build(False, "prev_chapter_incomplete")

    return status
