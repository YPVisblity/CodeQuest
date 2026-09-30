# 範例：實際使用gTTS建立繁體中文MP3
# 執行前需安裝：pip install gTTS
from gtts import gTTS

tts = gTTS(
    text="歡迎使用語音公告系統",
    lang="zh-TW",
)
tts.save("announcement.mp3")
print("語音檔已儲存")
