"""Bounded non-authoritative prior-result first-look for fresh research consumers.

Atlas may make prior-result candidates legible, but it does not decide semantic
equivalence, novelty, research admission, or owner truth. This experimental read
composition searches already-generated owner projections when present and the
Git-durable curated synthesis layer, then returns bounded candidates plus source
health. It performs no write and mints no new research standing.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


_GENERATED_FILES = (
    "results.json",
    "closure.json",
    "negative-history.json",
    "history.json",
    "owner-map.json",
    "current-recovery.json",
)
_CJK_RE = re.compile(r"[\u3400-\u9fff]+")
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9_.:/+\-]{1,}")
_MAX_INSPECT_BYTES = 65_536


def _terms(query: str) -> tuple[str, ...]:
    normalized = query.strip().lower()
    if not normalized:
        raise ValueError("first-look query must be non-empty")
    terms: set[str] = set(_WORD_RE.findall(normalized))
    for run in _CJK_RE.findall(normalized):
        terms.add(run)
        if len(run) >= 2:
            terms.update(run[index : index + 2] for index in range(len(run) - 1))
    terms = {term for term in terms if len(term.encode("utf-8")) >= 2}
    if not terms:
        terms.add(normalized)
    return tuple(sorted(terms))


def _matches(text: str, query_terms: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    lowered = text.lower()
    matched = tuple(term for term in query_terms if term in lowered)
    if not matched:
        return 0, ()
    score = sum(2 + min(lowered.count(term), 4) for term in matched)
    return score, matched


def _excerpt(text: str, matched: tuple[str, ...], *, limit: int = 420) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    lowered = compact.lower()
    positions = [lowered.find(term) for term in matched if lowered.find(term) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - limit // 3)
    end = min(len(compact), start + limit)
    value = compact[start:end]
    if start:
        value = "…" + value
    if end < len(compact):
        value += "…"
    return value


def _record_locator(path: tuple[str, ...]) -> str:
    return "/".join(path) if path else "$"


def _records(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from _records(item, path + (str(index),))
        return
    if isinstance(value, dict):
        scalar = {
            key: item
            for key, item in value.items()
            if item is None or isinstance(item, (str, int, float, bool))
        }
        if scalar:
            yield path, value
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                yield from _records(item, path + (str(key),))
        return


def _candidate(
    *,
    source_class: str,
    truth_role: str,
    path: str,
    locator: str,
    text: str,
    query_terms: tuple[str, ...],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    score, matched = _matches(text, query_terms)
    path_score, path_matched = _matches(path, query_terms)
    if score == 0 and path_score == 0:
        return None
    all_matched = tuple(sorted(set(matched) | set(path_matched)))
    result: dict[str, Any] = {
        "sourceClass": source_class,
        "truthRole": truth_role,
        "path": path,
        "locator": locator,
        "score": score + 2 * path_score,
        "matchedTerms": list(all_matched),
        "excerpt": _excerpt(text, all_matched),
    }
    if extra:
        result.update(extra)
    return result


def _projection_health(generated: Path) -> dict[str, Any]:
    path = generated / "projection-health.json"
    if not path.exists():
        return {
            "available": False,
            "currentness": "UNKNOWN_NO_GENERATED_PROJECTION_HEALTH",
            "counts": {},
        }
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "available": False,
            "currentness": "UNKNOWN_UNREADABLE_PROJECTION_HEALTH",
            "counts": {},
            "error": f"{type(error).__name__}: {error}",
        }
    rows = value if isinstance(value, list) else value.get("projectionHealth", []) if isinstance(value, dict) else []
    counts: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("health") or row.get("currentness") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    fully_current = bool(counts) and set(counts) <= {"CURRENT_TO_SOURCE", "CURRENT_VERIFIED"}
    return {
        "available": True,
        "currentness": "CURRENT_VERIFIED" if fully_current else "MIXED_OR_UNKNOWN",
        "counts": dict(sorted(counts.items())),
    }


def prior_result_first_look(
    query: str,
    *,
    repository_root: str | Path = ".",
    generated_dir: str | Path = "generated",
    limit: int = 8,
) -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= 32:
        raise ValueError("first-look limit must be an integer from 1 to 32")
    root = Path(repository_root)
    generated = Path(generated_dir)
    if not generated.is_absolute():
        generated = root / generated
    query_terms = _terms(query)
    candidates: list[dict[str, Any]] = []

    for name in _GENERATED_FILES:
        path = generated / name
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for locator, row in _records(value):
            text = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            currentness = None
            if isinstance(row, dict):
                currentness = row.get("currentness") or row.get("health")
            candidate = _candidate(
                source_class="generated-owner-projection",
                truth_role="owner-projection-reference-not-atlas-truth",
                path=str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
                locator=_record_locator(locator),
                text=text,
                query_terms=query_terms,
                extra={"currentness": str(currentness)} if currentness is not None else None,
            )
            if candidate is not None:
                candidates.append(candidate)

    synthesis = root / "synthesis"
    if synthesis.exists():
        for path in sorted(synthesis.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            candidate = _candidate(
                source_class="curated-synthesis",
                truth_role="non-authoritative-cross-owner-synthesis",
                path=str(path.relative_to(root)),
                locator="$file",
                text=text,
                query_terms=query_terms,
            )
            if candidate is not None:
                candidates.append(candidate)

    candidates.sort(key=lambda item: (-int(item["score"]), str(item["path"]), str(item["locator"])))
    bounded = candidates[:limit]
    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-prior-result-first-look-experimental",
        "truthRole": "non-authoritative-prior-result-candidate-projection",
        "query": query.strip(),
        "queryTerms": list(query_terms),
        "candidateCount": len(bounded),
        "candidates": bounded,
        "projectionHealth": _projection_health(generated),
        "claims": {
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


def inspect_prior_result_candidate(
    query: str,
    candidate_path: str,
    candidate_locator: str,
    *,
    repository_root: str | Path = ".",
    generated_dir: str | Path = "generated",
    limit: int = 8,
) -> dict[str, Any]:
    """Read one exact first-look candidate without becoming an arbitrary file reader.

    The candidate must be present in the bounded first-look result for the same query,
    path, locator, and limit. Atlas returns source bytes/rows but still does not infer
    semantic equivalence, novelty, research admission, or owner truth.
    """

    if not isinstance(candidate_path, str) or not candidate_path or candidate_path != candidate_path.strip():
        raise ValueError("candidate path must be non-empty and trimmed")
    if not isinstance(candidate_locator, str) or not candidate_locator or candidate_locator != candidate_locator.strip():
        raise ValueError("candidate locator must be non-empty and trimmed")
    root = Path(repository_root)
    result = prior_result_first_look(
        query,
        repository_root=root,
        generated_dir=generated_dir,
        limit=limit,
    )
    candidate = next(
        (
            item
            for item in result["candidates"]
            if item.get("path") == candidate_path and item.get("locator") == candidate_locator
        ),
        None,
    )
    if candidate is None:
        raise ValueError("candidate is not present in the bounded first-look result")

    source_class = candidate.get("sourceClass")
    content: dict[str, Any]
    if source_class == "curated-synthesis":
        if candidate_locator != "$file":
            raise ValueError("curated synthesis candidate must use $file locator")
        synthesis_root = (root / "synthesis").resolve()
        target = (root / candidate_path).resolve()
        if not target.is_relative_to(synthesis_root) or target.suffix != ".md":
            raise ValueError("curated synthesis candidate escaped the synthesis root")
        payload = target.read_bytes()
        if len(payload) > _MAX_INSPECT_BYTES:
            raise ValueError(f"candidate content exceeds {_MAX_INSPECT_BYTES} bytes")
        text = payload.decode("utf-8")
        content = {
            "encoding": "text/markdown; charset=utf-8",
            "text": text,
        }
    elif source_class == "generated-owner-projection":
        generated = Path(generated_dir)
        if not generated.is_absolute():
            generated = root / generated
        generated_root = generated.resolve()
        target = (root / candidate_path).resolve()
        if (
            not target.is_relative_to(generated_root)
            or target.name not in _GENERATED_FILES
            or target.parent != generated_root
        ):
            raise ValueError("generated candidate escaped the generated projection set")
        value = json.loads(target.read_text(encoding="utf-8"))
        row = next(
            (item for locator, item in _records(value) if _record_locator(locator) == candidate_locator),
            None,
        )
        if row is None:
            raise ValueError("generated candidate locator no longer resolves")
        payload = json.dumps(
            row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if len(payload) > _MAX_INSPECT_BYTES:
            raise ValueError(f"candidate content exceeds {_MAX_INSPECT_BYTES} bytes")
        content = {
            "encoding": "application/json; charset=utf-8",
            "json": row,
        }
    else:
        raise ValueError("unsupported first-look candidate source class")

    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-prior-result-candidate-inspection-experimental",
        "truthRole": "non-authoritative-first-look-candidate-content",
        "query": result["query"],
        "candidate": candidate,
        "contentBytes": len(payload),
        "contentDigest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "content": content,
        "projectionHealth": result["projectionHealth"],
        "claims": {
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


__all__ = ["inspect_prior_result_candidate", "prior_result_first_look"]
