"""Audit and compute summary metrics directly from SQLite database."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gene.evaluation.exposure_engine import ExposureEngine


def audit_exp1b_db(db_path: str):
    p = Path(db_path)
    if not p.exists() or p.stat().st_size == 0:
        print(f"Error: Database file '{db_path}' not found or empty.")
        return

    conn = sqlite3.connect(db_path)
    engine = ExposureEngine()

    # 1. Load memory nodes to register parents
    cur = conn.cursor()
    cur.execute("SELECT node_id, generation, natural_text, locus_id, allele_id, run_id FROM memory_nodes WHERE generation = 1")
    g1_nodes = cur.fetchall()

    for n_id, gen, txt, locus, allele, run_id in g1_nodes:
        arm = "infected" if "infected" in run_id else "clean"
        # Find phenotype from dual_oracle_evaluations
        cur.execute("SELECT phenotype FROM dual_oracle_evaluations WHERE node_id = ?", (n_id,))
        row = cur.fetchone()
        phenotype = row[0] if row else "unknown"
        engine.register_parent(parent_node_id=n_id, parent_gen=gen, parent_phenotype=phenotype, arm=arm)

    # 2. Load transmission opportunities
    cur.execute("""
        SELECT opportunity_id, run_id, world_id, arm, exposure_p, parent_generation, child_generation,
               parent_node_id, parent_locus_id, parent_phenotype, child_task_id, target_predicate,
               is_exposed, is_generated, is_written, child_node_id, child_phenotype, ancestral_allele_fidelity
        FROM transmission_opportunities
    """)
    opp_rows = cur.fetchall()

    for r in opp_rows:
        engine.record_opportunity(
            opportunity_id=r[0],
            run_id=r[1],
            world_id=r[2],
            arm=r[3],
            exposure_p=r[4],
            parent_gen=r[5],
            child_gen=r[6],
            parent_node_id=r[7],
            parent_locus_id=r[8],
            parent_phenotype=r[9],
            child_task_id=r[10],
            target_predicate=r[11],
            is_exposed=bool(r[12]),
            is_generated=bool(r[13]),
            is_written=bool(r[14]),
            child_node_id=r[15],
            child_phenotype=r[16],
            ancestral_allele_fidelity=r[17],
        )

    # 3. Print Summary
    print("=" * 145)
    print(f"   EXPERIMENT 1B-A1: RECOMPUTED BALANCED EXPOSURE SUMMARY ({db_path})")
    print("=" * 145)
    print(f"{'Dose (p)':<10} | {'Contact X':<10} | {'tau_S':<8} | {'Write W_hat':<12} | {'R_trans':<8} | {'R_total':<8} | {'Clean Cov C':<14} | {'mu_de_novo':<12} | {'mu_unsupp':<12} | {'Fidelity F2':<12} | {'Epidemic State'}")
    print("-" * 145)

    grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    for p in grid:
        s = engine.compute_summary(exposure_p=p)
        tau_str = f"{s.epistemic_transmissibility_tau_S:.2f}" if s.epistemic_transmissibility_tau_S is not None else "N/A"
        w_str = f"{s.write_admission_W_hat:.2f}" if s.write_admission_W_hat is not None else "N/A"
        c_str = f"{s.clean_coverage_C*100:.1f}% ({s.clean_correct_derived}/{s.clean_opportunities})" if s.clean_coverage_C is not None else "N/A"
        mu_denovo_str = f"{s.mu_de_novo*100:.1f}% ({s.unexposed_false_children_emitted}/{s.unexposed_opportunities})" if s.unexposed_opportunities > 0 else "0.0%"
        mu_unsupp_str = f"{s.mu_unsupported_concrete*100:.1f}% ({s.unexposed_concrete_children_emitted}/{s.unexposed_opportunities})" if s.unexposed_opportunities > 0 else "0.0%"
        f2_str = f"{s.ancestral_fidelity_F2:.2f}" if s.ancestral_fidelity_F2 is not None else "N/A"
        
        if s.reproduction_number_R_trans > 1.0:
            rep_str = "SUPERCRITICAL (R > 1) [Amplification]"
        elif abs(s.reproduction_number_R_trans - 1.0) < 1e-4:
            rep_str = "CRITICAL (R = 1) [Replacement Equilibrium]"
        else:
            rep_str = "SUBCRITICAL (R < 1) [Lineage Decay]"

        print(f"p = {p:<6.2f} | X = {s.contact_rate_X:<6.2f} | {tau_str:<8} | {w_str:<12} | {s.reproduction_number_R_trans:<8.2f} | {s.reproduction_number_R_total_corruption:<8.2f} | {c_str:<14} | {mu_denovo_str:<12} | {mu_unsupp_str:<12} | {f2_str:<12} | {rep_str}")

    print("=" * 145)
    conn.close()


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "gene_exp1b_exposure_v2_20260820_020136.db"
    audit_exp1b_db(db)
