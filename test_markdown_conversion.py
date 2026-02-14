#!/usr/bin/env python3
"""
Test enhanced Markdown conversion
"""

from gmail_send_skill import GmailSendSkill
from skill_compat import ExecutionContext

def test_enhanced_conversion():
    skill = GmailSendSkill()
    
    test_markdown = """# 测试标题

这是一个 **粗体** 和 *斜体* 文本测试。

## 功能测试

- 列表项 1
- 列表项 2
- 列表项 3

`代码示例`

> 这是一个引用块

[链接示例](https://example.com)

---

*结束*
"""

    print("🧪 测试增强的 Markdown 转换")
    print("=" * 40)
    
    html_result = skill._convert_markdown_to_html(test_markdown)
    
    print(f"HTML 转换结果长度: {len(html_result)} 字符")
    print(f"包含样式表: {'<style>' in html_result}")
    print(f"包含 DOCTYPE: {'<!DOCTYPE html>' in html_result}")
    print(f"包含标题标签: {'<h1>' in html_result}")
    print(f"包含粗体标签: {'<strong>' in html_result}")
    print(f"包含列表标签: {'<ul>' in html_result}")
    print(f"包含链接标签: {'<a href=' in html_result}")
    
    # 保存测试结果到文件
    with open('test_html_output.html', 'w', encoding='utf-8') as f:
        f.write(html_result)
    print("\n✅ HTML 输出已保存到 test_html_output.html")
    
    # 测试状态信息
    print("\n📊 Markdown 支持状态:")
    from gmail_send_skill import MARKDOWN_AVAILABLE, MARKDOWN_VERSION, AVAILABLE_EXTENSIONS
    print(f"Markdown 库可用: {MARKDOWN_AVAILABLE}")
    if MARKDOWN_AVAILABLE:
        print(f"Markdown 版本: {MARKDOWN_VERSION}")
        print(f"可用扩展: {AVAILABLE_EXTENSIONS}")
    else:
        print("使用内置基础转换器")

if __name__ == "__main__":
    test_enhanced_conversion()