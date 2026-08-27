"""patterns.py — the composition kit. Law 9: buy each rung only when it pays."""
from pathlib import Path


def route(value, lanes, classifier):
    """lanes: {label: {...config}}; classifier: value -> label.
    Routing's three wins: focus, cost tiers, privacy enforcement."""
    label = classifier(value)
    return {"lane": label, **lanes[label]}


def chain_with_gates(steps, gates):
    """Run step, check gate, continue. First failing gate stops the chain."""
    output = None
    for i, step in enumerate(steps):
        output = step(output) if i else step()
        if not gates[i](output):
            return output, i
    return output, None


def vote(verdicts, threshold):
    """Same task, N lenses. The threshold IS the precision/recall decision."""
    return {"flagged": sum(bool(v) for v in verdicts) >= threshold,
            "votes": len(verdicts)}


def scale_effort(complexity):
    """Anthropic's embedded rules: workers / max calls per worker."""
    return {"simple": (1, 10), "comparison": (2, 15), "complex": (10, None)}[complexity]


def orchestrate(query, plan, worker, artifact_dir, recorder=None):
    """Orchestrator-workers: plan first, references back, failures isolated."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "plan.md").write_text(f"# Plan\n\nQuery: {query}\n"
                                          + "\n".join(f"- {t['area']}: {t['objective']}" for t in plan))
    if recorder:
        recorder.log("plan-saved")
    references, failures = [], []
    for task in plan:
        try:
            references.append(worker(task["area"], task["objective"], artifact_dir))
        except Exception as exc:                       # isolated, never fatal
            failures.append({"area": task["area"], "error": str(exc)})
    areas = [t["area"] for t in plan]
    report = f"Report on: {query}\n" + "\n".join(
        f"- {a}: {'COMPLETE' if a in {r['area'] for r in references} else 'FAILED'}" for a in areas)
    return {"plan_saved": True, "references": references,
            "failures": failures, "report": report}
