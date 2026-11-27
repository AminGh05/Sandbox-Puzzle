"""Genetic search over fixed-length action sequences for the sand drawer puzzle.

Each chromosome is replayed from the supplied initial state. ``None`` marks the
end of a shorter effective sequence; a goal reached during replay ends it early.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List, NamedTuple, Optional, Sequence, Tuple

from environment import Action, State, get_successors


class Gene(NamedTuple):
    """Stable action identity, independent of the action's display text."""

    type: str
    col: Optional[int]
    index: int


Chromosome = List[Optional[Gene]]
STOP = None


@dataclass
class SequenceEvaluation:
    successful: bool
    fitness: float
    path_cost: float
    best_conflict: float
    best_prefix_length: int
    actions: List[Action]
    final_state: State


@dataclass
class GeneticResult:
    solution: Optional[List[Action]]
    cost: Optional[float]
    generations: int
    best_fitness: float
    best_conflict: float
    history: List[float]


def _gene(action: Action) -> Gene:
    return Gene(action.type, action.col, action.index)


def conflict_number(state: State) -> float:
    """Count occupied cells and open internal gates; zero exactly at the goal."""
    occupied_cells = sum(value > 0.0 for value in state.col0 + state.col1)
    open_gates = sum(state.gates0) + sum(state.gates1)
    return float(occupied_cells + open_gates)


def evaluate_sequence(
    initial: State,
    chromosome: Sequence[Optional[Gene]],
    success_bonus: float = 1000.0,
    cost_weight: float = 0.01,
) -> SequenceEvaluation:
    """Replay and score one sequence; illegal actions receive fitness zero."""
    state = initial
    actions: List[Action] = []
    path_cost = 0.0
    best_conflict = conflict_number(state)
    best_prefix_length = 0

    if state.is_goal():
        return SequenceEvaluation(True, success_bonus, 0.0, 0.0, 0, actions, state)

    for gene in chromosome:
        if gene is STOP:
            break

        transitions = get_successors(state)
        transition = next((item for item in transitions if _gene(item[0]) == gene), None)
        if transition is None:
            return SequenceEvaluation(False, 0.0, path_cost, best_conflict,
                                      best_prefix_length, actions, state)

        action, next_state, action_cost = transition
        actions.append(action)
        path_cost += action_cost
        state = next_state
        conflict = conflict_number(state)
        if conflict < best_conflict:
            best_conflict = conflict
            best_prefix_length = len(actions)
        if state.is_goal():
            # The suffix is deliberately ignored once the goal is reached.
            fitness = success_bonus + 1.0 / (1.0 + path_cost)
            return SequenceEvaluation(True, fitness, path_cost, 0.0,
                                      len(actions), actions, state)

    # Positive score, with a stronger preference for lower conflict and then cost.
    fitness = 1.0 / (1.0 + best_conflict + cost_weight * path_cost)
    return SequenceEvaluation(False, fitness, path_cost, best_conflict,
                              best_prefix_length, actions, state)


def successful_path(initial: State, chromosome: Sequence[Optional[Gene]]) -> bool:
    """Sequence-based goal test: does replay reach a goal before it ends?"""
    # Keep this predicate separate from State.is_goal(), which tests a board.
    if initial.is_goal():
        return True
    state = initial
    for gene in chromosome:
        if gene is STOP:
            return False
        transition = next((item for item in get_successors(state)
                           if _gene(item[0]) == gene), None)
        if transition is None:
            return False
        state = transition[1]
        if state.is_goal():
            return True
    return state.is_goal()


def _random_chromosome(initial: State, length: int, rng: random.Random) -> Chromosome:
    """Build a legal random walk and pad it to the configured chromosome length."""
    genes: Chromosome = []
    state = initial
    for _ in range(length):
        if state.is_goal():
            genes.append(STOP)
            continue
        successors = get_successors(state)
        if not successors:
            genes.append(STOP)
            continue
        action, state, _ = rng.choice(successors)
        genes.append(_gene(action))
    return genes


def _select(population: Sequence[Chromosome], evaluations: Sequence[SequenceEvaluation],
            count: int, rng: random.Random) -> List[Chromosome]:
    """Fitness-proportionate roulette selection with replacement."""
    weights = [max(0.0, evaluation.fitness) for evaluation in evaluations]
    if not any(weights):
        return [list(rng.choice(population)) for _ in range(count)]
    return [list(item) for item in rng.choices(population, weights=weights, k=count)]


def _crossover(first: Chromosome, second: Chromosome, rng: random.Random,
               two_point: bool = False) -> Tuple[Chromosome, Chromosome]:
    """Single-point (default) or two-point crossover, returning two children."""
    size = len(first)
    if size < 2:
        return list(first), list(second)
    if two_point and size >= 3:
        left, right = sorted(rng.sample(range(size + 1), 2))
        child1 = first[:left] + second[left:right] + first[right:]
        child2 = second[:left] + first[left:right] + second[right:]
    else:
        point = rng.randrange(1, size)
        child1 = first[:point] + second[point:]
        child2 = second[:point] + first[point:]
    return child1, child2


def _mutate(chromosome: Chromosome, initial: State, rng: random.Random,
            mutation_rate: float) -> Chromosome:
    """Randomly replace one or a few genes with actions legal at that prefix."""
    child = list(chromosome)
    positions = [i for i, gene in enumerate(child) if gene is not STOP]
    if not positions:
        positions = list(range(len(child)))
    if not positions or rng.random() >= mutation_rate:
        return child

    # Usually one gene changes; occasionally a second independently changes.
    mutation_count = 2 if len(positions) > 1 and rng.random() < 0.15 else 1
    for position in rng.sample(positions, min(mutation_count, len(positions))):
        state = initial
        valid_prefix = True
        for gene in child[:position]:
            if gene is STOP:
                valid_prefix = False
                break
            transition = next((t for t in get_successors(state) if _gene(t[0]) == gene), None)
            if transition is None:
                valid_prefix = False
                break
            state = transition[1]
            if state.is_goal():
                valid_prefix = False
                break
        if not valid_prefix:
            # A crossover may have made an earlier gene illegal; replace the
            # chosen suffix position with a legal action after a fresh prefix.
            continue
        choices = get_successors(state)
        if choices:
            child[position] = _gene(rng.choice(choices)[0])
    return child


def genetic_search(
    initial: State,
    population_size: int = 60,
    sequence_length: int = 30,
    generations: int = 200,
    mutation_rate: float = 0.12,
    success_bonus: float = 1000.0,
    cost_weight: float = 0.01,
    seed: Optional[int] = None,
    two_point_crossover: bool = False,
    elite_count: int = 2,
) -> GeneticResult:
    """Search for a successful action sequence using a genetic algorithm."""
    if population_size < 2 or population_size % 2:
        raise ValueError("population_size must be an even integer of at least 2")
    if sequence_length < 1:
        raise ValueError("sequence_length must be positive")
    if generations < 0:
        raise ValueError("generations cannot be negative")
    if not 0.0 <= mutation_rate <= 1.0:
        raise ValueError("mutation_rate must be between 0 and 1")
    if success_bonus <= 1.0:
        raise ValueError("success_bonus must exceed all unsuccessful fitness values")

    rng = random.Random(seed)
    population = [_random_chromosome(initial, sequence_length, rng)
                  for _ in range(population_size)]
    best_eval: Optional[SequenceEvaluation] = None
    best_fitness = -1.0
    history: List[float] = []
    completed_generations = 0

    for generation in range(generations + 1):
        evaluations = [evaluate_sequence(initial, chromosome, success_bonus, cost_weight)
                       for chromosome in population]
        top_index = max(range(len(population)), key=lambda i: evaluations[i].fitness)
        generation_best = evaluations[top_index]
        if generation_best.fitness > best_fitness:
            best_fitness = generation_best.fitness
            best_eval = generation_best
        history.append(generation_best.fitness)
        completed_generations = generation

        if generation == generations:
            break

        elites_n = min(max(0, elite_count), population_size - 2)
        if elites_n % 2:
            elites_n -= 1
        elite_indices = sorted(range(population_size),
                               key=lambda i: evaluations[i].fitness, reverse=True)[:elites_n]
        next_population = [list(population[i]) for i in elite_indices]
        parents = _select(population, evaluations, population_size - elites_n, rng)
        for i in range(0, len(parents) - 1, 2):
            children = _crossover(parents[i], parents[i + 1], rng, two_point_crossover)
            next_population.append(_mutate(children[0], initial, rng, mutation_rate))
            next_population.append(_mutate(children[1], initial, rng, mutation_rate))
        # The requested even population size remains fixed, including with elites.
        population = next_population[:population_size]

    assert best_eval is not None
    return GeneticResult(
        solution=best_eval.actions if best_eval.successful else None,
        cost=best_eval.path_cost if best_eval.successful else None,
        generations=completed_generations,
        best_fitness=best_eval.fitness,
        best_conflict=best_eval.best_conflict,
        history=history,
    )

