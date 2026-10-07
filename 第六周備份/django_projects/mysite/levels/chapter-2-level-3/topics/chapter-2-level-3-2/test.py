html1 = """
<html><body>
<h2>第一篇文章</h2>
<p>內容...</p>
<h2>第二篇文章</h2>
<p>內容...</p>
<h2>第三篇文章</h2>
</body></html>
"""
result1 = extract_titles(html1)

html2 = """
<html><body>
<h1>這不是h2</h1>
<h2>唯一的標題</h2>
</body></html>
"""
result2 = extract_titles(html2)

html3 = "<html><body><p>沒有任何h2標籤</p></body></html>"
result3 = extract_titles(html3)