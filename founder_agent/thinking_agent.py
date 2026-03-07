"""Agent that turns founder inputs into structured ideas."""
from brain_input import brain_parser
from decision_engine.approval_queue import ApprovalQueue


def ingest_founder_inputs() -> dict:
    return brain_parser.ingest_to_queues()
