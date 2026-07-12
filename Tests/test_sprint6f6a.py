"""
BursaAI v6.0 Sprint 6F.6A Parameter Space test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from WalkForward.parameter_generator import (
    ParameterGenerator,
)
from WalkForward.parameter_services import (
    register_parameter_generator,
)
from WalkForward.parameter_space import (
    ParameterSpace,
)
from WalkForward.parameter_templates import (
    build_default_trading_parameter_space,
)


def main():
    space = ParameterSpace()

    space.add(
        "fast",
        [5, 10, 20],
        validator=lambda value: value > 0,
    )

    space.add(
        "slow",
        [30, 50],
        validator=lambda value: value > 0,
    )

    space.add(
        "rsi",
        [7, 14],
        validator=lambda value: value > 0,
    )

    space.add_constraint(
        lambda parameters: (
            parameters["fast"]
            < parameters["slow"]
        )
    )

    combinations = space.combinations()

    assert len(combinations) == 12
    assert space.size() == 12
    assert all(
        parameters["fast"]
        < parameters["slow"]
        for parameters in combinations
    )

    generator = ParameterGenerator(
        parameter_space=space,
        random_seed=42,
    )

    grid = generator.generate_grid()

    assert len(grid) == 12
    assert grid[0].parameter_id == 1
    assert grid[0].source == "GRID"

    random_one = generator.generate_random(
        4
    )

    random_two = generator.generate_random(
        4
    )

    assert len(random_one) == 4
    assert len(random_two) == 4

    assert [
        item.parameters
        for item in random_one
    ] == [
        item.parameters
        for item in random_two
    ]

    assert len({
        tuple(sorted(item.parameters.items()))
        for item in random_one
    }) == 4

    default_space = (
        build_default_trading_parameter_space()
    )

    assert default_space.size() > 0

    assert all(
        parameters["ema_fast"]
        < parameters["ema_slow"]
        for parameters in default_space.combinations()
    )

    infrastructure = build_infrastructure()

    registered = register_parameter_generator(
        infrastructure.services,
        parameter_space=space,
        random_seed=42,
    )

    assert (
        infrastructure.services.resolve(
            "optimization_parameter_generator"
        )
        is registered
    )

    assert (
        infrastructure.services.resolve(
            "optimization_parameter_space"
        )
        is space
    )

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6F.6A TEST")
    print("=" * 92)
    print("Parameter Definition      : OK")
    print("Parameter Space           : OK")
    print("Parameter Validation      : OK")
    print("Constraint Validation     : OK")
    print("Grid Generation           : OK")
    print("Random Generation         : OK")
    print("Reproducible Seed         : OK")
    print("Unique Random Sets        : OK")
    print("Default Trading Template  : OK")
    print("Service Registration      : OK")
    print("=" * 92)
    print("SPRINT 6F.6A PARAMETER SPACE & GENERATOR OK")


if __name__ == "__main__":
    main()
