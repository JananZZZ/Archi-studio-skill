from __future__ import annotations

from .models import Preferences
from .presets import MODE_DEFAULTS, PRESETS

QUESTIONS = [
    ("mode", "主要用途", [("resume", "简历 / 面试"), ("portfolio", "作品集 / Portfolio"), ("academic", "答辩 / 学术"), ("business", "商务汇报")]),
    ("density", "内容密度", [("concise", "精简"), ("balanced", "平衡"), ("detailed", "详细")]),
    ("palette", "视觉风格", [(k, v["label"]) for k, v in PRESETS.items()]),
    ("language", "语言", [("zh+en", "中文为主 + 必要英文/缩写"), ("bilingual", "中英均衡"), ("zh", "全中文"), ("en", "全英文")]),
    ("emphasis", "重点", [("product_evolution", "产品演进"), ("technical", "技术结构"), ("balanced", "两者均衡")]),
]


def interactive_questionnaire(input_fn=input, print_fn=print) -> Preferences:
    p = Preferences()
    print_fn("\nArchi Studio · 意向问卷（回车使用默认值）")
    for key, title, options in QUESTIONS:
        print_fn(f"\n{title}：")
        for i, (_, label) in enumerate(options, 1):
            print_fn(f"  {i}. {label}")
        current = getattr(p, key)
        default_idx = next((i for i, (v, _) in enumerate(options, 1) if v == current), 1)
        raw = input_fn(f"选择 [默认 {default_idx}]：").strip()
        idx = default_idx
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            idx = int(raw)
        setattr(p, key, options[idx - 1][0])
        if key == "mode":
            defaults = MODE_DEFAULTS.get(p.mode, {})
            for dk, dv in defaults.items():
                setattr(p, dk, dv)
    yn = input_fn("\n生成可交互式编辑器？ [Y/n]：").strip().lower()
    p.interactive_editor = yn not in {"n", "no", "0"}
    return p
