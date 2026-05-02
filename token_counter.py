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
