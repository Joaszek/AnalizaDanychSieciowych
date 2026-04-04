#!/usr/bin/env python3
# ============================================================
#  main.py – główny plik uruchamiający projekt
# ============================================================
"""
Projekt Pr3: Dijkstra i Bellman-Ford – porównanie struktur danych

Uruchomienie:
    python main.py              # pełne eksperymenty
    python main.py --quick      # szybki test (mniejsze grafy)
    python main.py --demo       # demonstracja na małym grafie
    python main.py --no-plots   # bez generowania wykresów

Wyniki trafiają do katalogu ./results/
"""

import sys
import os
import argparse
import time

from config import GRAPH_SIZES, GRAPH_DENSITIES, RESULTS_DIR, SAVE_CSV, GENERATE_PLOTS
from graph_structures import AdjacencyMatrix, EdgeList, AdjacencyList
from graph_generator import generate_random_graph, generate_graph_all_structures
from algorithms import dijkstra, bellman_ford, reconstruct_path
from experiments import run_all_experiments, run_negative_cycle_experiment
from evaluation import (
    save_csv, print_summary_table, generate_all_plots, print_analysis
)

def run_demo() -> None:
    print("\n" + "=" * 60)
    print("  DEMO – mały graf (6 wierzchołków)")
    print("=" * 60)

    edges = [
        (0, 1, 4), (0, 2, 2),
        (1, 3, 5), (1, 2, 1),
        (2, 1, 1), (2, 3, 8), (2, 4, 10),
        (3, 5, 2),
        (4, 3, 2), (4, 5, 3),
    ]

    print("\n  Krawędzie grafu (u → v, waga):")
    for u, v, w in edges:
        print(f"    {u} → {v}  waga={w}")

    print("\n  Wyniki dla każdej struktury danych:")
    print()

    for struct_name in ["adjacency_matrix", "edge_list", "adjacency_list"]:
        graph = generate_random_graph(struct_name, 6, density=0, seed=0)
        for u, v, w in edges:
            graph.add_edge(u, v, w)

        res_d = dijkstra(graph, source=0)
        res_bf = bellman_ford(graph, source=0)

        print(f"  [{struct_name}]")
        print(f"  {'Cel':>4} | {'Dijkstra':>10} | {'B-Ford':>10} | {'Ścieżka (Dijkstra)':}")
        print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*10}-+-{'-'*30}")
        for target in range(1, 6):
            dist_d = res_d["distances"][target]
            dist_bf = res_bf["distances"][target]
            path = reconstruct_path(res_d["predecessors"], 0, target)
            path_str = " → ".join(map(str, path)) if path else "brak ścieżki"
            dist_d_str = f"{dist_d:.0f}" if dist_d < 1e14 else "∞"
            dist_bf_str = f"{dist_bf:.0f}" if dist_bf < 1e14 else "∞"
            print(f"  {target:>4} | {dist_d_str:>10} | {dist_bf_str:>10} | {path_str}")
        print(f"\n  Operacje – Dijkstra: {res_d['operations']}, Bellman-Ford: {res_bf['operations']}")
        print()


def run_quick_test() -> list:
    import config as cfg

    original_sizes     = cfg.GRAPH_SIZES
    original_densities = cfg.GRAPH_DENSITIES
    original_runs      = cfg.NUM_RUNS

    cfg.GRAPH_SIZES     = [20, 50, 100]
    cfg.GRAPH_DENSITIES = [0.2, 0.5]
    cfg.NUM_RUNS        = 3

    print("\n  Tryb QUICK – mniejsze grafy i mniej powtórzeń.")
    results = run_all_experiments(verbose=True)

    cfg.GRAPH_SIZES     = original_sizes
    cfg.GRAPH_DENSITIES = original_densities
    cfg.NUM_RUNS        = original_runs

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pr3: Dijkstra vs Bellman-Ford – porównanie struktur danych"
    )
    parser.add_argument("--quick",    action="store_true", help="Szybki test (mniejsze grafy)")
    parser.add_argument("--demo",     action="store_true", help="Tylko demonstracja na małym grafie")
    parser.add_argument("--no-plots", action="store_true", help="Pomiń generowanie wykresów")
    args = parser.parse_args()

    print("=" * 60)
    print("  Pr3: Dijkstra & Bellman-Ford – Analiza struktur danych")
    print("=" * 60)
    print(f"  Rozmiary grafów  : {GRAPH_SIZES}")
    print(f"  Gęstości         : {GRAPH_DENSITIES}")
    print(f"  Powtórzeń (runs) : (z config.py)")

    if args.demo:
        run_demo()
        return

    print("\n[1/4] Uruchamiam eksperymenty...\n")
    t0 = time.time()

    if args.quick:
        results = run_quick_test()
    else:
        results = run_all_experiments(verbose=True)

    print("\n[2/4] Test wykrywania ujemnego cyklu...")
    neg_results = run_negative_cycle_experiment(verbose=True)
    results.extend(neg_results)

    elapsed = time.time() - t0
    print(f"\n  Łączny czas eksperymentów: {elapsed:.1f} s")
    print(f"  Liczba pomiarów: {len(results)}")

    print("\n[3/4] Podsumowanie wyników:\n")
    main_results = [r for r in results if "neg.cycle" not in r.algorithm]
    print_summary_table(main_results)

    print_analysis(main_results)

    if SAVE_CSV:
        path = save_csv(results)
        print(f"  Wyniki CSV zapisane: {path}")

    if GENERATE_PLOTS and not args.no_plots:
        print("\n[4/4] Generowanie wykresów...")
        generate_all_plots(main_results)
    else:
        print("\n[4/4] Wykresy pominięte.")

    print("\n  Gotowe! Wyniki w katalogu:", os.path.abspath(RESULTS_DIR))
    print("=" * 60)


if __name__ == "__main__":
    main()