import algorithms
import heapq
import math

INF = math.inf

def dijkstra(graph, source: int) -> dict:

    n = graph.num_vertices
    dist = {v: INF for v in range(n)}
    pred = {v: None for v in range(n)}
    dist[source] = 0
    operations = 0

    heap = [(0, source)]
    visited = set()

    while heap:
        d_u, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)

        if d_u > dist[u]:
            continue

        for v, w in graph.get_neighbors(u):
            operations += 1
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                heapq.heappush(heap, (new_dist, v))
    
    return {
        "distances":      dist,
        "predecessors":   pred,
        "operations":     operations,
        "negative_cycle": False,
    }

def bellman_ford(graph, source: int) -> dict:

    n = graph.num_vertices
    dist = {v: INF for v in range(n)}
    pred = {v: None for v in range(n)}
    dist[source] = 0
    operations = 0
 
    edges = graph.get_all_edges()
 
    for iteration in range(n - 1):
        updated = False
        for u, v, w in edges:
            operations += 1
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
 
        if not updated:
            break
 
    negative_cycle = False
    for u, v, w in edges:
        operations += 1
        if dist[u] != INF and dist[u] + w < dist[v]:
            negative_cycle = True
            break
 
    return {
        "distances":      dist,
        "predecessors":   pred,
        "operations":     operations,
        "negative_cycle": negative_cycle,
    }

def reconstruct_path(predecessors: dict, source: int, target: int) -> list:

    path = []
    current = target
 
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = predecessors.get(current)
    else:
        return []
 
    path.reverse()
    if path[0] != source:
        return []
    return path