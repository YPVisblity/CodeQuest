# 範例：函式可以讀取全域變數，但若要修改它就需要特別宣告
player_name = "ARIA"

def show_player_name():
    return "玩家：" + player_name

print(show_player_name())
