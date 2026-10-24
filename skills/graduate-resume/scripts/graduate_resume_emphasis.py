"""Job-aware presentation derived from verified text without adding facts."""

from __future__ import annotations

import re
from typing import Any, Mapping


TERM_GROUPS = (
    (("电气", "自动化", "机电"), ("PLC", "梯形图", "西门子", "三菱", "电气控制", "电气识图", "电气制图", "电路基础", "电工基本操作技术", "AutoCAD", "CAD", "变频器", "接线", "调试", "故障排查", "故障报警", "继电器", "接触器", "断路器")),
    (("电力", "风电", "新能源", "运维", "升压站"), ("一次设备", "二次设备", "安装", "调试", "巡检", "维护", "低压配电", "电力系统", "安全规程", "电业安全工作规程", "升压站", "电气制图")),
    (("绘图", "设计", "CAD"), ("AutoCAD", "CAD", "二维绘图", "三维建模", "工程制图", "电气制图", "电气原理图", "I/O")),
    (("PLC", "自动化", "调试"), ("PLC", "S7-200/1200", "S7-200", "S7-1200", "梯形图", "STEP 7-MicroWIN", "编程", "在线调试", "故障排查", "传感器", "触摸屏", "组态", "联调")),
    (("销售", "商务", "客服"), ("商品咨询", "收银结算", "销售目标", "促销活动", "沟通", "客户服务")),
    (("行政", "文员", "办公", "宣传"), ("Word", "Excel", "PPT", "Office", "PS", "文档处理", "物料设计", "数据统计", "活动策划")),
)
TECHNICAL_TERMS = tuple(dict.fromkeys(term for _, terms in TERM_GROUPS for term in terms))


def job_context(target: Mapping[str, Any] | None) -> str:
    if target is None:
        return ""
    return "；".join((str(target.get("role", "")), *target.get("requirements", ())))


def relevant_terms(candidate: Mapping[str, Any], context: str = "") -> tuple[str, ...]:
    intention = context or "；".join((str(candidate.get("headline", "")), *candidate.get("directions", ())))
    folded = intention.casefold()
    terms = {term for triggers, values in TERM_GROUPS if any(trigger.casefold() in folded for trigger in triggers) for term in values}
    terms.update(term for term in TECHNICAL_TERMS if term.casefold() in folded)
    return tuple(sorted(terms, key=lambda term: (term.casefold() not in folded, -len(term), term)))


def relevance(value: str, terms: tuple[str, ...], context: str = "") -> int:
    matches = [term for term in terms if term.casefold() in value.casefold()]
    return sum(len(term) for term in matches) + 1000 * sum(len(term) for term in matches if term.casefold() in context.casefold())


def ordered_courses(value: str, terms: tuple[str, ...], context: str = "") -> str:
    separators = re.findall(r"[、；;，,]", value)
    if not separators or len(set(separators)) != 1:
        return value
    separator = separators[0]
    parts = value.split(separator)
    if any(not part.strip() for part in parts):
        return value
    return separator.join(sorted(parts, key=lambda part: -relevance(part, terms, context)))


def emphasis_spans(value: str, terms: tuple[str, ...], academic: bool = False) -> tuple[tuple[int, int], ...]:
    candidates = []
    for term in terms:
        pattern = re.escape(term)
        if term.isascii():
            pattern = r"(?<![A-Za-z0-9])" + pattern + r"(?![A-Za-z0-9])"
        for matched in re.finditer(pattern, value, flags=re.IGNORECASE):
            clause_start = max(value.rfind(mark, 0, matched.start()) for mark in "；;。！？\n") + 1
            prefix = value[clause_start:matched.start()]
            if re.search(r"不熟悉|未掌握|不了解|不具备|尚未|未参与|仅了解|待学习", prefix):
                continue
            candidates.append(matched.span())
    if academic:
        for matched in re.finditer(r"(?:成绩|专业|年级)?排名前\s*(\d+(?:\.\d+)?)\s*%|(?:一|二|三)等奖学金", value):
            if matched.group(1) is None or float(matched.group(1)) <= 10:
                candidates.append(matched.span())
        for matched in re.finditer(r"(?<![\d.])(\d{1,3}(?:\.\d+)?)\s*(?:分|/\s*100)(?!\d)", value):
            course_start = max(value.rfind(mark, 0, matched.start()) for mark in "；;、，,\n") + 1
            if relevance(value[course_start:matched.start()], terms) and 90 <= float(matched.group(1)) <= 100:
                candidates.append(matched.span())
    selected = []
    for start, end in sorted(candidates, key=lambda span: (span[0], -span[1])):
        if any(start < prior_end and end > prior_start for prior_start, prior_end in selected):
            continue
        if len(selected) == 3:
            break
        selected.append((start, end))
    return tuple(selected)
