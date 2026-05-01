import os
import csv
import math
from typing import List

from experiments import ExperimentResult
from config import RESULTS_DIR

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("  [UWAGA] matplotlib niedostępny  wykresy pominięte.")


def save_csv(results: List[ExperimentResult], filename: str = "results.csv") -> str:
    """Zapisuje wyniki do pliku CSV."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    filepath = os.path.join(RESULTS_DIR, filename)

    fields = [
        "algorithm", "structure", "num_vertices", "density",
        "num_edges", "avg_time_ms", "std_time_ms",
        "memory_bytes", "avg_operations", "negative_cycle",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "algorithm":      r.algorithm,
                "structure":      r.structure,
                "num_vertices":   r.num_vertices,
                "density":        r.density,
                "num_edges":      r.num_edges,
                "avg_time_ms":    r.avg_time_ms,
                "std_time_ms":    r.std_time_ms,
                "memory_bytes":   r.memory_bytes,
                "avg_operations": r.avg_operations,
                "negative_cycle": r.negative_cycle,
            })

    return filepath


def print_summary_table(results: List[ExperimentResult]) -> None:

    header = (
        f"{'Algorytm':<22} {'Struktura':<20} {'V':>6} {'gęst.':>6} "
        f"{'E':>7} {'czas[ms]':>10} {'±':>8} {'pamięć[KB]':>11} {'operacje':>10}"
    )
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)

    prev_algo = None
    for r in sorted(results, key=lambda x: (x.algorithm, x.structure, x.num_vertices, x.density)):
        if r.algorithm != prev_algo:
            if prev_algo is not None:
                print()
            prev_algo = r.algorithm

        mem_kb = r.memory_bytes / 1024
        nc_flag = " [NEG.CYCLE!]" if r.negative_cycle else ""
        print(
            f"{r.algorithm:<22} {r.structure:<20} {r.num_vertices:>6} {r.density:>6.1f} "
            f"{r.num_edges:>7} {r.avg_time_ms:>10.4f} {r.std_time_ms:>8.4f} "
            f"{mem_kb:>11.1f} {r.avg_operations:>10.0f}{nc_flag}"
        )

    print(sep)


def _filter(results, algo=None, structure=None, density=None, size=None):
    out = results
    if algo:      out = [r for r in out if r.algorithm == algo]
    if structure: out = [r for r in out if r.structure == structure]
    if density is not None: out = [r for r in out if abs(r.density - density) < 1e-6]
    if size is not None:    out = [r for r in out if r.num_vertices == size]
    return out


COLORS = {
    "adjacency_matrix": "#e74c3c",
    "edge_list":        "#2ecc71",
    "adjacency_list":   "#3498db",
}
LABELS = {
    "adjacency_matrix": "Macierz wag",
    "edge_list":        "Lista krawędzi",
    "adjacency_list":   "Lista sąsiedztwa",
}


def plot_time_vs_size(results: List[ExperimentResult], density: float = 0.3) -> None:
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Czas wykonania vs rozmiar grafu  (gęstość = {density:.1f})",
        fontsize=13, fontweight="bold"
    )

    for ax, algo in zip(axes, ["Dijkstra", "Bellman-Ford"]):
        for struct in ["adjacency_matrix", "edge_list", "adjacency_list"]:
            data = _filter(results, algo=algo, structure=struct, density=density)
            data.sort(key=lambda r: r.num_vertices)
            if not data:
                continue
            xs = [r.num_vertices for r in data]
            ys = [r.avg_time_ms for r in data]
            errs = [r.std_time_ms for r in data]
            ax.errorbar(xs, ys, yerr=errs,
                        label=LABELS[struct], color=COLORS[struct],
                        marker="o", linewidth=2, capsize=4)

        ax.set_title(algo, fontsize=11)
        ax.set_xlabel("Liczba wierzchołków (V)")
        ax.set_ylabel("Czas [ms]")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xscale("log")

    plt.tight_layout()
    _save_fig("time_vs_size.png")


def plot_time_vs_density(results: List[ExperimentResult], size: int = 250) -> None:
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Czas wykonania vs gęstość grafu  (V = {size})",
        fontsize=13, fontweight="bold"
    )

    for ax, algo in zip(axes, ["Dijkstra", "Bellman-Ford"]):
        for struct in ["adjacency_matrix", "edge_list", "adjacency_list"]:
            data = _filter(results, algo=algo, structure=struct, size=size)
            data.sort(key=lambda r: r.density)
            if not data:
                continue
            xs = [r.density for r in data]
            ys = [r.avg_time_ms for r in data]
            ax.plot(xs, ys, label=LABELS[struct],
                    color=COLORS[struct], marker="s", linewidth=2)

        ax.set_title(algo, fontsize=11)
        ax.set_xlabel("Gęstość grafu")
        ax.set_ylabel("Czas [ms]")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save_fig("time_vs_density.png")


def plot_memory_vs_size(results: List[ExperimentResult], density: float = 0.3) -> None:
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title(
        f"Zużycie pamięci vs rozmiar grafu (gęstość = {density:.1f})",
        fontsize=12, fontweight="bold"
    )

    for struct in ["adjacency_matrix", "edge_list", "adjacency_list"]:
        data = _filter(results, algo="Dijkstra", structure=struct, density=density)
        data.sort(key=lambda r: r.num_vertices)
        if not data:
            continue
        xs = [r.num_vertices for r in data]
        ys = [r.memory_bytes / 1024 for r in data]  # KB
        ax.plot(xs, ys, label=LABELS[struct],
                color=COLORS[struct], marker="^", linewidth=2)

    ax.set_xlabel("Liczba wierzchołków (V)")
    ax.set_ylabel("Zużycie pamięci [KB]")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")

    plt.tight_layout()
    _save_fig("memory_vs_size.png")


def plot_operations_vs_size(results: List[ExperimentResult], density: float = 0.3) -> None:
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"Liczba operacji (relaksacji) vs rozmiar  (gęstość = {density:.1f})",
        fontsize=13, fontweight="bold"
    )

    for ax, algo in zip(axes, ["Dijkstra", "Bellman-Ford"]):
        for struct in ["adjacency_matrix", "edge_list", "adjacency_list"]:
            data = _filter(results, algo=algo, structure=struct, density=density)
            data.sort(key=lambda r: r.num_vertices)
            if not data:
                continue
            xs = [r.num_vertices for r in data]
            ys = [r.avg_operations for r in data]
            ax.plot(xs, ys, label=LABELS[struct],
                    color=COLORS[struct], marker="D", linewidth=2)

        ax.set_title(algo, fontsize=11)
        ax.set_xlabel("Liczba wierzchołków (V)")
        ax.set_ylabel("Liczba operacji")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xscale("log")
        ax.set_yscale("log")

    plt.tight_layout()
    _save_fig("operations_vs_size.png")


def plot_dijkstra_vs_bellmanford(results: List[ExperimentResult], density: float = 0.3) -> None:
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(
        f"Dijkstra vs Bellman-Ford czas (lista sąsiedztwa, gęstość={density:.1f})",
        fontsize=12, fontweight="bold"
    )

    algo_colors = {"Dijkstra": "#8e44ad", "Bellman-Ford": "#e67e22"}

    for algo, color in algo_colors.items():
        data = _filter(results, algo=algo, structure="adjacency_list", density=density)
        data.sort(key=lambda r: r.num_vertices)
        if not data:
            continue
        xs = [r.num_vertices for r in data]
        ys = [r.avg_time_ms for r in data]
        errs = [r.std_time_ms for r in data]
        ax.errorbar(xs, ys, yerr=errs,
                    label=algo, color=color,
                    marker="o", linewidth=2.5, capsize=4)

    ax.set_xlabel("Liczba wierzchołków (V)")
    ax.set_ylabel("Czas [ms]")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")

    plt.tight_layout()
    _save_fig("dijkstra_vs_bellmanford.png")


def generate_all_plots(results: List[ExperimentResult]) -> None:
    if not MATPLOTLIB_AVAILABLE:
        print("  Wykresy pominięte (brak matplotlib).")
        return

    print("Generowanie wykresów...")
    plot_time_vs_size(results, density=0.3)
    plot_time_vs_density(results, size=250)
    plot_memory_vs_size(results, density=0.3)
    plot_operations_vs_size(results, density=0.3)
    plot_dijkstra_vs_bellmanford(results, density=0.3)
    print(f"  Wykresy zapisane w katalogu: {RESULTS_DIR}/")


def _save_fig(filename: str) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"    Zapisano: {path}")


def load_csv(filename: str = "results.csv") -> List[ExperimentResult]:
    """Wczytuje wyniki z pliku CSV."""
    filepath = os.path.join(RESULTS_DIR, filename)
    results = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(ExperimentResult(
                algorithm=row["algorithm"],
                structure=row["structure"],
                num_vertices=int(row["num_vertices"]),
                density=float(row["density"]),
                num_edges=int(row["num_edges"]),
                avg_time_ms=float(row["avg_time_ms"]),
                std_time_ms=float(row["std_time_ms"]),
                memory_bytes=int(row["memory_bytes"]),
                avg_operations=float(row["avg_operations"]),
                negative_cycle=row["negative_cycle"].strip().lower() in ("true", "1", "yes"),
            ))
    return results


def print_analysis(results: List[ExperimentResult]) -> None:
    """Drukuje automatyczną analizę tekstową wyników."""
    print("=" * 70)
    print("  ANALIZA WYNIKÓW")
    print("=" * 70)

    for algo in ["Dijkstra", "Bellman-Ford"]:
        print(f"── {algo} ──")
        algo_results = _filter(results, algo=algo)
        if not algo_results:
            continue

        max_v = max(r.num_vertices for r in algo_results)
        large_graph = _filter(algo_results, size=max_v, density=0.3)
        if large_graph:
            best = min(large_graph, key=lambda r: r.avg_time_ms)
            worst = max(large_graph, key=lambda r: r.avg_time_ms)
            print(
                f"  Dla V={max_v}, gęstość=0.3:"
                f"Najszybsza struktura : {best.structure} ({best.avg_time_ms:.2f} ms)"
                f"Najwolniejsza        : {worst.structure} ({worst.avg_time_ms:.2f} ms)"
                f"Współczynnik różnicy : {worst.avg_time_ms / max(best.avg_time_ms, 0.001):.1f}x"
            )

        mem_results = _filter(algo_results, density=0.3, size=max_v)
        if mem_results:
            print("  Zużycie pamięci (V={}, gęstość=0.3):".format(max_v))
            for r in sorted(mem_results, key=lambda x: x.memory_bytes):
                print(f"    {r.structure:<20}: {r.memory_bytes/1024:.1f} KB")

    print()


if __name__ == "__main__":
    csv_path = os.path.join(RESULTS_DIR, "results.csv")
    print(f"Wczytywanie wyników z: {csv_path}")
    results = load_csv("results.csv")
    print(f"Załadowano {len(results)} rekordów.\n")

    main_results = [r for r in results if "neg.cycle" not in r.algorithm]

    print_summary_table(main_results)
    print_analysis(main_results)
    generate_all_plots(main_results)