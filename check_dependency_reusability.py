#!/usr/bin/env python3
"""
check_dependency_reusability.py

Uses the Spack Python API to determine whether the dependencies present in a
preexisting container Spack environment satisfy the constraints required by this
CI run, so that explicit reconcretization can be skipped.

Checks only the *dependencies* of the packages under test (main package and any
dependents-to-test), not the packages themselves -- those will always be built
fresh via `spack develop` / root install. If every dependency in the preexisting
container environment satisfies dependency constraints implied by the requested
root specs (including package-name@package-version and package-variants), those
dependencies can be reused and explicit reconcretization can be skipped.

Constraints checked against dependencies (roots excluded):
    - Dependency constraints inferred from concretized requested root specs
    - Explicit ^dep constraints embedded in package-variants (e.g. ^cmake@3.20)
    - Presence of required dependencies in the preexisting environment

Returns 0 if all dependencies can be reused, 1 otherwise.
"""

import argparse
import sys

import spack.concretize as spack_concretize
import spack.environment as ev
import spack.spec as sp


def dependent_spec_requires_concretization(spec_str):
    """Return True when a dependent spec string carries explicit constraints."""
    # Plain package names (e.g. "w3emc") need no solver pass here.
    # Concretize only when users provide extra constraints on that dependent.
    constraint_tokens = ("@", "+", "~", "^", "%")
    return any(tok in spec_str for tok in constraint_tokens)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Check whether preexisting container Spack dependencies satisfy CI requirements."
        )
    )
    parser.add_argument("--env-path", required=True,
                        help="Path to preexisting container Spack environment")
    parser.add_argument("--package-name", required=True,
                        help="Name of the Spack package being tested")
    parser.add_argument("--package-version", required=True,
                        help="Version of the package being tested")
    parser.add_argument("--package-variants", default="",
                        help="Variants to apply to the package spec")
    parser.add_argument("--dependents-to-test", default="",
                        help="Space-delimited list of dependent specs to also test")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load the preexisting container environment and its lock file
    env = ev.Environment(args.env_path)
    with env:
        env._read()

        # Root spec names to locate in the environment:
        # the main package plus each dependent under test
        root_names = {args.package_name}
        for raw in (args.dependents_to_test or "").split():
            root_names.add(sp.Spec(raw).name)

        # Build requested root specs for concretization-based dependency checks.
        requested_root_specs = []
        main_root_spec = f"{args.package_name}@{args.package_version}"
        if args.package_variants.strip():
            main_root_spec += f" {args.package_variants.strip()}"
        requested_root_specs.append((main_root_spec, True))
        for dep_root_spec in (args.dependents_to_test or "").split():
            requested_root_specs.append(
                (dep_root_spec, dependent_spec_requires_concretization(dep_root_spec))
            )

        # Build per-dependency constraints from concretized root specs.
        # If the same dependency appears in multiple requested roots, require the
        # preexisting environment dependency to satisfy all seen constraints.
        required_dep_constraints = {}
        for root_spec_str, should_concretize in requested_root_specs:
            if not should_concretize:
                print(
                    f"Skipping concretization for unconstrained dependent root '{root_spec_str}'",
                    file=sys.stderr,
                )
                continue

            requested_root = sp.Spec(root_spec_str)
            try:
                requested_root = spack_concretize.concretize_one(requested_root)
            except Exception as exc:
                print(
                    f"Failed to concretize requested spec '{root_spec_str}': {exc}",
                    file=sys.stderr,
                )
                sys.exit(1)

            for dep_spec in requested_root.traverse(root=False):
                required_dep_constraints.setdefault(dep_spec.name, []).append(dep_spec)

        # Find the locked root specs in the preexisting container environment so we can
        # traverse their dependency graphs
        targets = [s for s in env.all_specs() if s.name in root_names]

        missing = root_names - {t.name for t in targets}
        if missing:
            print(
                f"Specs not found in preexisting container environment: {missing}",
                file=sys.stderr,
            )
            sys.exit(1)

        conflicts_found = False
        available_dep_names = set()
        for root in targets:
            print(f"\n=== {root.name} dependencies ===")
            for dep in root.traverse(root=False):
                # Skip other root packages (dependents-to-test); they will also
                # be built fresh and should not be checked here
                if dep.name in root_names:
                    continue

                available_dep_names.add(dep.name)

                for constraint in required_dep_constraints.get(dep.name, []):
                    if not dep.satisfies(constraint):
                        print(
                            f"  CONFLICT: {dep} does not satisfy required dependency constraint {constraint}",
                            file=sys.stderr,
                        )
                        conflicts_found = True
            print("======")

        # Roots are intentionally excluded from dependency reuse checks because
        # they are rebuilt as requested specs. Exclude them from "missing deps"
        # accounting to avoid false positives (e.g. a dependent root requiring
        # another root).
        required_dep_names = set(required_dep_constraints.keys()) - root_names
        missing_required_deps = required_dep_names - available_dep_names
        if missing_required_deps:
            print(
                "Missing required dependencies in preexisting container environment: "
                f"{sorted(missing_required_deps)}",
                file=sys.stderr,
            )
            conflicts_found = True

    if conflicts_found:
        sys.exit(1)

    print(
        "All dependencies satisfy requested root-spec dependency constraints; "
        "preexisting container environment can be reused without reconcretization."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
