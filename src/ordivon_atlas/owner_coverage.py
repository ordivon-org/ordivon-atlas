from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable

from .atlas import SourceSpec


class CoverageDisposition(StrEnum):
    OWNER_CANDIDATE = "OWNER_CANDIDATE"
    OWNER_RECOGNIZED_NO_PUBLICATION = "OWNER_RECOGNIZED_NO_PUBLICATION"
    PUBLICATION_READY = "PUBLICATION_READY"
    ADMISSION_DEFERRED = "ADMISSION_DEFERRED"
    NON_OWNER = "NON_OWNER"
    SPECIAL_REVIEW = "SPECIAL_REVIEW"


@dataclass(frozen=True)
class DiscoveryRoot:
    path: str
    namePrefixes: list[str] | None = None
    names: list[str] | None = None
    excludeNames: list[str] | None = None


@dataclass(frozen=True)
class FrontierEntry:
    subjectRef: str
    displayName: str
    repo: str
    disposition: str
    reason: str
    coverageScope: str | None = None
    ownerResearchRef: str | None = None
    authorityRef: str | None = None
    corpusRootCandidate: str | None = None
    evidenceRefs: list[str] | None = None
    reconsiderationTriggers: list[str] | None = None


@dataclass(frozen=True)
class CoverageConfig:
    discoveryRoots: list[DiscoveryRoot]
    entries: list[FrontierEntry]


class OwnerCoverageError(ValueError):
    pass


def _canonical(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


def load_coverage_config(path: str | Path) -> CoverageConfig:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("kind") != "ordivon.atlas-owner-coverage-frontier":
        raise OwnerCoverageError("unsupported Atlas owner coverage frontier")
    if data.get("truthRole") != "non-authoritative-owner-coverage-ledger":
        raise OwnerCoverageError("owner coverage frontier must remain non-authoritative")
    roots = [DiscoveryRoot(**row) for row in data.get("discoveryRoots", [])]
    entries = [FrontierEntry(**row) for row in data.get("entries", [])]
    return CoverageConfig(discoveryRoots=roots, entries=entries)


def _validate_frontier(sources: Iterable[SourceSpec], config: CoverageConfig) -> list[str]:
    errors: list[str] = []
    source_list = list(sources)
    registered_repos = {_canonical(source.repo) for source in source_list}
    registered_owners = {source.ownerResearchRef for source in source_list}
    seen_subjects: set[str] = set()
    seen_repos: set[str] = set()
    seen_owners: set[str] = set()

    allowed = {item.value for item in CoverageDisposition}
    for entry in config.entries:
        repo = _canonical(entry.repo)
        if entry.subjectRef in seen_subjects:
            errors.append(f"DUPLICATE_SUBJECT_REF:{entry.subjectRef}")
        seen_subjects.add(entry.subjectRef)
        if repo in seen_repos:
            errors.append(f"DUPLICATE_FRONTIER_REPO:{repo}")
        seen_repos.add(repo)
        if repo in registered_repos:
            errors.append(f"FRONTIER_DUPLICATES_REGISTERED_REPO:{repo}")
        if entry.disposition not in allowed:
            errors.append(f"UNKNOWN_DISPOSITION:{entry.subjectRef}:{entry.disposition}")
        if entry.ownerResearchRef:
            if entry.ownerResearchRef in registered_owners:
                errors.append(f"FRONTIER_DUPLICATES_REGISTERED_OWNER:{entry.ownerResearchRef}")
            if entry.ownerResearchRef in seen_owners:
                errors.append(f"DUPLICATE_FRONTIER_OWNER:{entry.ownerResearchRef}")
            seen_owners.add(entry.ownerResearchRef)
        if entry.disposition == CoverageDisposition.ADMISSION_DEFERRED and not entry.reconsiderationTriggers:
            errors.append(f"DEFERRED_WITHOUT_RECONSIDERATION_TRIGGER:{entry.subjectRef}")
        if entry.disposition in {
            CoverageDisposition.OWNER_RECOGNIZED_NO_PUBLICATION,
            CoverageDisposition.PUBLICATION_READY,
        } and not entry.ownerResearchRef:
            errors.append(f"OWNER_STATE_WITHOUT_OWNER_REF:{entry.subjectRef}")
        if not entry.reason.strip():
            errors.append(f"MISSING_REASON:{entry.subjectRef}")
    return errors


def discover_repositories(roots: Iterable[DiscoveryRoot]) -> list[str]:
    discovered: set[str] = set()
    for spec in roots:
        root = Path(spec.path).expanduser()
        if not root.exists() or not root.is_dir():
            continue
        excluded = set(spec.excludeNames or [])
        explicit_names = set(spec.names or [])
        prefixes = tuple(spec.namePrefixes or [])
        candidates = [root / name for name in sorted(explicit_names)] if explicit_names else sorted(root.iterdir())
        for candidate in candidates:
            if candidate.name in excluded or not candidate.is_dir():
                continue
            if not explicit_names and prefixes and not candidate.name.startswith(prefixes):
                continue
            if (candidate / ".git").exists():
                discovered.add(_canonical(candidate))
    return sorted(discovered)


def _publication_probe(entry: FrontierEntry) -> dict[str, Any]:
    root = Path(entry.repo)
    corpus_root = entry.corpusRootCandidate or ""
    current = root / corpus_root / "authority" / "CURRENT.json"
    return {
        "candidateCurrentPath": str(current),
        "candidateCurrentExists": current.is_file(),
        "candidateCurrentProbeTruthRole": "local-working-tree-presence-only-not-source-fenced-authority",
    }


def build_owner_coverage(sources: Iterable[SourceSpec], config: CoverageConfig) -> dict[str, Any]:
    source_list = list(sources)
    errors = _validate_frontier(source_list, config)
    registered_repos = {_canonical(source.repo): source for source in source_list}
    frontier_repos = {_canonical(entry.repo): entry for entry in config.entries}
    unavailable_roots = [
        _canonical(spec.path)
        for spec in config.discoveryRoots
        if not Path(spec.path).expanduser().is_dir()
    ]
    discovered = discover_repositories(config.discoveryRoots)

    rows: list[dict[str, Any]] = []
    for source in sorted(source_list, key=lambda item: item.ownerResearchRef):
        rows.append({
            "subjectRef": source.ownerResearchRef,
            "displayName": source.ownerResearchRef.removeprefix("research-owner:"),
            "repo": _canonical(source.repo),
            "coverageScope": "RESEARCH_AUTHORITY",
            "coverageDisposition": "REGISTERED_RESEARCH_OWNER",
            "ownerResearchRef": source.ownerResearchRef,
            "authorityRef": source.authorityRef,
            "truthRole": "registered-research-owner-source-reference-not-owner-truth",
        })

    reconciliation: list[dict[str, Any]] = []
    for entry in sorted(config.entries, key=lambda item: item.subjectRef):
        probe = _publication_probe(entry)
        row = {
            **asdict(entry),
            "repo": _canonical(entry.repo),
            "coverageDisposition": entry.disposition,
            "truthRole": "non-authoritative-owner-coverage-classification",
            "repoPresent": Path(entry.repo).is_dir(),
            **probe,
        }
        row.pop("disposition", None)
        rows.append(row)
        if entry.disposition not in {CoverageDisposition.NON_OWNER}:
            reconciliation.append({
                "subjectRef": entry.subjectRef,
                "coverageScope": entry.coverageScope,
                "coverageDisposition": entry.disposition,
                "reason": entry.reason,
                "reconsiderationTriggers": entry.reconsiderationTriggers or [],
                **probe,
            })

    classified_repos = set(registered_repos) | set(frontier_repos)
    unclassified = [repo for repo in discovered if repo not in classified_repos]
    for repo in unclassified:
        reconciliation.append({
            "subjectRef": f"unclassified-repo:{Path(repo).name}",
            "coverageDisposition": "UNCLASSIFIED_REPOSITORY",
            "repo": repo,
            "reason": "Discovered repository is neither an admitted Atlas research-owner source nor explicitly classified in the owner coverage frontier.",
            "reconsiderationTriggers": ["classify owner responsibility before allowing the repository to disappear from institutional discovery"],
        })

    ready_but_unregistered = [
        row for row in rows
        if row.get("coverageDisposition") != "REGISTERED_RESEARCH_OWNER" and row.get("candidateCurrentExists")
    ]
    disposition_counts: dict[str, int] = {}
    for row in rows:
        disposition = str(row["coverageDisposition"])
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1

    classification_complete = not unclassified and not errors and not unavailable_roots
    return {
        "schemaVersion": 1,
        "kind": "ordivon.atlas-owner-coverage-projection",
        "truthRole": "non-authoritative-owner-coverage-projection",
        "coverageRows": rows,
        "reconciliationFrontier": reconciliation,
        "discoveredRepositories": discovered,
        "unavailableDiscoveryRoots": unavailable_roots,
        "unclassifiedRepositories": unclassified,
        "configurationErrors": errors,
        "summary": {
            "registeredResearchOwners": len(source_list),
            "frontierEntries": len(config.entries),
            "discoveredRepositories": len(discovered),
            "unavailableDiscoveryRoots": len(unavailable_roots),
            "unclassifiedRepositories": len(unclassified),
            "reconciliationRequired": len(reconciliation),
            "publicationSurfacePresentButUnregistered": len(ready_but_unregistered),
            "dispositionCounts": dict(sorted(disposition_counts.items())),
            "coverageClassificationComplete": classification_complete,
            "researchOwnerAdmissionComplete": not reconciliation and not errors and not unavailable_roots,
        },
    }


def write_owner_coverage(
    sources: Iterable[SourceSpec], config: CoverageConfig, out_dir: str | Path
) -> dict[str, Any]:
    projection = build_owner_coverage(sources, config)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "owner-coverage.json"
    temp = out / ".owner-coverage.json.tmp"
    temp.write_text(
        json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temp.replace(target)
    return projection
