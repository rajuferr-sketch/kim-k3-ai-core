"""The 15 mandatory kim-k3 agents.

Import :mod:`kim_k3.agents.registry` to enumerate them and
:mod:`kim_k3.agents.orchestrator` to run the full pipeline.
"""

from kim_k3.agents.registry import AGENT_CLASSES, PIPELINE_ORDER, build_all, get

__all__ = ["AGENT_CLASSES", "PIPELINE_ORDER", "build_all", "get"]
