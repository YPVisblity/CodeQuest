影片庫需要批次檢查，不能再一支一支手動看，主管要求做一份總覽報告，
顯示總共檢查了幾支、有幾支通過、哪幾支沒通過。

AI 幫忙寫了統計函式，但因為 Python 裡任何非空字串都是 True（包含
"Error:格式錯誤" 這種錯誤訊息字串），如果只用 if result: 判斷，
會把失敗的檔案也誤判成成功，導致整份統計報告完全不可信。

請完成 verify_video_library(file_list) 函式（可以直接呼叫上面提供的
verify_download() 來檢查每一支影片）：
輸入是一個 list，每個元素都是 file_info dict（格式跟 verify_download 一樣）
回傳一個 dict，包含：
  total：總共檢查了幾支影片
  success：成功下載的支數
  failed：失敗的檔案名稱列表（依照原始順序）

例如輸入 5 支影片，其中 2 支成功、3 支各因不同原因失敗
應回傳 {"total": 5, "success": 2, "failed": ["lesson03.txt", "lesson04.mp4", "lesson05.mp4"]}
