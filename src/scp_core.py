class SCPInstance:
    def __init__(self):
        self.m = 0
        self.n = 0
        self.cost = []
        self.row_cols = []
        self.col_rows = []

    def load_from_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                tokens = f.read().split()
        except OSError:
            return False

        if len(tokens) < 2:
            return False

        it = iter(tokens)
        self.m = int(next(it))
        self.n = int(next(it))

        self.cost = [0] * (self.n + 1)
        self.row_cols = [[] for _ in range(self.m + 1)]
        self.col_rows = [set() for _ in range(self.n + 1)]

        for j in range(1, self.n + 1):
            self.cost[j] = int(next(it))

        for i in range(1, self.m + 1):
            k = int(next(it))
            for _ in range(k):
                col = int(next(it))
                if 1 <= col <= self.n:
                    self.row_cols[i].append(col)
                    self.col_rows[col].add(i)

        return True


def save_solution(out_file: str, total_cost: int, selected_cols: list[int]):
    unique_cols = sorted(set(selected_cols))
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"{total_cost}\n")
        f.write(" ".join(map(str, unique_cols)) + "\n")