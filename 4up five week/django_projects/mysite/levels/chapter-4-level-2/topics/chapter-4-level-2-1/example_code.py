# 範例：建立一個簡單的背景工作 Thread
import threading

def background_task(message):
    print(message)

worker = threading.Thread(
    target=background_task,
    args=("背景工作開始",),
    name="WorkerThread",
)

worker.start()
worker.join()
print("背景工作完成")
