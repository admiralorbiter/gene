"""Preflight tests for Track S: Support Acquisition from Observable Traces."""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from gene.experiments.trace_support_compiler import ExecutionTraceNode, TraceSupportCompiler


def test_trace_support_compiler_recombinant_support():
    """Verify that backward slicing extracts {{A, B}, {D, E}} from execution DAG with OR-support."""
    compiler = TraceSupportCompiler()

    # Root assumptions
    compiler.add_node(ExecutionTraceNode(node_id="fact_A", claim_type="founder", claim_value="KIRA", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_B", claim_type="assignment", claim_value="SEC_LEAD", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_D", claim_type="founder", claim_value="VALEN", is_root_premise=True))
    compiler.add_node(ExecutionTraceNode(node_id="fact_E", claim_type="assignment", claim_value="DIRECTOR", is_root_premise=True))

    # Intermediate G1 deductions
    compiler.add_node(ExecutionTraceNode(node_id="lemma_P1", claim_type="protocol", claim_value="PROTO_X7", support_environments=[["fact_A", "fact_B"]]))
    compiler.add_node(ExecutionTraceNode(node_id="lemma_P2", claim_type="protocol", claim_value="PROTO_X7", support_environments=[["fact_D", "fact_E"]]))

    # Target G2 synthesis: target_C is supported EITHER by lemma_P1 OR by lemma_P2
    compiler.add_node(ExecutionTraceNode(
        node_id="target_C",
        claim_type="protocol",
        claim_value="PROTO_X7",
        support_environments=[["lemma_P1"], ["lemma_P2"]]
    ))

    # Compile support for P1
    s_p1 = compiler.compile_minimal_support_environments("lemma_P1")
    assert s_p1 == [{"fact_A", "fact_B"}]

    # Compile support for target_C -> genuinely recovers both alternative environments!
    s_c = compiler.compile_minimal_support_environments("target_C")
    assert len(s_c) == 2
    assert {"fact_A", "fact_B"} in s_c
    assert {"fact_D", "fact_E"} in s_c
