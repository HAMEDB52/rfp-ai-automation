import pytest

from rfp_automation.graph import END, StateGraph


def test_linear_graph_runs_in_order():
    g = StateGraph()
    g.add_node("a", lambda s: {**s, "path": s.get("path", "") + "a"})
    g.add_node("b", lambda s: {**s, "path": s["path"] + "b"})
    g.set_entry("a").add_edge("a", "b").add_edge("b", END)
    assert g.run({})["path"] == "ab"
    assert g.trace == ["a", "b"]


def test_conditional_edge_picks_branch():
    g = StateGraph()
    g.add_node("start", lambda s: s)
    g.add_node("yes", lambda s: {**s, "taken": "yes"})
    g.add_node("no", lambda s: {**s, "taken": "no"})
    g.set_entry("start")
    g.add_conditional_edge("start", lambda s: "yes" if s["flag"] else "no")
    g.add_edge("yes", END)
    g.add_edge("no", END)
    assert g.run({"flag": True})["taken"] == "yes"
    assert g.run({"flag": False})["taken"] == "no"


def test_cycle_is_stopped_by_step_limit():
    g = StateGraph()
    g.add_node("loop", lambda s: s)
    g.set_entry("loop").add_edge("loop", "loop")
    with pytest.raises(RuntimeError):
        g.run({}, max_steps=5)


def test_unknown_node_raises():
    g = StateGraph()
    g.add_node("a", lambda s: s)
    g.set_entry("a").add_edge("a", "ghost")
    with pytest.raises(KeyError):
        g.run({})
