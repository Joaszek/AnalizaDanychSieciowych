import random
from graph_structures import create_graph, AdjacencyMatrix, EdgeList, AdjacencyList


def generate_random_graph(
    structure_name: str,
    num_vertices: int,
    density: float,
    weight_min: int = 1,
    weight_max: int = 100,
    allow_negative: bool = False,
    seed: int = None,
) -> object:
    if seed is not None:
        random.seed(seed)

    graph = create_graph(structure_name, num_vertices)

    max_edges = num_vertices * (num_vertices - 1)
    target_edges = int(max_edges * density)

    possible = [
        (u, v)
        for u in range(num_vertices)
        for v in range(num_vertices)
        if u != v
    ]
    random.shuffle(possible)

    for u, v in possible[:target_edges]:
        if allow_negative:
            w = random.randint(weight_min, weight_max)
        else:
            w = random.randint(max(1, weight_min), weight_max)
        graph.add_edge(u, v, w)

    return graph


def generate_graph_all_structures(
    num_vertices: int,
    density: float,
    weight_min: int = 1,
    weight_max: int = 100,
    allow_negative: bool = False,
    seed: int = 42,
) -> dict:

    structures = ["adjacency_matrix", "edge_list", "adjacency_list"]
    graphs = {}
    for s in structures:
        graphs[s] = generate_random_graph(
            structure_name=s,
            num_vertices=num_vertices,
            density=density,
            weight_min=weight_min,
            weight_max=weight_max,
            allow_negative=allow_negative,
            seed=seed,
        )
    return graphs


def generate_graph_with_negative_cycle(
    structure_name: str,
    num_vertices: int,
    density: float = 0.3,
    seed: int = 42,
) -> object:

    graph = generate_random_graph(
        structure_name=structure_name,
        num_vertices=num_vertices,
        density=density,
        weight_min=-5,
        weight_max=50,
        seed=seed,
    )
    
    if num_vertices >= 3:
        graph.add_edge(0, 1, -10)
        graph.add_edge(1, 2, -10)
        graph.add_edge(2, 0, -10)

    return graph