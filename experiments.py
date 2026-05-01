import time
import tracemalloc
import statistics
from dataclasses import dataclass, field
from typing import List

from config import (
    GRAPH_SIZES, GRAPH_DENSITIES, WEIGHT_MIN, WEIGHT_MAX,
    NEGATIVE_WEIGHT_MIN, NEGATIVE_WEIGHT_MAX,
    NUM_RUNS, SOURCE_NODE, STRUCTURES,
)
from graph_generator import generate_graph_all_structures
from algorithms import dijkstra, bellman_ford


@dataclass
class ExperimentResult:
    algorithm:       str
    structure:       str
    num_vertices:    int
    density:         float
    avg_time_ms:     float
    std_time_ms:     float
    memory_bytes:    int
    avg_operations:  float
    negative_cycle:  bool = False
    num_edges:       int = 0


def _measure_single(algorithm_fn, graph, source: int) -> tuple:

    start = time.perf_counter()
    result = algorithm_fn(graph, source)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    return elapsed_ms, result["operations"], result.get("negative_cycle", False)


def run_single_experiment(
    algorithm_name: str,
    num_vertices: int,
    density: float,
    allow_negative: bool = False,
    seed: int = 42,
) -> List[ExperimentResult]:

    algorithm_fn = dijkstra if algorithm_name == "Dijkstra" else bellman_ford

    graphs = generate_graph_all_structures(
        num_vertices=num_vertices,
        density=density,
        weight_min=NEGATIVE_WEIGHT_MIN if allow_negative else WEIGHT_MIN,
        weight_max=WEIGHT_MAX,
        allow_negative=allow_negative,
        seed=seed,
    )

    results = []

    for structure_name, graph in graphs.items():
        times = []
        ops_list = []
        neg_cycle = False

        for run in range(NUM_RUNS):
            run_graph = generate_graph_all_structures(
                num_vertices=num_vertices,
                density=density,
                weight_min=NEGATIVE_WEIGHT_MIN if allow_negative else WEIGHT_MIN,
                weight_max=WEIGHT_MAX,
                allow_negative=allow_negative,
                seed=seed + run,
            )[structure_name]

            t_ms, ops, nc = _measure_single(algorithm_fn, run_graph, SOURCE_NODE)
            times.append(t_ms)
            ops_list.append(ops)
            neg_cycle = nc

        avg_t = statistics.mean(times)
        std_t = statistics.stdev(times) if len(times) > 1 else 0.0
        avg_ops = statistics.mean(ops_list)

        results.append(ExperimentResult(
            algorithm=algorithm_name,
            structure=structure_name,
            num_vertices=num_vertices,
            density=density,
            avg_time_ms=round(avg_t, 4),
            std_time_ms=round(std_t, 4),
            memory_bytes=graph.memory_bytes(),
            avg_operations=round(avg_ops, 1),
            negative_cycle=neg_cycle,
            num_edges=graph.num_edges,
        ))

    return results


def run_all_experiments(verbose: bool = True) -> List[ExperimentResult]:

    all_results = []
    total = len(GRAPH_SIZES) * len(GRAPH_DENSITIES) * 2
    done = 0

    for algo, allow_neg in [("Dijkstra", False), ("Bellman-Ford", True)]:
        for size in GRAPH_SIZES:
            for density in GRAPH_DENSITIES:
                done += 1
                if verbose:
                    print(
                        f"  [{done:3d}/{total}] {algo:12s} | "
                        f"V={size:5d} | gęstość={density:.1f} ...",
                        end=" ", flush=True
                    )

                results = run_single_experiment(
                    algorithm_name=algo,
                    num_vertices=size,
                    density=density,
                    allow_negative=allow_neg,
                    seed=42,
                )
                all_results.extend(results)

                if verbose:
                    rep = next(r for r in results if r.structure == "adjacency_list")
                    print(f"OK  ({rep.avg_time_ms:.2f} ms)")

    return all_results


def run_negative_cycle_experiment(verbose: bool = True) -> List[ExperimentResult]:

    from graph_generator import generate_graph_with_negative_cycle
    from graph_structures import create_graph

    if verbose:
        print("Test ujemnego cyklu dla Bellmana-Forda...")

    results = []
    for structure in STRUCTURES:
        graph = generate_graph_with_negative_cycle(
            structure_name=structure,
            num_vertices=20,
            density=0.3,
        )
        t_ms, ops, neg_cycle = _measure_single(bellman_ford, graph, SOURCE_NODE)
        results.append(ExperimentResult(
            algorithm="Bellman-Ford (neg.cycle)",
            structure=structure,
            num_vertices=20,
            density=0.3,
            avg_time_ms=round(t_ms, 4),
            std_time_ms=0.0,
            memory_bytes=graph.memory_bytes(),
            avg_operations=ops,
            negative_cycle=neg_cycle,
            num_edges=graph.num_edges,
        ))
        if verbose:
            status = "✓ wykryto" if neg_cycle else "✗ nie wykryto"
            print(f"    {structure:20s} ujemny cykl: {status}")

    return results