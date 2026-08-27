from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .atlas import SourceSpec, _git_path_exists, _transport_revision


@dataclass(frozen=True)
class InstitutionalOwnerSpec:
    institutionalOwnerRef: str
    ownerNativeRef: str
    displayName: str
    repo: str
    authorityClass: str
    scope: str
    cardinality: str
    recoveryRef: str
    entryRef: str
    transportMode: str
    remote: str | None
    ref: str
    remoteFallbacks: list[str] | None = None
    sourceBoundary: str | None = None
    nonClaims: list[str] | None = None


class InstitutionalTopologyError(ValueError):
    pass


def load_institutional_registry(path: str | Path) -> list[InstitutionalOwnerSpec]:
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("kind") != "ordivon.atlas-institutional-owner-reference-registry":
        raise InstitutionalTopologyError("unsupported institutional owner registry")
    if data.get("truthRole") != "non-authoritative-owner-reference-registry":
        raise InstitutionalTopologyError("institutional owner registry must remain non-authoritative")
    rows=[InstitutionalOwnerSpec(**row) for row in data.get("entries",[])]
    refs=[row.institutionalOwnerRef for row in rows]
    if len(refs) != len(set(refs)):
        raise InstitutionalTopologyError("duplicate institutionalOwnerRef")
    return rows


def observe_institutional_owner(spec: InstitutionalOwnerSpec) -> dict[str, Any]:
    transport=SourceSpec(
        ownerResearchRef=f"transport:{spec.institutionalOwnerRef}",
        authorityRef=f"transport:{spec.institutionalOwnerRef}",
        repo=spec.repo, remote=spec.remote, ref=spec.ref, corpusRoot="",
        remoteFallbacks=spec.remoteFallbacks, transportMode=spec.transportMode,
    )
    row={
        **asdict(spec),
        "ownerFacet":"INSTITUTIONAL_NON_RESEARCH",
        "truthRole":"non-authoritative-source-fenced-owner-reference",
        "verificationLevel":"OWNER_NATIVE_CANONICAL_RECOVERY_SOURCE_FENCE",
        "transportRevision":None,
        "sourceFenceHealth":"SOURCE_TRANSPORT_UNRESOLVED",
        "reason":None,
    }
    try:
        revision=_transport_revision(transport)
        row["transportRevision"]=revision
    except Exception as exc:
        row["reason"]=str(exc)
        return row
    missing=[]
    for relative in [spec.entryRef,spec.recoveryRef]:
        if not _git_path_exists(spec.repo, revision, relative):
            missing.append(relative)
    if missing:
        row["sourceFenceHealth"]="OWNER_RECOVERY_UNRESOLVED"
        row["reason"]="missing source-fenced owner recovery: "+", ".join(missing)
        return row
    row["sourceFenceHealth"]="SOURCE_FENCED_RECOVERY_PRESENT"
    return row


def build_institutional_topology(
    research_sources: Iterable[SourceSpec],
    institutional_specs: Iterable[InstitutionalOwnerSpec],
    research_health: list[dict[str, Any]] | None = None,
    research_recovery: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    sources=list(research_sources)
    specs=list(institutional_specs)
    health_by_owner={row.get("ownerResearchRef"):row for row in (research_health or [])}
    recovery_by_owner={row.get("ownerResearchRef"):row for row in (research_recovery or [])}
    rows=[]
    for source in sorted(sources,key=lambda x:x.ownerResearchRef):
        health=health_by_owner.get(source.ownerResearchRef,{})
        recovery=recovery_by_owner.get(source.ownerResearchRef,{})
        rows.append({
            "institutionalOwnerRef":source.ownerResearchRef,
            "ownerNativeRef":source.ownerResearchRef,
            "displayName":source.ownerResearchRef.removeprefix("research-owner:"),
            "repo":str(Path(source.repo).resolve(strict=False)),
            "ownerFacet":"RESEARCH_AUTHORITY",
            "authorityClass":"RESEARCH_AUTHORITY",
            "scope":"OWNER_NATIVE_RESEARCH_SEMANTICS",
            "cardinality":"OWNER_SCOPED",
            "recoveryRef":recovery.get("locator"),
            "recoveryTargetRole":recovery.get("targetRole"),
            "verificationLevel":"OWNER_NATIVE_IMMUTABLE_RESEARCH_PUBLICATION",
            "sourceFenceHealth":health.get("health","NOT_OBSERVED_IN_THIS_PROJECTION"),
            "transportRevision":health.get("transportRevision") or health.get("sourceTransportRevision"),
            "authorityVersionRef":health.get("authorityVersionRef") or health.get("observedAuthorityVersionRef"),
            "truthRole":"registered-research-authority-reference-not-owner-truth",
        })
    rows.extend(observe_institutional_owner(spec) for spec in sorted(specs,key=lambda x:x.institutionalOwnerRef))
    unresolved=[row for row in rows if row["ownerFacet"]=="INSTITUTIONAL_NON_RESEARCH" and row["sourceFenceHealth"]!="SOURCE_FENCED_RECOVERY_PRESENT"]
    return {
        "schemaVersion":1,
        "kind":"ordivon.atlas-institutional-owner-topology",
        "truthRole":"non-authoritative-cross-owner-topology-projection",
        "laws":[
            "INSTITUTIONAL_OWNER != RESEARCH_OWNER",
            "OWNER_FACET != REPOSITORY_IDENTITY",
            "SOURCE_FENCED_RECOVERY != SEMANTIC_AUTHORITY",
            "PUBLICATION_CURRENTNESS != LIVE_PHYSICAL_CURRENTNESS",
            "ATLAS_PROJECTION != OWNER_TRUTH",
        ],
        "ownerRows":rows,
        "unresolvedInstitutionalSourceFences":unresolved,
        "summary":{
            "researchAuthorityOwners":len(sources),
            "recognizedNonResearchInstitutionalOwners":len(specs),
            "representedOwnerFacets":len(rows),
            "unresolvedInstitutionalSourceFences":len(unresolved),
            "institutionalTopologySourceFenced":not unresolved,
        },
    }


def write_institutional_topology(research_sources, institutional_specs, out_dir, research_health=None, research_recovery=None):
    projection=build_institutional_topology(research_sources,institutional_specs,research_health,research_recovery)
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    target=out/"institutional-owner-topology.json"; temp=out/".institutional-owner-topology.json.tmp"
    temp.write_text(json.dumps(projection,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    temp.replace(target)
    return projection
