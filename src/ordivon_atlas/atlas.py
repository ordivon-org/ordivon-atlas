from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


class HealthState(StrEnum):
    CURRENT_TO_SOURCE = "CURRENT_TO_SOURCE"
    SOURCE_ADVANCED_STALE = "SOURCE_ADVANCED_STALE"
    AUTHORITY_CHANGED_UNRESOLVED = "AUTHORITY_CHANGED_UNRESOLVED"
    BROKEN_POINTER = "BROKEN_POINTER"
    CURRENTNESS_UNKNOWN = "CURRENTNESS_UNKNOWN"


@dataclass(frozen=True)
class SourceSpec:
    ownerResearchRef: str
    authorityRef: str
    repo: str
    remote: str | None
    ref: str
    corpusRoot: str
    remoteFallbacks: list[str] | None = None
    transportMode: str = "remote_git"

    @property
    def current_path(self) -> str:
        return _join_repo_path(self.corpusRoot, "authority/CURRENT.json")


@dataclass
class SourceObservation:
    ownerResearchRef: str
    authorityRef: str
    transportRevision: str | None
    authorityVersionRef: str | None
    health: str
    reason: str | None
    currentRecovery: dict[str, Any] | None
    publication: dict[str, Any] | None
    publicationPath: str | None

    def public(self) -> dict[str, Any]:
        return asdict(self)


class AtlasSourceError(RuntimeError):
    pass


def _run_git(repo: str, args: list[str], *, timeout: int = 20) -> bytes:
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise AtlasSourceError(stderr or f"git {' '.join(args)} failed with {proc.returncode}")
    return proc.stdout


def _remote_revision(spec: SourceSpec) -> str:
    remotes = [remote for remote in [spec.remote, *(spec.remoteFallbacks or [])] if remote]
    errors: list[str] = []
    for remote in remotes:
        try:
            proc = subprocess.run(
                ["git", "ls-remote", remote, spec.ref],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            errors.append(f"{remote}: timeout")
            continue
        if proc.returncode != 0:
            errors.append(f"{remote}: {proc.stderr.decode('utf-8', errors='replace').strip() or 'git ls-remote failed'}")
            continue
        lines = [line for line in proc.stdout.decode().splitlines() if line.strip()]
        if len(lines) == 1:
            return lines[0].split("\t", 1)[0]
        errors.append(f"{remote}: expected exactly one ref for {spec.ref}, got {len(lines)}")
    raise AtlasSourceError(" | ".join(errors) or "no remote Git source transport configured")


def _local_revision(spec: SourceSpec) -> str:
    if not spec.ref.startswith("refs/"):
        raise AtlasSourceError(f"local Git source ref must be explicit: {spec.ref}")
    raw = _run_git(spec.repo, ["rev-parse", "--verify", f"{spec.ref}^{{commit}}"])
    revision = raw.decode("utf-8", errors="strict").strip()
    if len(revision) != 40 or any(ch not in "0123456789abcdef" for ch in revision):
        raise AtlasSourceError(f"local Git source ref did not resolve to one commit: {spec.ref}")
    return revision


def _transport_revision(spec: SourceSpec) -> str:
    if spec.transportMode == "remote_git":
        return _remote_revision(spec)
    if spec.transportMode == "local_git":
        return _local_revision(spec)
    raise AtlasSourceError(f"unsupported source transport mode: {spec.transportMode}")


def _git_show(repo: str, revision: str, path: str) -> bytes:
    return _run_git(repo, ["show", f"{revision}:{path}"])


def _git_path_exists(repo: str, revision: str, path: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{revision}:{path}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
        check=False,
    )
    return proc.returncode == 0


def _join_repo_path(root: str, relative: str) -> str:
    root_path = PurePosixPath(root)
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise AtlasSourceError(f"unsafe publication path: {relative}")
    return str(root_path / rel)


def _sha256_ref(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _verify_declared_source_integrity(
    spec: SourceSpec, transport_revision: str, publication: dict[str, Any]
) -> None:
    source = publication.get("source")
    if not isinstance(source, dict) or source.get("kind") != "git-multi-ref-aggregate":
        return

    manifest_ref = source.get("aggregateManifest")
    expected_manifest_digest = source.get("aggregateManifestDigest")
    if not isinstance(manifest_ref, str) or not manifest_ref:
        raise AtlasSourceError("aggregate publication missing aggregateManifest")
    if not isinstance(expected_manifest_digest, str) or not expected_manifest_digest.startswith("sha256:"):
        raise AtlasSourceError("aggregate publication missing aggregateManifestDigest")

    manifest_path = _join_repo_path("", manifest_ref)
    manifest_bytes = _git_show(spec.repo, transport_revision, manifest_path)
    observed_manifest_digest = _sha256_ref(manifest_bytes)
    if observed_manifest_digest != expected_manifest_digest:
        raise AtlasSourceError(
            f"aggregate manifest digest mismatch: expected {expected_manifest_digest}, observed {observed_manifest_digest}"
        )
    try:
        manifest = json.loads(manifest_bytes)
    except Exception as exc:
        raise AtlasSourceError(f"aggregate manifest invalid JSON: {exc}") from exc
    if manifest.get("authorityRef") != spec.authorityRef or manifest.get("ownerResearchRef") != spec.ownerResearchRef:
        raise AtlasSourceError("aggregate manifest identity mismatch")

    anchors = manifest.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        raise AtlasSourceError("aggregate manifest has no exact anchors")
    for index, anchor in enumerate(anchors):
        if not isinstance(anchor, dict):
            raise AtlasSourceError(f"aggregate anchor {index} is not an object")
        revision = anchor.get("revision")
        relative_path = anchor.get("path")
        expected_bytes = anchor.get("bytes")
        expected_digest = anchor.get("sha256")
        if (
            not isinstance(revision, str)
            or len(revision) != 40
            or any(ch not in "0123456789abcdef" for ch in revision)
        ):
            raise AtlasSourceError(f"aggregate anchor {index} does not carry an exact commit revision")
        if not isinstance(relative_path, str) or not relative_path:
            raise AtlasSourceError(f"aggregate anchor {index} has no path")
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            raise AtlasSourceError(f"aggregate anchor {index} has invalid byte length")
        if not isinstance(expected_digest, str) or not expected_digest.startswith("sha256:"):
            raise AtlasSourceError(f"aggregate anchor {index} has invalid digest")
        safe_path = _join_repo_path("", relative_path)
        payload = _git_show(spec.repo, revision, safe_path)
        if len(payload) != expected_bytes:
            raise AtlasSourceError(
                f"aggregate anchor {index} byte mismatch: expected {expected_bytes}, observed {len(payload)}"
            )
        observed_digest = _sha256_ref(payload)
        if observed_digest != expected_digest:
            raise AtlasSourceError(
                f"aggregate anchor {index} digest mismatch: expected {expected_digest}, observed {observed_digest}"
            )


def load_registry(path: str | Path) -> list[SourceSpec]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or not isinstance(data.get("sources"), list):
        raise ValueError("unsupported Atlas source registry")
    return [SourceSpec(**item) for item in data["sources"]]


def compare_projected_version(projected: str | None, observation: SourceObservation) -> str:
    if observation.health != HealthState.CURRENT_TO_SOURCE:
        return observation.health
    if projected is None:
        return HealthState.CURRENTNESS_UNKNOWN
    if projected == observation.authorityVersionRef:
        return HealthState.CURRENT_TO_SOURCE
    return HealthState.SOURCE_ADVANCED_STALE


def _result_classification(publication: dict[str, Any], result_ref: str) -> dict[str, Any]:
    standing: set[str] = set()
    roles: set[str] = set()
    verdict: Any = None
    evidence_scope: Any = None
    matched = 0
    for statement in publication.get("statements", []):
        if not isinstance(statement, dict) or statement.get("subjectRef") != result_ref:
            continue
        predicate = statement.get("predicate")
        value = statement.get("value")
        if isinstance(predicate, str) and predicate.startswith("STANDING:") and value is True:
            standing.add(predicate.split(":", 1)[1])
            matched += 1
        elif predicate == "EPISTEMIC_VERDICT":
            verdict = value
            matched += 1
        elif predicate == "EVIDENCE_SCOPE":
            evidence_scope = value
            matched += 1
        elif predicate == "STRUCTURAL_ROLE":
            if isinstance(value, list):
                roles.update(str(item) for item in value)
            elif value is not None:
                roles.add(str(value))
            matched += 1
    return {
        "classificationHealth": "EXPLICIT" if matched else "UNKNOWN",
        "standing": sorted(standing),
        "epistemicVerdict": verdict,
        "evidenceScope": evidence_scope,
        "structuralRoles": sorted(roles),
    }


def _owner_descriptor(publication: dict[str, Any], owner_ref: str) -> dict[str, Any]:
    canonical_name: Any = None
    canonical_referent: Any = None
    historical_names: list[str] = []
    for statement in publication.get("statements", []):
        if not isinstance(statement, dict) or statement.get("subjectRef") != owner_ref or statement.get("scope") != "OWNER":
            continue
        predicate = statement.get("predicate")
        value = statement.get("value")
        if predicate == "CANONICAL_NAME":
            canonical_name = value
        elif predicate == "CANONICAL_REFERENT":
            canonical_referent = value
        elif predicate == "HISTORICAL_NAME":
            if isinstance(value, list):
                historical_names.extend(str(item) for item in value)
            elif value is not None:
                historical_names.append(str(value))
    descriptor: dict[str, Any] = {}
    if canonical_name is not None:
        descriptor["canonicalName"] = canonical_name
    if canonical_referent is not None:
        descriptor["canonicalReferent"] = canonical_referent
    if historical_names:
        descriptor["historicalNames"] = sorted(set(historical_names))
    return descriptor


class Atlas:
    """Generated projection over owner-native publication surfaces.

    Atlas never upgrades a projection into owner truth. Every semantic row carries
    the owner AuthorityVersionRef from a verified owner publication or an explicit
    last-known source fence retained from a prior Atlas projection.
    """

    def __init__(self, sources: Iterable[SourceSpec]):
        self.sources = list(sources)

    @classmethod
    def from_registry(cls, path: str | Path) -> "Atlas":
        return cls(load_registry(path))

    def observe(self, spec: SourceSpec) -> SourceObservation:
        try:
            transport_revision = _transport_revision(spec)
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, None, None, HealthState.CURRENTNESS_UNKNOWN, f"SOURCE_TRANSPORT_UNRESOLVED: {exc}", None, None, None)

        try:
            current_bytes = _git_show(spec.repo, transport_revision, spec.current_path)
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, None, HealthState.CURRENTNESS_UNKNOWN, f"CURRENT_SURFACE_MISSING: {exc}", None, None, None)

        try:
            current = json.loads(current_bytes)
            if current.get("kind") != "ordivon.research-owner-current":
                raise ValueError("unexpected CURRENT kind")
            authority_version = current["currentAuthorityVersionRef"]
            publication_path = _join_repo_path(spec.corpusRoot, current["publication"])
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, None, HealthState.BROKEN_POINTER, f"CURRENT_INVALID: {exc}", None, None, None)

        if current.get("authorityRef") != spec.authorityRef or current.get("ownerResearchRef") != spec.ownerResearchRef:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.AUTHORITY_CHANGED_UNRESOLVED, "CURRENT_IDENTITY_MISMATCH", None, None, publication_path)

        try:
            publication_bytes = _git_show(spec.repo, transport_revision, publication_path)
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, f"PUBLICATION_MISSING: {exc}", None, None, publication_path)

        actual_ref = _sha256_ref(publication_bytes)
        if actual_ref != authority_version:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, f"DIGEST_MISMATCH: expected {authority_version}, observed {actual_ref}", None, None, publication_path)

        try:
            publication = json.loads(publication_bytes)
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, f"PUBLICATION_INVALID_JSON: {exc}", None, None, publication_path)

        if publication.get("authorityRef") != spec.authorityRef or publication.get("ownerResearchRef") != spec.ownerResearchRef:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.AUTHORITY_CHANGED_UNRESOLVED, "PUBLICATION_IDENTITY_MISMATCH", None, publication, publication_path)

        try:
            _verify_declared_source_integrity(spec, transport_revision, publication)
        except Exception as exc:
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, f"DECLARED_SOURCE_INTEGRITY_INVALID: {exc}", None, publication, publication_path)

        recovery = publication.get("currentRecovery")
        if not isinstance(recovery, dict) or not recovery.get("targetRole") or not recovery.get("locator"):
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, "CURRENT_RECOVERY_INVALID", recovery if isinstance(recovery, dict) else None, publication, publication_path)
        if not _git_path_exists(spec.repo, transport_revision, recovery["locator"]):
            return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.BROKEN_POINTER, f"CURRENT_RECOVERY_MISSING: {recovery['locator']}", recovery, publication, publication_path)

        return SourceObservation(spec.ownerResearchRef, spec.authorityRef, transport_revision, authority_version, HealthState.CURRENT_TO_SOURCE, None, recovery, publication, publication_path)

    def observe_all(self) -> list[SourceObservation]:
        return [self.observe(spec) for spec in self.sources]

    def _publication_history(self, spec: SourceSpec, obs: SourceObservation) -> list[dict[str, Any]]:
        if not obs.transportRevision:
            return []
        prefix = _join_repo_path(spec.corpusRoot, "authority/publications")
        try:
            raw = _run_git(spec.repo, ["ls-tree", "-r", "--name-only", obs.transportRevision, prefix]).decode()
        except Exception:
            return []
        rows: list[dict[str, Any]] = []
        for path in sorted(line for line in raw.splitlines() if line.endswith(".json")):
            try:
                payload = _git_show(spec.repo, obs.transportRevision, path)
                version = _sha256_ref(payload)
                parsed = json.loads(payload)
                rows.append({"ownerResearchRef": spec.ownerResearchRef, "authorityRef": spec.authorityRef, "authorityVersionRef": version, "currentness": "CURRENT_VERIFIED" if version == obs.authorityVersionRef else "HISTORICAL_NOT_CURRENT", "profile": parsed.get("profile"), "publicationPath": path, "sourceTransportRevision": obs.transportRevision})
            except Exception as exc:
                rows.append({"ownerResearchRef": spec.ownerResearchRef, "authorityRef": spec.authorityRef, "publicationPath": path, "currentness": "UNRESOLVABLE_HISTORY", "reason": str(exc), "sourceTransportRevision": obs.transportRevision})
        return rows

    def build(self, previous: dict[str, Any] | None = None) -> dict[str, Any]:
        observations = self.observe_all()
        previous = previous or {}
        previous_owner_rows = {row.get("ownerResearchRef"): row for row in previous.get("owners", []) if row.get("ownerResearchRef")}

        owners: list[dict[str, Any]] = []
        recovery: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        closures: list[dict[str, Any]] = []
        negatives: list[dict[str, Any]] = []
        history: list[dict[str, Any]] = []
        health: list[dict[str, Any]] = []
        specs = {spec.ownerResearchRef: spec for spec in self.sources}

        def previous_rows(section: str, owner_ref: str) -> list[dict[str, Any]]:
            return [dict(row) for row in previous.get(section, []) if row.get("ownerResearchRef") == owner_ref]

        def retain(section: str, owner_ref: str, state: str) -> list[dict[str, Any]]:
            rows = previous_rows(section, owner_ref)
            for row in rows:
                row["projectionCurrentness"] = state
                row["retainedFromPreviousProjection"] = True
            return rows

        for obs in observations:
            previous_owner = previous_owner_rows.get(obs.ownerResearchRef)
            previous_ref = previous_owner.get("authorityVersionRef") if previous_owner else None
            previous_state = None if previous_ref is None else compare_projected_version(previous_ref, obs)
            health.append({
                "ownerResearchRef": obs.ownerResearchRef,
                "authorityRef": obs.authorityRef,
                "health": obs.health,
                "reason": obs.reason,
                "observedAuthorityVersionRef": obs.authorityVersionRef,
                "previousProjectedAuthorityVersionRef": previous_ref,
                "previousProjectionCurrentness": previous_state,
                "sourceTransportRevision": obs.transportRevision,
            })

            if obs.health != HealthState.CURRENT_TO_SOURCE or not obs.publication:
                if previous_owner and previous_ref:
                    retained_owner = dict(previous_owner)
                    retained_owner.update({
                        "projectionHealth": obs.health,
                        "projectionCurrentness": obs.health,
                        "retainedFromPreviousProjection": True,
                        "observedAuthorityVersionRef": obs.authorityVersionRef,
                        "observedSourceTransportRevision": obs.transportRevision,
                    })
                    owners.append(retained_owner)
                    recovery.extend(retain("currentRecovery", obs.ownerResearchRef, obs.health))
                    results.extend(retain("results", obs.ownerResearchRef, obs.health))
                    closures.extend(retain("closure", obs.ownerResearchRef, obs.health))
                    negatives.extend(retain("negativeAndLineage", obs.ownerResearchRef, obs.health))
                    history.extend(previous_rows("history", obs.ownerResearchRef))
                else:
                    owners.append({
                        "ownerResearchRef": obs.ownerResearchRef,
                        "authorityRef": obs.authorityRef,
                        "authorityVersionRef": None,
                        "projectionHealth": obs.health,
                        "projectionCurrentness": obs.health,
                        "retainedFromPreviousProjection": False,
                        "sourceTransportRevision": obs.transportRevision,
                    })
                continue

            owners.append({
                "ownerResearchRef": obs.ownerResearchRef,
                "authorityRef": obs.authorityRef,
                "authorityVersionRef": obs.authorityVersionRef,
                "projectionHealth": obs.health,
                "projectionCurrentness": HealthState.CURRENT_TO_SOURCE,
                "retainedFromPreviousProjection": False,
                "sourceTransportRevision": obs.transportRevision,
                **_owner_descriptor(obs.publication, obs.ownerResearchRef),
            })
            history.extend(self._publication_history(specs[obs.ownerResearchRef], obs))
            source_fence = {
                "ownerResearchRef": obs.ownerResearchRef,
                "authorityRef": obs.authorityRef,
                "authorityVersionRef": obs.authorityVersionRef,
                "sourceTransportRevision": obs.transportRevision,
                "projectionCurrentness": HealthState.CURRENT_TO_SOURCE,
                "retainedFromPreviousProjection": False,
            }
            recovery.append({**source_fence, **(obs.currentRecovery or {})})
            for closeout in obs.publication.get("closeouts", []):
                base = {**source_fence, "researchRef": closeout.get("researchRef"), "profile": closeout.get("profile")}
                for result_ref in closeout.get("resultRefs", []):
                    classification = _result_classification(obs.publication, result_ref)
                    results.append({**base, "resultRef": result_ref, **classification})
                for closure in closeout.get("closure", []):
                    closures.append({**source_fence, "researchRef": closeout.get("researchRef"), **closure})
                for item in closeout.get("materialLineage", []):
                    negatives.append({**source_fence, "researchRef": closeout.get("researchRef"), "kind": "MATERIAL_LINEAGE", "summary": item})
                if closeout.get("negativeRoute"):
                    negatives.append({**source_fence, "researchRef": closeout.get("researchRef"), "kind": "NEGATIVE_ROUTE", "summary": closeout["negativeRoute"]})

        return {"schemaVersion": 1, "kind": "ordivon.atlas-projection", "truthRole": "generated-projection", "owners": owners, "currentRecovery": recovery, "results": results, "closure": closures, "negativeAndLineage": negatives, "history": history, "projectionHealth": health}

    def write(self, out_dir: str | Path) -> dict[str, Any]:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        previous = None
        atlas_file = out / "atlas.json"
        if atlas_file.exists():
            try:
                previous = json.loads(atlas_file.read_text(encoding="utf-8"))
            except Exception:
                previous = None

        projection = self.build(previous=previous)
        views = {
            "atlas.json": projection,
            "owner-map.json": projection["owners"],
            "current-recovery.json": projection["currentRecovery"],
            "results.json": projection["results"],
            "closure.json": projection["closure"],
            "negative-history.json": projection["negativeAndLineage"],
            "history.json": projection["history"],
            "projection-health.json": projection["projectionHealth"],
            "projection-health-latest.json": projection["projectionHealth"],
        }
        pending: list[tuple[Path, Path]] = []
        for name, payload in views.items():
            target = out / name
            temp = out / f".{name}.tmp"
            temp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            pending.append((temp, target))
        for temp, target in pending:
            temp.replace(target)
        return projection
