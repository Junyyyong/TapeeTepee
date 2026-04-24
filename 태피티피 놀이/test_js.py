import re
with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(m.group(1))
