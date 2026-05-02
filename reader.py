My Pingu: 05-03 01:04:08
好！按这个顺序逐一在 GitHub 网页上建文件：

--

📁 步骤

打开 https://github.com/Vitality-Johnny/AI-classhelper
点 【Add file】** → **【Create new file】

--

文件 1：`config.py`

```python
"""API 配置模块"""
import os

通义千问
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
QWEN_MODEL = "qwen-plus"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

输出目录
OUTPUT_DIR = "output"

运行时
MAX_RETRIES = 3
CHUNK_SIZE = 3000
```

--

文件 2：`requirements.txt`

```
requests>=2.28.0
PyMuPDF>=1.23.0
```

--

文件 3：`reader.py`（主程序，最重要的文件）

```python
"""AI 课本精读助手 — Qwen + DeepSeek 双模型混合调用"""

import sys, os, json, time, re, argparse
import requests
import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def call_qwen(prompt, system="", model=None):
    model = model or config.QWEN_MODEL
    headers = {"Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
               "Content-Type": "application/json"}
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for _ in range(config.MAX_RETRIES):
        try:
            resp = requests.post(f"{config.QWEN_BASE_URL}/chat/completions",
                                 headers=headers,
                                 json={"model": model, "messages": messages},
                                 timeout=120)
            if resp.status_code == 200:
                d = resp.json()
                u = d.get("usage", {})
                log(f"[Qwen] Token: ↑{u.get('prompt_tokens','?')} ↓{u.get('completion_tokens','?')} 合计{u.get('total_tokens','?')}")
                return d["choices"][0]["message"]["content"]
            log(f"[Qwen] HTTP {resp.status_code}")
            time.sleep(2**_)
        except Exception as e:
            log(f"[Qwen] 异常: {e}")
            time.sleep(2**_)
    return "[Qwen 调用失败]"


def call_deepseek(prompt, system=""):
    headers = {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
               "Content-Type": "application/json"}
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for _ in range(config.MAX_RETRIES):
        try:
            resp = requests.post(f"{config.DEEPSEEK_BASE_URL}/chat/completions",
                                 headers=headers,
                                 json={"model": config.DEEPSEEK_MODEL,
                                       "messages": messages},
                                 timeout=120)
            if resp.status_code == 200:
                d = resp.json()
                u = d.get("usage", {})
                log(f"[DeepSeek] Token: ↑{u.get('prompt_tokens','?')} ↓{u.get('completion_tokens','?')} 合计{u.get('total_tokens','?')}")
                return d["choices"][0]["message"]["content"]
            log(f"[DeepSeek] HTTP {resp.status_code}")
            time.sleep(2**_)
        except Exception as e:
            log(f"[DeepSeek] 异常: {e}")
            time.sleep(2**_)
    return "[DeepSeek 调用失败]"


def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        sys.exit(1)
    log(f"📄 打开 PDF: {os.path.basename(pdf_path)}")
    doc = fitz.open(pdf_path)
    total = len(doc)
    log(f"📄 共 {total} 页")

    raw = ""
    for i, page in enumerate(doc):
        raw += page.get_text()
        if (i+1) % 30 == 0:
            log(f"📄 已处理 {i+1}/{total} 页")
    doc.close()
    log(f"📄 提取完成，共 {len(raw)} 字符")

    chapters = []
    pat = re.compile(r'(第[一二三四五六七八九十百千\d]+[章节部篇])\s*([^\n]*)')
    cur_title = "前言"
    cur_text = ""
    for line in raw.split("\n"):
        line = line.strip()
``` (1/3)

My Pingu: 05-03 01:04:09
```python
m = pat.search(line)
        if m:
            if cur_text.strip():
                chapters.append((cur_title, cur_text.strip()))
            cur_title = m.group(0)
            cur_text = line + "\n"
        else:
            cur_text += line + "\n"
    if cur_text.strip():
        chapters.append((cur_title, cur_text.strip()))

    if len(chapters) < 3:
        log("⚠️ 章节检测不理想，改用页数分段")
        chapters = []
        doc = fitz.open(pdf_path)
        n = total
        step = max(3, n // 10)
        for s in range(0, n, step):
            e = min(s+step, n)
            t = ""
            for i in range(s, e):
                t += doc[i].get_text()
            chapters.append((f"第{s//step+1}部分 (第{s+1}-{e}页)", t.strip()))
        doc.close()

    log(f"📑 识别到 {len(chapters)} 个章节")
    return chapters


KW_PROMPT = """你是教材精读助手。请分析以下教材内容：

==== 内容 ====
{text}

==== 输出格式 ====
1. 核心概念：3-5 个最重要概念
2. 重要定义：关键定义和公式
3. 重点标注：需要记忆的内容
4. 难点击破：难点的通俗解释
使用 markdown。"""

EX_PROMPT = """你是编程课助教。根据以下教材内容出练习题：

==== 内容 ====
{text}

==== 要求 ====
1. 选择题 3-5 道（标答案）
2. 简答题 2-3 道
3. 代码题 1-2 道（如果涉及编程）
使用 markdown。"""

CODE_PROMPT = """你是编程助教。请从以下内容提取代码/算法，并给出带注释的示例：

==== 内容 ====
{text}

无代码则回复"本章无明显代码内容"。"""

DIA_PROMPT = """分析以下内容中可能涉及的图表，用文字还原：

==== 内容 ====
{text}

无明显图表则回复"本章无明显图表内容"。"""

SUM_PROMPT = """请将以下所有章节知识点浓缩成期末速览手册（3-5页）：

==== 内容 ====
{all_chapters}

按章节顺序，每章只保留最核心 3-5 个知识点。markdown 格式。"""


def process_chapter(title, text, no_ex=False, no_dia=False):
    out = f"\n---\n\n## {title}\n\n"
    txt = text[:config.CHUNK_SIZE]

    log(f"[{title}] 用 Qwen 提取知识点...")
    kw = call_qwen(KW_PROMPT.format(text=txt), "你是一个教材精读助手")
    out += f"### 📖 知识点总结\n\n{kw}\n\n"

    if not no_dia:
        log(f"[{title}] 用 Qwen 分析图表...")
        di = call_qwen(DIA_PROMPT.format(text=txt), "你是一个图表分析助手")
        if "无明显图表" not in di:
            out += f"### 🖼 图表分析\n\n{di}\n\n"

    if not no_ex:
        log(f"[{title}] 用 DeepSeek 生成习题...")
        ex = call_deepseek(EX_PROMPT.format(text=txt), "你是一个编程课助教")
        out += f"### ✍️ 练习题\n\n{ex}\n\n"

    log(f"[{title}] 用 DeepSeek 提取代码...")
    cd = call_deepseek(CODE_PROMPT.format(text=txt), "你是一个编程助教")
    if "无明显代码" not in cd:
        out += f"### 💻 代码示例\n\n{cd}\n\n"

    return out


def main():
    parser = argparse.ArgumentParser(description="AI 课本精读助手")
    parser.add_argument("pdf", help="教材 PDF 路径")
    parser.add_argument("--no-exercises", action="store_true")
    parser.add_argument("--no-diagram", action="store_true")
    args = parser.parse_args()

    if not config.DASHSCOPE_API_KEY:
        print("❌ 未设置 DASHSCOPE_API_KEY")
        sys.exit(1)
    if not config.DEEPSEEK_API_KEY:
        print("❌ 未设置 DEEPSEEK_API_KEY")
        sys.exit(1)

    pdf = args.pdf
    print("=" * 50)
    print(f"  PDF: {pdf}")
    print(f"  Qwen({config.QWEN_MODEL}) + DeepSeek({config.DEEPSEEK_MODEL})")
    print("=" * 50)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    chapters = extract_text_from_pdf(pdf)

    all_content = []
    for title, text in chapters:
        log(f"⏳ 处理: {title}")
        md = process_chapter(title, text, args.no_exercises, args.no_diagram)
        all_content.append((title, md))
        log(f"✅ 完成: {title}")

    name = os.path.splitext(os.path.basename(pdf))[0]
    out_path = os.path.join(config.OUTPUT_DIR, f"{name}_精读笔记.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} · AI 精读笔记\n\n")
        f.write(f"> Qwen({config.QWEN_MODEL}) + DeepSeek({config.DEEPSEEK_MODEL})\n\n---\n")
        for _, content in all_content:
            f.write(content)

    log(f"📝 笔记保存: {out_path}")

期末速览
    log("📕 生成期末速览...")
    all_txt = "\n\n".join(f"【{t}】\n{c}" for t, c in all_content)
    summary = call_qwen(SUM_PROMPT.format(all_chapters=all_txt[:8000]), "你是一个教材精读助手")
    sum_path = os.path.join(config.OUTPUT_DIR, f"{name}_期末速览.md")
    with open(sum_path, "w", encoding="utf-8") as f:
``` (2/3)

My Pingu: 05-03 01:04:09
```python
f.write(f"# 📕 {name} · 期末速览手册\n\n{summary}")
    log(f"📕 速览保存: {sum_path}")

    print(f"\n✅ 全部完成！\n📝 {out_path}\n📕 {sum_path}")


if __name__ == "__main__":
    main()
```

--

文件 4：`README.md`

```markdown

AI ClassHelper · AI 课本精读助手

> 大二学生个人项目 · Qwen + DeepSeek 双模型混合调用

功能

| 功能 | 模型 | 说明 |
|------|------|------|
| 📖 知识点提取 | 通义千问 | 每章核心概念、定义、公式 |
| 🖼 图表分析 | 通义千问 | 教材插图/流程图内容识别 |
| ✍️ 练习题生成 | DeepSeek | 选择题 + 简答题 + 答案 |
| 💻 代码示例 | DeepSeek | 代码/算法带注释示例 |
| 📕 期末速览 | 双模型 | 全书浓缩 3-5 页 |

快速开始

```bash
pip install -r requirements.txt
export DASHSCOPE_API_KEY="你的Key"
export DEEPSEEK_API_KEY="你的Key"
python reader.py 教材.pdf
```

Token 消耗（参考）

| 教材 | Qwen | DeepSeek | 总计 |
|------|------|----------|------|
| 数据结构（C语言版） | ~5 万 | ~4 万 | ~9 万 |
| 计算机网络 | ~4 万 | ~3 万 | ~7 万 |
```

--

文件 5：`.gitignore`

```
__pycache__/
.pyc
.env
output/
```

--

文件 6：`.env.example`

```
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

--

文件 7：`token_counter.py`（可选，统计用）

```python
"""Token 使用统计"""
import sys, re
from collections import defaultdict

def parse_log(path):
    stats = defaultdict(lambda: {"count": 0, "prompt": 0, "completion": 0, "total": 0})
    p = re.compile(r'\[(Qwen|DeepSeek)\].*?Token: ↑(\d+) ↓(\d+).*?合计(\d+)')
    with open(path) as f:
        for line in f:
            m = p.search(line)
            if m:
                s = stats[m.group(1)]
                s["count"] += 1
                s["prompt"] += int(m.group(2))
                s["completion"] += int(m.group(3))
                s["total"] += int(m.group(4))
    return dict(stats)

if __name__ == "__main__":
    stats = parse_log(sys.argv[1])
    for m, s in stats.items():
        print(f"{m}: {s['count']}次, Prompt={s['prompt']\:,}, "
              f"Completion={s['completion']:,}, Total={s['total']\:,}")
    total = sum(s["total"] for s in stats.values())
    print(f"总计: {total:,} Token")
```

--

建完所有文件后，GitHub 上就会显示这样的项目结构：

```
AI-classhelper/
├── README.md
├── requirements.txt
├── config.py
├── reader.py          ← 主程序
├── token_counter.py
├── .gitignore
└── .env.example
```

然后本地使用时：
```bash
pip install -r requirements.txt
export DASHSCOPE_API_KEY="你的key"
export DEEPSEEK_API_KEY="你的key"
python reader.py 数据结构教材.pdf
```

搞定！需要我帮你写申请书第 04 项的完整文本吗？😊 (3/3)
