from bs4 import BeautifulSoup
import chardet

with open('已买到的宝贝.html', 'rb') as file:
    result = chardet.detect(file.read())

encoding = result['encoding']
with open('已买到的宝贝.html', 'r', encoding=encoding, errors='ignore') as file:
    html_content = file.read()

# 使用 Beautiful Soup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 选择所有包含 line-height:16px; 样式的 span 元素
selected_spans = soup.find_all('span', style=lambda value: 'line-height:16px;' in value if value else False)

# 打印选中的元素文本内容
for span in selected_spans:
    print(span.get_text())
