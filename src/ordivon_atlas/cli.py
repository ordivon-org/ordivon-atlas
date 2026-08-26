from __future__ import annotations

import argparse
import json
from pathlib import Path

from .atlas import Atlas
from .first_look import (
    inspect_prior_result_candidate,
    prior_result_first_look,
    prior_result_first_look_many,
    retrieval_authoring_context,
    retrieval_coordinate_profile,
    retrieval_representation_profile,
)
from .owner_coverage import build_owner_coverage, load_coverage_config, write_owner_coverage


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ordivon-atlas")
    parser.add_argument("--registry", default="config/sources.json")
    parser.add_argument("--frontier", default="config/owner-frontier.json")
    sub = parser.add_subparsers(dest="command", required=True)
    refresh = sub.add_parser("refresh", help="resolve owner sources and regenerate Atlas views")
    refresh.add_argument("--out", default="generated")
    sub.add_parser("check", help="observe source currentness without writing views")
    sub.add_parser(
        "coverage-check",
        help="classify admitted, candidate, deferred and non-owner repositories without minting owner truth",
    )
    first_look = sub.add_parser("first-look", help="bounded non-authoritative prior-result candidate lookup")
    first_look.add_argument("query")
    first_look.add_argument("--out", default="generated")
    first_look.add_argument("--limit", type=int, default=8)
    first_look_many = sub.add_parser(
        "first-look-many", help="bounded caller-authored multi-variant prior-result lookup"
    )
    first_look_many.add_argument("queries", nargs="+")
    first_look_many.add_argument("--out", default="generated")
    first_look_many.add_argument("--limit", type=int, default=8)
    sub.add_parser(
        "retrieval-profile", help="mechanical Atlas retrieval-representation profile"
    )
    sub.add_parser(
        "retrieval-coordinates", help="task-neutral owner-curated retrieval-coordinate profile"
    )
    sub.add_parser(
        "retrieval-authoring-context",
        help="mechanical retrieval environment and coordinates for caller query authoring",
    )
    inspect_candidate = sub.add_parser(
        "inspect-candidate",
        help="read one exact bounded first-look candidate without inferring equivalence/admission",
    )
    inspect_candidate.add_argument("query")
    inspect_candidate.add_argument("path")
    inspect_candidate.add_argument("locator")
    inspect_candidate.add_argument("--out", default="generated")
    inspect_candidate.add_argument("--limit", type=int, default=8)
    inspect_candidate.add_argument("--max-projection-bytes", type=int, default=12_288)
    show = sub.add_parser("show", help="print one generated view")
    show.add_argument(
        "view",
        choices=["atlas", "owners", "coverage", "recovery", "results", "closure", "negative", "history", "health"],
    )
    show.add_argument("--out", default="generated")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "first-look":
        print(json.dumps(prior_result_first_look(args.query, repository_root=".", generated_dir=args.out, limit=args.limit), indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if args.command == "first-look-many":
        print(
            json.dumps(
                prior_result_first_look_many(
                    args.queries, repository_root=".", generated_dir=args.out, limit=args.limit
                ),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "retrieval-profile":
        print(
            json.dumps(
                retrieval_representation_profile(repository_root="."),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "retrieval-authoring-context":
        print(
            json.dumps(
                retrieval_authoring_context(repository_root="."),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "retrieval-coordinates":
        print(
            json.dumps(
                retrieval_coordinate_profile(repository_root="."),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "inspect-candidate":
        print(
            json.dumps(
                inspect_prior_result_candidate(
                    args.query,
                    args.path,
                    args.locator,
                    repository_root=".",
                    generated_dir=args.out,
                    limit=args.limit,
                    max_projection_bytes=args.max_projection_bytes,
                ),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return 0

    atlas = Atlas.from_registry(args.registry)
    if args.command == "coverage-check":
        coverage = build_owner_coverage(atlas.sources, load_coverage_config(args.frontier))
        print(json.dumps(coverage, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if coverage["summary"]["coverageClassificationComplete"] else 2
    if args.command == "check":
        print(json.dumps([row.public() for row in atlas.observe_all()], indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if args.command == "refresh":
        projection = atlas.write(args.out)
        coverage = write_owner_coverage(atlas.sources, load_coverage_config(args.frontier), args.out)
        unhealthy = [row for row in projection["projectionHealth"] if row["health"] != "CURRENT_TO_SOURCE"]
        print(
            json.dumps(
                {
                    "owners": len(projection["owners"]),
                    "unhealthy": len(unhealthy),
                    "fullyCurrent": not unhealthy,
                    "coverageClassificationComplete": coverage["summary"]["coverageClassificationComplete"],
                    "coverageUnclassified": coverage["summary"]["unclassifiedRepositories"],
                    "coverageReconciliationRequired": coverage["summary"]["reconciliationRequired"],
                    "snapshotUpdated": True,
                    "out": args.out,
                },
                sort_keys=True,
            )
        )
        return 0 if not unhealthy and coverage["summary"]["coverageClassificationComplete"] else 2

    names = {
        "atlas": "atlas.json",
        "owners": "owner-map.json",
        "coverage": "owner-coverage.json",
        "recovery": "current-recovery.json",
        "results": "results.json",
        "closure": "closure.json",
        "negative": "negative-history.json",
        "history": "history.json",
        "health": "projection-health.json",
    }
    path = Path(args.out) / names[args.view]
    print(path.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
