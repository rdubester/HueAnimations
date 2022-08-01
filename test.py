import random
from typing import List

def largestIsland(grid: List[List[int]]) -> int:
    # turn the grid into a grap  where we hve a special marker for edges between two space seperated cells
    # find the largest connected component that uses only one special edge
    # (or the same 
    pass

def neighbours(grid, i, j, all_cells=False):
    res = []
    for (xoff, yoff) in [(0,1), (1,0), (0, -1), (-1, 0)]:
        i_ = i + yoff
        j_ = j + xoff
        if 0 <= i_ < len(grid):
            if 0 <= j_ < len(grid[i]):
                if all_cells or grid[i_][j_]:
                    res.append((i_,j_))
    return res

test = [[1,0,1,0],
        [1,0,0,1],
        [0,1,1,1],
        [0,0,1,0]]

n = 5
m = 6
t = 0.5
test = [[0] * m for _ in range(n)]
for i in range(n):
    for j in range(m):
        r = random.uniform(0,1)
        if r < t:
            test[i][j] = 1

test = [[0,0,0,0,0,0,0],[0,1,1,1,1,0,0],[0,1,0,0,1,0,0],[1,0,1,0,1,0,0],[0,1,0,0,1,0,0],[0,1,0,0,1,0,0],[0,1,1,1,1,0,0]]
for t in test:
    print(t)
print()

# for i in range (len(test)):
#     for j in range(len(test[i])):
#         print(i,j, neighbours(test, i,j))

# class cell():
#     def __init__(self, coords, neighbours) -> None:
#         self.coords = coords
#         self.neighbours = neighbours
#         self.visited = False

components = [[-1] * len(row) for row in test]
sizes = []
component_id = 0
# iterate over each cell and color it with the id of it's component
for i in range (len(test)):
    for j in range(len(test[i])):
        # skip if the cell is off or if it has already been colored
        if not test[i][j] or components[i][j] >= 0:
            continue
        # begin evaluating a component
        size = 0
        components[i][j] = component_id
        # cells to be evaluated in the future
        stack = [(i,j)]
        while stack:
            # pop the cell and color it
            (i_, j_) = stack.pop()
            size += 1
            # get it's adjacent components
            adj = neighbours(test, i_, j_)
            for (i__, j__) in adj:
                if components[i__][j__] < 0:
                    components[i__][j__] = component_id
                    stack.append((i__, j__))
        # we have finished coloring a component so increase the id
        component_id += 1
        sizes.append(size)

for r in components:
    print(r)
print()
print(sizes)
print()


best = sizes[0]
best_flip = None
for i in range (len(test)):
    for j in range(len(test[i])):
        if test[i][j]:
            continue
        adj = neighbours(test, i,j)
        adj_components = set()
        for (i_, j_) in adj:
            adj_components.add(components[i_][j_])
        adj_components = list(adj_components)
        adj_sizes = sorted([sizes[c] for c in adj_components], reverse=True)
        best_adj = adj_sizes[:2]
        size = 1 + sum(adj_sizes)
        if size > best:
            best = size
            best_flip = (i,j)
        #print(i, j, adj_components, adj_sizes[:2])
print(best, best_flip)


# bcab
# ideally we want to skip the b for now, because it occurs later in the string and isn't the lowest letter
# but if we skip then we have to take c next as it is solo
# so the result is cab
# which is worse than bca, which is what we get by taking the b first

# consider the b

# remdup(str) = str[0] + remdup(str[1:]) | remdup(str[1:]
# remdup([]) = []
