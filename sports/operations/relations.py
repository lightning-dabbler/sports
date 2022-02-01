def create_relation(datasets_map, dataset, *order_of_dependency):
    current_node = datasets_map[dataset]
    current_node["fetch"] = True
    for node in order_of_dependency:
        node = datasets_map[node]
        node["fetch"] = True
        current_node = node
    return current_node
