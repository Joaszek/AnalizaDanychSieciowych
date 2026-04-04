import sys
import math


class AdjacencyMatrix:
    """
    Reprezentacja grafu jako macierzy wag.

    adjacency_matrix[i][j] = waga krawędzi i→j,
    lub None gdy krawędź nie istnieje.

    Złożoność pamięciowa: O(V²)
    Sprawdzenie sąsiedztwa: O(1)
    Iteracja po sąsiadach: O(V)
    """

    def __init__(self, num_vertices: int):
        self._n = num_vertices
        self._edge_count = 0
        self._matrix = [[None] * num_vertices for _ in range(num_vertices)]


    def add_edge(self, u: int, v: int, w: float) -> None:
        if self._matrix[u][v] is None:
            self._edge_count += 1
        self._matrix[u][v] = w

    def get_neighbors(self, u: int):
        return [
            (v, self._matrix[u][v])
            for v in range(self._n)
            if self._matrix[u][v] is not None
        ]

    def get_all_edges(self):
        edges = []
        for u in range(self._n):
            for v in range(self._n):
                if self._matrix[u][v] is not None:
                    edges.append((u, v, self._matrix[u][v]))
        return edges

    def has_edge(self, u: int, v: int) -> bool:
        return self._matrix[u][v] is not None

    def get_weight(self, u: int, v: int):
        return self._matrix[u][v]

    @property
    def num_vertices(self) -> int:
        return self._n

    @property
    def num_edges(self) -> int:
        return self._edge_count

    def memory_bytes(self) -> int:
        return self._n * self._n * 28

    def __repr__(self):
        return f"AdjacencyMatrix(V={self._n}, E={self._edge_count})"


class EdgeList:

    def __init__(self, num_vertices: int):
        self._n = num_vertices
        self._edges = []
        self._edge_set = set()

    def add_edge(self, u: int, v: int, w: float) -> None:
        if (u, v) not in self._edge_set:
            self._edges.append((u, v, w))
            self._edge_set.add((u, v))

    def get_neighbors(self, u: int):
        """Zwraca listę (sąsiad, waga) – O(E)."""
        return [(v, w) for (a, v, w) in self._edges if a == u]

    def get_all_edges(self):
        return list(self._edges)

    def has_edge(self, u: int, v: int) -> bool:
        return (u, v) in self._edge_set

    @property
    def num_vertices(self) -> int:
        return self._n

    @property
    def num_edges(self) -> int:
        return len(self._edges)

    def memory_bytes(self) -> int:
        return len(self._edges) * 120 + 56

    def __repr__(self):
        return f"EdgeList(V={self._n}, E={len(self._edges)})"


class AdjacencyList:

    def __init__(self, num_vertices: int):
        self._n = num_vertices
        self._adj = {i: [] for i in range(num_vertices)}
        self._edge_count = 0

    def add_edge(self, u: int, v: int, w: float) -> None:
        self._adj[u].append((v, w))
        self._edge_count += 1

    def get_neighbors(self, u: int):
        return list(self._adj[u])

    def get_all_edges(self):
        edges = []
        for u, neighbors in self._adj.items():
            for v, w in neighbors:
                edges.append((u, v, w))
        return edges

    def has_edge(self, u: int, v: int) -> bool:
        return any(nb == v for nb, _ in self._adj[u])

    @property
    def num_vertices(self) -> int:
        return self._n

    @property
    def num_edges(self) -> int:
        return self._edge_count

    def memory_bytes(self) -> int:
        return self._edge_count * 120 + self._n * 200

    def __repr__(self):
        return f"AdjacencyList(V={self._n}, E={self._edge_count})"


def create_graph(structure_name: str, num_vertices: int):

    mapping = {
        "adjacency_matrix": AdjacencyMatrix,
        "edge_list":        EdgeList,
        "adjacency_list":   AdjacencyList,
    }
    if structure_name not in mapping:
        raise ValueError(
            f"Nieznana struktura: '{structure_name}'. "
            f"Dostępne: {list(mapping.keys())}"
        )
    return mapping[structure_name](num_vertices)