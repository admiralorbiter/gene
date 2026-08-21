---
state: ESCALATED
active_contract_id: CONTRACT-R8-8A
contract_path: research/contracts/CONTRACT-R8-8A.md
execution_base_sha: b64b67679168335722036d6af22c1fbcd025aea6
last_checkpoint: research/checkpoints/MIGRATION_CHECKPOINT.md
last_promotion: null
---

# Active Research Contract Pointer

**Current Operational State**: `READY`

This document provides the machine-discoverable operational entry point for autonomous research agents and Mother Base.

## Active Contract Details
- **Active Contract ID**: `CONTRACT-R8-8A`
- **Contract Path**: [`research/contracts/CONTRACT-R8-8A.md`](contracts/CONTRACT-R8-8A.md)
- **Execution Base Commit (`execution_base_sha`)**: `b64b67679168335722036d6af22c1fbcd025aea6`
- **Last Checkpoint**: [`research/checkpoints/MIGRATION_CHECKPOINT.md`](checkpoints/MIGRATION_CHECKPOINT.md)
- **Governance**: Design Review `APPROVED`, Authorized by `human`.

## Protocol for Agents
1. When starting work, parse the YAML frontmatter above.
2. If `state: ESCALATED` or `state: ESCALATED`, inspect the target contract at `contract_path` and optimize implementation strictly against its frozen constraints.
3. Prohibited from modifying hypotheses, estimands, metrics, or claim ceilings after freezing.
