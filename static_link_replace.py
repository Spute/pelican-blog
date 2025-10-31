import os
import re
from bs4 import BeautifulSoup

# 需要替换的路径前缀
R2_PUBLIC_URL = "https://blog-cdn.520233.best"  # 替换为你自己的 R2 公网 URL

# 遍历指定文件夹下的所有 .html 文件
def replace_static_paths_in_html(directory: str, url_prefix: str):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"正在处理文件: {file_path}")

                # 读取 HTML 文件
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 使用 BeautifulSoup 解析 HTML
                soup = BeautifulSoup(content, "html.parser")

                # 找到所有带有 src 或 href 属性的标签，并替换路径
                modified = False

                # 替换 <img> 和其他带 src 属性的标签
                for tag in soup.find_all(src=True):
                    original_src = tag['src']
                    if original_src.startswith("/static/"):
                        new_src = f"{url_prefix}{original_src}"
                        tag['src'] = new_src
                        modified = True
                        print(f"修改：src={original_src} -> src={new_src}")

                # 替换 <link> 和其他带 href 属性的标签
                for tag in soup.find_all(href=True):
                    original_href = tag['href']
                    if original_href.startswith("/static/"):
                        new_href = f"{url_prefix}{original_href}"
                        tag['href'] = new_href
                        modified = True
                        print(f"修改：href={original_href} -> href={new_href}")

                # 如果内容有修改，写回文件
                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    print(f"文件已更新：{file_path}")

# 运行脚本
if __name__ == "__main__":
    output_directory = "output"  # 替换为你的文件夹路径
    replace_static_paths_in_html(output_directory, R2_PUBLIC_URL)
