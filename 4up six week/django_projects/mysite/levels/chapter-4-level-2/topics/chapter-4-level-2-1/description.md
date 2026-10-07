多媒體系統需要同時播放音訊與影片。如果依序呼叫兩個播放器，第二個播放器必須等第一個結束後才能開始。

請完成 play_multimedia(audio_path, video_path, audio_player, video_player) 函式：

1. 建立名為 AudioThread 的執行緒，執行 audio_player(audio_path)。
2. 建立名為 VideoThread 的執行緒，執行 video_player(video_path)。
3. 先使用 start() 啟動兩個執行緒。
4. 再使用 join() 等待兩個執行緒完成。
5. 完成後回傳 "多媒體播放完成"。

注意：必須先啟動兩個 Thread，才能開始等待。若啟動第一個 Thread 後立刻 join，音訊和影片仍會依序執行。

評測時會傳入測試播放器，不會真的開啟音訊或影片。
