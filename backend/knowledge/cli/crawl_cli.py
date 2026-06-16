import os
import time

from services.crawler.client import KnowledgeApiClient
from services.crawler.parser import HtmlParser
from utils.text_utils import TextUtils
from config.settings import settings
from repositories.file_repository import FileRepository


def main():
    success = 0
    fail = 0
    total = 1001

    parser = HtmlParser()

    for i in range(total):
        knowledge_no = i + 1

        print(f"[{knowledge_no}/{total}] 获取KnowledgeNo:{knowledge_no}")

        try:
            # 1. 请求知识库内容
            knowledge_content = KnowledgeApiClient.fetch_knowledge_content(
                knowledge_no=knowledge_no
            )

            # 2. 判断内容是否存在
            if knowledge_content and knowledge_content.get("content"):

                # 3. 解析 HTML 为 Markdown
                md_content = parser.parse_html_to_markdown(
                    knowledge_no,
                    knowledge_content
                )

                # 4. 获取标题
                md_title = knowledge_content.get("title", "无标题")

                # 5. 清洗文件名中的非法字符
                clean_title = TextUtils.clean_filename(md_title)

                # 6. 限制文件名长度
                if len(clean_title) > 50:
                    clean_title = clean_title[:50].rstrip("_")

                # 7. 构建 Markdown 文件名
                file_name = f"{knowledge_no:04d}-{clean_title}.md"

                # 8. 构建完整保存路径
                file_path = os.path.join(settings.CRAWL_OUTPUT_DIR, file_name)

                # 9. 保存文件
                FileRepository.save_file(md_content, file_path)

                success += 1
                print(f"{knowledge_no} -> 保存成功: {file_name}")

            else:
                fail += 1
                print(f"{knowledge_no} -> 暂无内容, 保存失败")

        except Exception as e:
            fail += 1
            print(f"{knowledge_no} -> 请求或解析失败: {e}")

        # 10. 每次请求后暂停，避免请求太快
        time.sleep(0.2)

    print(f"\n爬取完成! 成功: {success}, 失败: {fail}")


if __name__ == "__main__":
    main()