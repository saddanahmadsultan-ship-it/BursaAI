from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

from Research.ranking_models import RankedStrategy
from Research.pareto_models import ParetoPoint


class ParetoEngine:
    """
    Non-dominated sorting untuk strategi research.

    Objektif default semuanya dimaksimumkan:
    - performance_score
    - risk_score
    - consistency_score
    - robustness_score
    - confidence_score
    """

    DEFAULT_OBJECTIVES = (
        "performance_score",
        "risk_score",
        "consistency_score",
        "robustness_score",
        "confidence_score",
    )

    def rank(
        self,
        strategies: Iterable[RankedStrategy],
        objectives: Sequence[str] | None = None,
    ) -> List[ParetoPoint]:
        items = list(strategies)
        objective_names = tuple(objectives or self.DEFAULT_OBJECTIVES)

        dominates: Dict[str, List[str]] = defaultdict(list)
        domination_count: Dict[str, int] = {
            item.candidate_id: 0 for item in items
        }

        by_id = {item.candidate_id: item for item in items}

        for left in items:
            for right in items:
                if left.candidate_id == right.candidate_id:
                    continue

                if self._dominates(left, right, objective_names):
                    dominates[left.candidate_id].append(
                        right.candidate_id
                    )
                elif self._dominates(right, left, objective_names):
                    domination_count[left.candidate_id] += 1

        fronts: List[List[str]] = []

        current_front = [
            candidate_id
            for candidate_id, count in domination_count.items()
            if count == 0
        ]

        while current_front:
            fronts.append(current_front)
            next_front: List[str] = []

            for candidate_id in current_front:
                for dominated_id in dominates[candidate_id]:
                    domination_count[dominated_id] -= 1

                    if domination_count[dominated_id] == 0:
                        next_front.append(dominated_id)

            current_front = next_front

        result: List[ParetoPoint] = []

        for front_index, front_ids in enumerate(fronts, start=1):
            crowding = self._crowding_distance(
                [by_id[candidate_id] for candidate_id in front_ids],
                objective_names,
            )

            for candidate_id in front_ids:
                item = by_id[candidate_id]

                result.append(
                    ParetoPoint(
                        candidate_id=item.candidate_id,
                        result_id=item.result_id,
                        front=front_index,
                        domination_count=sum(
                            1
                            for other in items
                            if self._dominates(
                                other,
                                item,
                                objective_names,
                            )
                        ),
                        dominates_count=len(
                            dominates[item.candidate_id]
                        ),
                        crowding_distance=crowding.get(
                            item.candidate_id,
                            0.0,
                        ),
                        objectives={
                            name: float(
                                getattr(
                                    item.breakdown,
                                    name,
                                )
                            )
                            for name in objective_names
                        },
                    )
                )

        result.sort(
            key=lambda point: (
                point.front,
                -point.crowding_distance,
                -point.dominates_count,
            )
        )

        return result

    @staticmethod
    def _dominates(
        left: RankedStrategy,
        right: RankedStrategy,
        objectives: Sequence[str],
    ) -> bool:
        left_values = [
            float(getattr(left.breakdown, name))
            for name in objectives
        ]

        right_values = [
            float(getattr(right.breakdown, name))
            for name in objectives
        ]

        no_worse = all(
            left_value >= right_value
            for left_value, right_value in zip(
                left_values,
                right_values,
            )
        )

        strictly_better = any(
            left_value > right_value
            for left_value, right_value in zip(
                left_values,
                right_values,
            )
        )

        return no_worse and strictly_better

    @staticmethod
    def _crowding_distance(
        front: List[RankedStrategy],
        objectives: Sequence[str],
    ) -> Dict[str, float]:
        if not front:
            return {}

        if len(front) <= 2:
            return {
                item.candidate_id: float("inf")
                for item in front
            }

        distances = {
            item.candidate_id: 0.0
            for item in front
        }

        for objective in objectives:
            ordered = sorted(
                front,
                key=lambda item: float(
                    getattr(item.breakdown, objective)
                ),
            )

            minimum = float(
                getattr(
                    ordered[0].breakdown,
                    objective,
                )
            )

            maximum = float(
                getattr(
                    ordered[-1].breakdown,
                    objective,
                )
            )

            distances[ordered[0].candidate_id] = float("inf")
            distances[ordered[-1].candidate_id] = float("inf")

            if maximum == minimum:
                continue

            for index in range(1, len(ordered) - 1):
                previous_value = float(
                    getattr(
                        ordered[index - 1].breakdown,
                        objective,
                    )
                )

                next_value = float(
                    getattr(
                        ordered[index + 1].breakdown,
                        objective,
                    )
                )

                distances[
                    ordered[index].candidate_id
                ] += (
                    next_value - previous_value
                ) / (
                    maximum - minimum
                )

        return distances
