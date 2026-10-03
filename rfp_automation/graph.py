"""محرّك سير عمل صغير على هيئة رسم بياني للحالة.

مستوحى من نمط LangGraph: عقد تُحوِّل حالة مشتركة، وحوافّ شرطية تحدد المسار.
نُفِّذ من الصفر ليبقى المشروع بلا اعتماديات ثقيلة وقابلاً للاختبار بالكامل.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

State = dict
NodeFn = Callable[[State], State]

END = "__end__"


@dataclass
class StateGraph:
    nodes: dict[str, NodeFn] = field(default_factory=dict)
    edges: dict[str, str | Callable[[State], str]] = field(default_factory=dict)
    entry: str | None = None
    trace: list[str] = field(default_factory=list)

    def add_node(self, name: str, fn: NodeFn) -> "StateGraph":
        self.nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        self.edges[source] = target
        return self

    def add_conditional_edge(self, source: str, router: Callable[[State], str]) -> "StateGraph":
        self.edges[source] = router
        return self

    def set_entry(self, name: str) -> "StateGraph":
        self.entry = name
        return self

    def run(self, state: State, *, max_steps: int = 50) -> State:
        if not self.entry:
            raise ValueError("لم تُحدَّد عقدة البداية")
        current, steps = self.entry, 0
        self.trace = []
        while current != END:
            if steps >= max_steps:
                raise RuntimeError(f"تجاوز الحد الأقصى للخطوات عند العقدة {current}")
            if current not in self.nodes:
                raise KeyError(f"عقدة غير معرّفة: {current}")
            self.trace.append(current)
            state = self.nodes[current](state) or state
            nxt = self.edges.get(current, END)
            current = nxt(state) if callable(nxt) else nxt
            steps += 1
        return state
