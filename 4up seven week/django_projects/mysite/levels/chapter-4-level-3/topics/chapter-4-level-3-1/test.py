tts_record = {}

class FakeTTS:
    def __init__(self, text, lang):
        tts_record["text"] = text
        tts_record["lang"] = lang

    def save(self, path):
        tts_record["saved_path"] = path

result1 = create_voice_announcement(
    "  歡迎來到第四章  ",
    "welcome.mp3",
    FakeTTS,
)
record1 = dict(tts_record)

result2 = create_voice_announcement(
    "   ",
    "empty.mp3",
    FakeTTS,
)

result3 = create_voice_announcement(
    "語音測試",
    "voice.wav",
    FakeTTS,
)
