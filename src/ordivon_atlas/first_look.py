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
_MAX_INSPECT_PROJECTION_BYTES = 12_288
_MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.MULTILINE)


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



def _markdown_sections(text: str, query_terms: tuple[str, ...]) -> list[dict[str, Any]]:
    matches = list(_MARKDOWN_HEADING_RE.finditer(text))
    if not matches:
        score, matched = _matches(text, query_terms)
        return (
            [{
                "heading": None,
                "level": 0,
                "score": score,
                "matchedTerms": list(matched),
                "text": text,
                "sourceStart": 0,
                "sourceEnd": len(text),
            }]
            if score
            else []
        )

    sections: list[dict[str, Any]] = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()]
        score, matched = _matches(preamble, query_terms)
        if score:
            sections.append({
                "heading": None,
                "level": 0,
                "score": score,
                "matchedTerms": list(matched),
                "text": preamble,
                "sourceStart": 0,
                "sourceEnd": matches[0].start(),
            })
    for index, heading_match in enumerate(matches):
        start = heading_match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_text = text[start:end]
        score, matched = _matches(section_text, query_terms)
        if not score:
            continue
        sections.append({
            "heading": heading_match.group(2).strip(),
            "level": len(heading_match.group(1)),
            "score": score,
            "matchedTerms": list(matched),
            "text": section_text,
            "sourceStart": start,
            "sourceEnd": end,
        })
    return sections


def _bounded_markdown_projection(
    text: str,
    query_terms: tuple[str, ...],
    *,
    max_projection_bytes: int = _MAX_INSPECT_PROJECTION_BYTES,
) -> dict[str, Any]:
    if (
        type(max_projection_bytes) is not int
        or not 1 <= max_projection_bytes <= _MAX_INSPECT_PROJECTION_BYTES
    ):
        raise ValueError(
            f"max projection bytes must be an integer from 1 to {_MAX_INSPECT_PROJECTION_BYTES}"
        )
    ranked = sorted(
        enumerate(_markdown_sections(text, query_terms)),
        key=lambda item: (-int(item[1]["score"]), item[0]),
    )
    selected: list[dict[str, Any]] = []
    selected_bytes = 0
    omitted_for_size = 0
    for _ordinal, section in ranked:
        section_bytes = len(str(section["text"]).encode("utf-8"))
        if section_bytes > max_projection_bytes:
            omitted_for_size += 1
            continue
        if selected_bytes + section_bytes > max_projection_bytes:
            omitted_for_size += 1
            continue
        selected.append(section)
        selected_bytes += section_bytes
    selected.sort(key=lambda item: int(item["sourceStart"]))
    encoded = json.dumps(
        selected, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "projection": "query-relative-exact-markdown-sections",
        "projectedBytes": selected_bytes,
        "projectionByteLimit": max_projection_bytes,
        "projectionDigest": "sha256:" + hashlib.sha256(encoded).hexdigest(),
        "sectionCount": len(selected),
        "matchedSectionCount": len(ranked),
        "projectionTruncated": len(selected) != len(ranked),
        "omittedForSize": omitted_for_size,
        "sections": selected,
        "fullContentAvailableViaRawEscape": True,
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
    max_projection_bytes: int = _MAX_INSPECT_PROJECTION_BYTES,
) -> dict[str, Any]:
    """Read one exact first-look candidate without becoming an arbitrary file reader.

    The candidate must be present in the bounded first-look result for the same query,
    path, locator, and limit. Atlas returns source bytes/rows but still does not infer
    semantic equivalence, novelty, research admission, or owner truth.
    """

    if (
        type(max_projection_bytes) is not int
        or not 1 <= max_projection_bytes <= _MAX_INSPECT_PROJECTION_BYTES
    ):
        raise ValueError(
            f"max projection bytes must be an integer from 1 to {_MAX_INSPECT_PROJECTION_BYTES}"
        )
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
            "encoding": "text/markdown-sections; charset=utf-8",
            **_bounded_markdown_projection(
                text, _terms(query), max_projection_bytes=max_projection_bytes
            ),
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


def prior_result_first_look_many(
    queries: list[str] | tuple[str, ...],
    *,
    repository_root: str | Path = ".",
    generated_dir: str | Path = "generated",
    limit: int = 8,
) -> dict[str, Any]:
    """Run caller-authored lexical variants as one bounded Atlas owner read.

    Atlas executes the supplied retrieval expressions, deduplicates candidate
    identity and preserves which variant/rank produced the strongest lexical
    match. It does not generate variants or infer that variants/candidates are
    semantically equivalent.
    """
    if not isinstance(queries, (list, tuple)) or not 1 <= len(queries) <= 4:
        raise ValueError("first-look-many requires 1 to 4 query variants")
    if type(limit) is not int or not 1 <= limit <= 32:
        raise ValueError("first-look-many limit must be an integer from 1 to 32")
    normalized: list[str] = []
    for query in queries:
        if not isinstance(query, str) or not query.strip() or query != query.strip():
            raise ValueError("first-look-many queries must be non-empty trimmed strings")
        if len(query.encode("utf-8")) > 2_048:
            raise ValueError("first-look-many query exceeds 2048 UTF-8 bytes")
        if query not in normalized:
            normalized.append(query)
    if not normalized:
        raise ValueError("first-look-many requires at least one distinct query")

    merged: dict[tuple[str, str], dict[str, Any]] = {}
    projection_health: dict[str, Any] | None = None
    variant_summaries: list[dict[str, Any]] = []
    for variant_index, query in enumerate(normalized):
        result = prior_result_first_look(
            query,
            repository_root=repository_root,
            generated_dir=generated_dir,
            limit=32,
        )
        if projection_health is None:
            projection_health = dict(result["projectionHealth"])
        variant_summaries.append(
            {
                "index": variant_index,
                "query": query,
                "candidateCountBeforeMerge": result["candidateCount"],
            }
        )
        for variant_rank, raw_candidate in enumerate(result["candidates"], start=1):
            if not isinstance(raw_candidate, dict):
                continue
            candidate = dict(raw_candidate)
            key = (str(candidate.get("path")), str(candidate.get("locator")))
            current = merged.get(key)
            if current is None:
                candidate["matchedVariantIndexes"] = [variant_index]
                candidate["bestVariantIndex"] = variant_index
                candidate["bestVariantRank"] = variant_rank
                merged[key] = candidate
                continue
            matched_indexes = list(current.get("matchedVariantIndexes", []))
            if variant_index not in matched_indexes:
                matched_indexes.append(variant_index)
                matched_indexes.sort()
            if int(candidate.get("score", 0)) > int(current.get("score", 0)):
                candidate["matchedVariantIndexes"] = matched_indexes
                candidate["bestVariantIndex"] = variant_index
                candidate["bestVariantRank"] = variant_rank
                merged[key] = candidate
            else:
                current["matchedVariantIndexes"] = matched_indexes

    candidates = list(merged.values())
    candidates.sort(
        key=lambda item: (
            -int(item.get("score", 0)),
            str(item.get("path")),
            str(item.get("locator")),
        )
    )
    bounded = candidates[:limit]
    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-prior-result-first-look-many-experimental",
        "truthRole": "non-authoritative-prior-result-candidate-projection",
        "queryVariants": normalized,
        "variantSummaries": variant_summaries,
        "candidateCount": len(bounded),
        "candidates": bounded,
        "projectionHealth": projection_health
        or {
            "available": False,
            "currentness": "UNKNOWN_NO_GENERATED_PROJECTION_HEALTH",
            "counts": {},
        },
        "claims": {
            "callerIntentTranslated": False,
            "queryVariantGenerated": False,
            "queryVariantsSemanticallyEquivalent": False,
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


def retrieval_representation_profile(
    *,
    repository_root: str | Path = ".",
) -> dict[str, Any]:
    """Return mechanical facts about the current Atlas retrieval representation."""
    root = Path(repository_root)
    synthesis = root / "synthesis"
    markdown_files = sorted(synthesis.rglob("*.md")) if synthesis.exists() else []
    latin_letters = 0
    cjk_chars = 0
    total_bytes = 0
    files_with_latin = 0
    files_with_cjk = 0
    for path in markdown_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        latin_count = sum(
            1
            for character in text
            if ("a" <= character <= "z") or ("A" <= character <= "Z")
        )
        cjk_count = sum(1 for character in text if "\u3400" <= character <= "\u9fff")
        total_bytes += len(text.encode("utf-8"))
        latin_letters += latin_count
        cjk_chars += cjk_count
        files_with_latin += int(latin_count > 0)
        files_with_cjk += int(cjk_count > 0)
    script_total = latin_letters + cjk_chars
    dominant_script = None
    if script_total:
        dominant_script = "latin" if latin_letters >= cjk_chars else "cjk"
    dominant_count = max(latin_letters, cjk_chars) if script_total else 0
    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-retrieval-representation-profile-experimental",
        "truthRole": "mechanical-retrieval-environment-profile-not-semantic-truth",
        "retrieval": {
            "mode": "lexical-substring-and-path-match",
            "queryExpansionByAtlas": False,
            "crossLanguageTranslationByAtlas": False,
            "semanticSimilarityByAtlas": False,
            "callerAuthoredQueryVariantsSupported": True,
            "maxCallerAuthoredQueryVariants": 4,
        },
        "curatedSynthesisCorpus": {
            "root": "synthesis",
            "markdownFileCount": len(markdown_files),
            "totalBytes": total_bytes,
            "latinLetters": latin_letters,
            "cjkChars": cjk_chars,
            "filesWithLatin": files_with_latin,
            "filesWithCjk": files_with_cjk,
            "dominantObservedScript": dominant_script,
            "dominantObservedScriptShareOfLatinPlusCjk": (
                format(dominant_count / script_total, ".12f").rstrip("0").rstrip(".")
                if script_total
                else None
            ),
        },
        "claims": {
            "callerIntentTranslated": False,
            "queryVariantGenerated": False,
            "queryVariantsSemanticallyEquivalent": False,
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


def retrieval_coordinate_profile(
    *,
    repository_root: str | Path = ".",
) -> dict[str, Any]:
    """Project a small task-neutral subset of owner-curated retrieval handles."""
    root = Path(repository_root)
    source = root / "synthesis" / "research-process-lineage" / "SOURCE-INDEX.md"
    payload = source.read_bytes()
    lines = payload.decode("utf-8").splitlines()
    coordinates: list[dict[str, str]] = []
    marker = "Key retrieval aliases / pressure terms:"
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        heading = None
        for heading_index in range(index - 1, -1, -1):
            if lines[heading_index].startswith("## "):
                heading = lines[heading_index][3:].strip()
                break
        first_alias = None
        for alias_index in range(index + 1, len(lines)):
            candidate = lines[alias_index]
            if candidate.startswith("## "):
                break
            if candidate.startswith("- "):
                first_alias = candidate[2:].strip()
                break
        if heading and first_alias:
            coordinates.append(
                {"sectionHeading": heading, "retrievalAlias": first_alias}
            )
    if not coordinates:
        raise ValueError("Atlas retrieval-coordinate source has no retrieval sections")
    if len(coordinates) > 32:
        raise ValueError("Atlas retrieval-coordinate source exceeds bounded section count")
    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-retrieval-coordinate-profile-experimental",
        "truthRole": "mechanical-source-grounded-retrieval-coordinates-not-query-translation",
        "source": {
            "path": str(source.relative_to(root)),
            "contentDigest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        },
        "selection": {
            "method": "first-alias-per-retrieval-section-in-source-order",
            "taskConditioned": False,
            "semanticRankingPerformed": False,
        },
        "coordinates": coordinates,
        "claims": {
            "callerIntentTranslated": False,
            "queryVariantGenerated": False,
            "coordinatesSemanticallyEquivalentToIntent": False,
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


def retrieval_authoring_context(
    *,
    repository_root: str | Path = ".",
) -> dict[str, Any]:
    """Compose static owner retrieval facts for caller query authoring.

    The result is intentionally upstream of query formation: it describes the
    current retrieval representation and owner-curated retrieval coordinates,
    but does not translate an intent, generate a query or grant research standing.
    """
    representation = retrieval_representation_profile(repository_root=repository_root)
    coordinates = retrieval_coordinate_profile(repository_root=repository_root)
    return {
        "schemaVersion": 0,
        "kind": "ordivon.atlas-retrieval-authoring-context-experimental",
        "truthRole": "mechanical-retrieval-authoring-context-not-query-or-semantic-truth",
        "representationProfile": representation,
        "coordinateProfile": coordinates,
        "claims": {
            "callerIntentTranslated": False,
            "queryVariantGenerated": False,
            "semanticEquivalenceInferred": False,
            "noveltyStanding": "UNKNOWN_CALLER_MUST_ADJUDICATE",
            "researchAdmissionGranted": False,
            "ownerTruthMinted": False,
        },
    }


__all__ = [
    "inspect_prior_result_candidate",
    "prior_result_first_look",
    "prior_result_first_look_many",
    "retrieval_authoring_context",
    "retrieval_coordinate_profile",
    "retrieval_representation_profile",
]
