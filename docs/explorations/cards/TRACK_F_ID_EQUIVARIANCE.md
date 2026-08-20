# Experiment Card — Track F: Reported-Lineage Identifier Equivariance

## QUESTION
Does the model's reported-support lineage citation set ($\mathcal{R}$, $P_{\text{reported}}$) depend on the arbitrary token string format used to label memory IDs (e.g. natural words vs short codes vs random alphanumeric hashes), and how robust is the readout interface to label permutation?

## PRIMARY MANIPULATION
Evaluate identical semantic inference tasks under 3 distinct identifier tokenization mappings:
- **Mapping A (Semantic Natural):** `parent_1 = "KAVO_ARCHIVE"`, `parent_2 = "RILEN_LOG"`, `foil = "TEPA_DOC"`
- **Mapping B (Short Coded):** `parent_1 = "ZURI_01"`, `parent_2 = "MEKO_02"`, `foil = "NAVI_99"`
- **Mapping C (Random Alphanumeric Hashes):** `parent_1 = "NODE_8F3A2B"`, `parent_2 = "NODE_E1C7D9"`, `foil = "NODE_4B6E02"`

All prompts are presented in randomized order. Emitted citation IDs are unmapped back to semantic canonical nodes.

## FROZEN CONTROLS
- 2-premise first-order Horn clause task.
- Structured JSON prompt contract.
- Greedy decoding ($T=0.0$, seed=42) on `gemma3:12b`.

## PRIMARY ENDPOINTS
- $A_{\text{ID}} = P(\text{identical semantic parent set cited after unmapping})$ (Equivariance Agreement)
- $E_{\text{ID}} = 1 - A_{\text{ID}}$ (Readout Interface Distortion Rate)

## FALSIFIER
If $A_{\text{ID}} = 1.000$ ($E_{\text{ID}} = 0.000$), the reported-lineage interface is perfectly equivariant to identifier tokenization. If $E_{\text{ID}} > 0.20$, self-reported citations contain significant prompt-label artifacts.

## ZERO-COMPUTE GATE
Deterministic bijective unmapping test verifying that all ID sets correctly invert without collision.

## LIVE CALL CEILING
12 calls (4 contexts × 3 ID mappings). Hard maximum: 18 calls.

## STOP RULE
Stop immediately after 12 calls.

## STATUS
PROVISIONAL — EXPLORATORY ROUND 1
