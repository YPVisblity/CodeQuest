import json
from pathlib import Path

def load_levels(base_dir="levels"):
    """
    動態讀取 levels/ 資料夾下的所有關卡與題目，
    並組裝回原本的 LEVELS 串列結構。
    """
    levels_path = Path(base_dir)
    if not levels_path.exists():
        print(f"警告：找不到 {base_dir} 資料夾！")
        return []

    levels = []

    for lvl_dir in sorted(
        levels_path.iterdir(),
        key=lambda p: (p.name.startswith("bonus-"), p.name),
    ):
        if not lvl_dir.is_dir():
            continue

        level_json_file = lvl_dir / "level.json"
        if not level_json_file.exists():
            continue

        with open(level_json_file, "r", encoding="utf-8") as f:
            lvl_data = json.load(f)

        topics_dir = lvl_dir / "topics"
        lvl_data["topics"] = []

        if topics_dir.exists() and topics_dir.is_dir():
            for topic_dir in sorted(
                topics_dir.iterdir(),
                key=lambda p: int(p.name.split('-')[-1])
            ):
                if not topic_dir.is_dir():
                    continue

                info_file = topic_dir / "info.json"
                if not info_file.exists():
                    continue

                with open(info_file, "r", encoding="utf-8") as f:
                    topic_info = json.load(f)

                desc_file = topic_dir / "description.md"
                starter_file = topic_dir / "starter.py"
                test_file = topic_dir / "test.py"
                example_file = topic_dir / "example_code.py"

                topic_info["description"] = desc_file.read_text(encoding="utf-8") if desc_file.exists() else ""
                topic_info["starter_code"] = starter_file.read_text(encoding="utf-8") if starter_file.exists() else ""
                topic_info["test_code"] = test_file.read_text(encoding="utf-8") if test_file.exists() else ""
                topic_info["example_code"] = example_file.read_text(encoding="utf-8") if example_file.exists() else ""

                lvl_data["topics"].append(topic_info)

        levels.append(lvl_data)

    return levels

def get_levels_by_id():
    """呼叫 load_levels() 並轉換為以 level_id 為 Key 的字典"""
    levels = load_levels()
    return {level["id"]: level for level in levels if "id" in level}


if __name__ == "__main__":

    loaded_levels = load_levels()
    print(f"成功載入 {len(loaded_levels)} 個關卡！")

    if loaded_levels and loaded_levels[0].get("topics"):
        first_topic = loaded_levels[0]["topics"][0]
        print(f"第一題標題: {first_topic['title']}")
        print(f"第一題測試碼:\n{first_topic['test_code']}")