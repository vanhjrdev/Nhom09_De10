import math
import random
import sys
import time
from dataclasses import dataclass

from scp_core import SCPInstance, save_solution


@dataclass
class Individual:
    chosen: list[bool]
    cover: list[int]
    cost: int = 0


class GeneticSolver:
    def __init__(
        self,
        instance: SCPInstance,
        seed: int,
        population_size: int,
        mutation_rate: float,
        hybrid: bool,
        budget_sec: float,
    ):
        self.instance = instance
        self.rng = random.Random(seed)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.hybrid = hybrid
        self.budget_sec = budget_sec
        self.start_time = 0.0
        self.evaluations = 0

    def elapsed(self) -> float:
        return time.perf_counter() - self.start_time

    def add(self, individual: Individual, column: int):
        individual.chosen[column] = True
        individual.cost += self.instance.cost[column]
        for row in self.instance.col_rows[column]:
            individual.cover[row] += 1

    def remove(self, individual: Individual, column: int):
        individual.chosen[column] = False
        individual.cost -= self.instance.cost[column]
        for row in self.instance.col_rows[column]:
            individual.cover[row] -= 1

    def prune(self, individual: Individual):
        selected = [
            column
            for column in range(1, self.instance.n + 1)
            if individual.chosen[column]
        ]
        self.rng.shuffle(selected)
        selected.sort(key=lambda column: self.instance.cost[column], reverse=True)

        for column in selected:
            if all(individual.cover[row] >= 2 for row in self.instance.col_rows[column]):
                self.remove(individual, column)

    def repair(self, individual: Individual):
        for row in range(1, self.instance.m + 1):
            if individual.cover[row] > 0:
                continue

            best_column = -1
            best_ratio = math.inf
            for column in self.instance.row_cols[row]:
                gain = sum(
                    1
                    for covered_row in self.instance.col_rows[column]
                    if individual.cover[covered_row] == 0
                )
                ratio = self.instance.cost[column] / gain
                if ratio < best_ratio or (
                    ratio == best_ratio and self.rng.getrandbits(1)
                ):
                    best_ratio = ratio
                    best_column = column

            if best_column < 0:
                raise ValueError("Hang khong duoc cot nao phu")
            self.add(individual, best_column)

        self.prune(individual)

    def from_bits(self, bits: list[bool]) -> Individual:
        individual = Individual(
            chosen=[False] * (self.instance.n + 1),
            cover=[0] * (self.instance.m + 1),
        )
        for column in range(1, self.instance.n + 1):
            if bits[column]:
                self.add(individual, column)
        self.repair(individual)
        self.evaluations += 1
        return individual

    def local_search(self, individual: Individual):
        selected = [
            column
            for column in range(1, self.instance.n + 1)
            if individual.chosen[column]
        ]
        self.rng.shuffle(selected)

        for old_column in selected:
            if self.elapsed() >= self.budget_sec:
                break

            unique_rows = [
                row
                for row in self.instance.col_rows[old_column]
                if individual.cover[row] == 1
            ]
            if not unique_rows:
                self.remove(individual, old_column)
                continue

            pivot = min(unique_rows, key=lambda row: len(self.instance.row_cols[row]))
            replacement = -1
            for column in self.instance.row_cols[pivot]:
                if (
                    individual.chosen[column]
                    or self.instance.cost[column] >= self.instance.cost[old_column]
                ):
                    continue
                if all(row in self.instance.col_rows[column] for row in unique_rows):
                    if (
                        replacement < 0
                        or self.instance.cost[column] < self.instance.cost[replacement]
                    ):
                        replacement = column

            if replacement >= 0:
                self.remove(individual, old_column)
                self.add(individual, replacement)

        self.prune(individual)

    def tournament(self, population: list[Individual]) -> Individual:
        candidates = [
            population[self.rng.randrange(self.population_size)] for _ in range(3)
        ]
        return min(candidates, key=lambda individual: individual.cost)

    def solve(self, log_path: str) -> Individual:
        self.start_time = time.perf_counter()
        population = []
        best = None

        with open(log_path, "w", encoding="utf-8", newline="") as log:
            log.write("time_s,iter,evals,best\n")

            def register_best(individual: Individual, generation: int):
                nonlocal best
                if best is None or individual.cost < best.cost:
                    best = Individual(
                        chosen=list(individual.chosen),
                        cover=list(individual.cover),
                        cost=individual.cost,
                    )
                    log.write(
                        f"{self.elapsed():.6f},{generation},"
                        f"{self.evaluations},{best.cost}\n"
                    )

            for index in range(self.population_size):
                bits = [False] * (self.instance.n + 1)
                if index > 0:
                    for column in range(1, self.instance.n + 1):
                        bits[column] = self.rng.random() < 0.25
                individual = self.from_bits(bits)
                if self.hybrid:
                    self.local_search(individual)
                register_best(individual, 0)
                population.append(individual)

            generation = 0
            while self.elapsed() < self.budget_sec:
                generation += 1
                next_population = [best]

                while (
                    len(next_population) < self.population_size
                    and self.elapsed() < self.budget_sec
                ):
                    parent_a = self.tournament(population)
                    parent_b = self.tournament(population)
                    bits = [False] * (self.instance.n + 1)
                    for column in range(1, self.instance.n + 1):
                        bits[column] = (
                            parent_a.chosen[column]
                            if self.rng.random() < 0.5
                            else parent_b.chosen[column]
                        )
                        if self.rng.random() < self.mutation_rate:
                            bits[column] = not bits[column]

                    child = self.from_bits(bits)
                    if self.hybrid:
                        self.local_search(child)
                    register_best(child, generation)
                    next_population.append(child)

                if len(next_population) == self.population_size:
                    population = next_population

        return best


def main():
    if not 4 <= len(sys.argv) <= 9:
        print(
            "Cach dung: python src/main_C.py <input_file> <GA|GA_LS> "
            "<output_sol> [seed] [budget_sec] [conv_csv] [population] "
            "[mutation_rate]"
        )
        sys.exit(1)

    try:
        input_file = sys.argv[1]
        algorithm = sys.argv[2].upper()
        output_file = sys.argv[3]
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else 42
        budget_sec = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
        log_file = sys.argv[6] if len(sys.argv) > 6 else "conv.csv"
        population_size = int(sys.argv[7]) if len(sys.argv) > 7 else 40

        if algorithm not in {"GA", "GA_LS"}:
            raise ValueError("Thuat toan phai la GA hoac GA_LS")

        instance = SCPInstance()
        if not instance.load_from_file(input_file):
            raise ValueError("Khong doc duoc tep dau vao")
        if instance.m <= 0 or instance.n <= 0:
            raise ValueError("Kich thuoc phai duong")
        if any(instance.cost[column] < 0 for column in range(1, instance.n + 1)):
            raise ValueError("Chi phi phai khong am")
        if any(not instance.row_cols[row] for row in range(1, instance.m + 1)):
            raise ValueError("Co hang khong duoc phu")

        mutation_rate = (
            float(sys.argv[8]) if len(sys.argv) > 8 else 1.0 / instance.n
        )
        if (
            not math.isfinite(budget_sec)
            or budget_sec <= 0
            or population_size < 2
            or not math.isfinite(mutation_rate)
            or not 0 <= mutation_rate <= 1
        ):
            raise ValueError("Tham so khong hop le")

        solver = GeneticSolver(
            instance,
            seed,
            population_size,
            mutation_rate,
            algorithm == "GA_LS",
            budget_sec,
        )
        start = time.perf_counter()
        best = solver.solve(log_file)
        elapsed = time.perf_counter() - start
        selected = [
            column
            for column in range(1, instance.n + 1)
            if best.chosen[column]
        ]
        save_solution(output_file, best.cost, selected)
        print(f"[{algorithm}] Cost: {best.cost} | Time: {elapsed:.4f}s")
    except (OSError, ValueError, StopIteration) as error:
        print(f"Loi: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
