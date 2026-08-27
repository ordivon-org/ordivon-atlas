from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.atlas import SourceSpec
from ordivon_atlas.institutional_topology import (
    InstitutionalOwnerSpec,
    build_institutional_topology,
    observe_institutional_owner,
)


def run(*args: str, cwd: Path | None = None) -> str:
    proc=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return proc.stdout.strip()


def repo_fixture(root: Path) -> Path:
    repo=root/"owner"
    run("git","init","-b","main",str(repo))
    run("git","config","user.email","topology@example.invalid",cwd=repo)
    run("git","config","user.name","Topology Fixture",cwd=repo)
    (repo/"README.md").write_text("entry\n")
    (repo/"docs").mkdir()
    (repo/"docs/authority.md").write_text("owner authority\n")
    run("git","add",".",cwd=repo); run("git","commit","-m","owner",cwd=repo)
    return repo


def institutional(repo: Path, recovery: str = "docs/authority.md") -> InstitutionalOwnerSpec:
    return InstitutionalOwnerSpec(
        institutionalOwnerRef="institutional-owner:fixture", ownerNativeRef="fixture", displayName="Fixture",
        repo=str(repo), authorityClass="FIXTURE_AUTHORITY", scope="FIXTURE", cardinality="SINGLETON",
        recoveryRef=recovery, entryRef="README.md", transportMode="local_git", remote=None, ref="refs/heads/main",
        sourceBoundary="source only", nonClaims=["semantic authority from Atlas"],
    )


class InstitutionalTopologyTests(unittest.TestCase):
    def test_source_fenced_recovery_is_present_without_minting_authority(self):
        with tempfile.TemporaryDirectory() as td:
            repo=repo_fixture(Path(td))
            row=observe_institutional_owner(institutional(repo))
            self.assertEqual(row["sourceFenceHealth"],"SOURCE_FENCED_RECOVERY_PRESENT")
            self.assertEqual(row["truthRole"],"non-authoritative-source-fenced-owner-reference")
            self.assertEqual(row["transportRevision"],run("git","rev-parse","HEAD",cwd=repo))

    def test_missing_recovery_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo=repo_fixture(Path(td))
            row=observe_institutional_owner(institutional(repo,"docs/missing.md"))
            self.assertEqual(row["sourceFenceHealth"],"OWNER_RECOVERY_UNRESOLVED")
            self.assertIn("docs/missing.md",row["reason"])

    def test_research_and_nonresearch_facets_coexist(self):
        with tempfile.TemporaryDirectory() as td:
            repo=repo_fixture(Path(td))
            research=SourceSpec("research-owner:fixture","authority:ordivon:research-owner:fixture",str(repo),None,"refs/heads/main","research",transportMode="local_git")
            health=[{"ownerResearchRef":"research-owner:fixture","health":"CURRENT_TO_SOURCE","sourceTransportRevision":"a"*40,"observedAuthorityVersionRef":"sha256:"+"b"*64,"currentRecovery":{"locator":"research/README.md"}}]
            recovery=[{"ownerResearchRef":"research-owner:fixture","locator":"research/README.md","targetRole":"OWNER_RESEARCH_CORPUS"}]
            x=build_institutional_topology([research],[institutional(repo)],health,recovery)
            research_row=next(r for r in x["ownerRows"] if r["ownerFacet"]=="RESEARCH_AUTHORITY")
            self.assertEqual(research_row["recoveryRef"],"research/README.md")
            self.assertEqual(research_row["recoveryTargetRole"],"OWNER_RESEARCH_CORPUS")
            self.assertEqual(x["summary"]["representedOwnerFacets"],2)
            self.assertEqual({r["ownerFacet"] for r in x["ownerRows"]},{"RESEARCH_AUTHORITY","INSTITUTIONAL_NON_RESEARCH"})

    def test_repository_registry_keeps_atlas_out_of_research_sources(self):
        root=Path(__file__).resolve().parents[1]
        sources=json.loads((root/"config/sources.json").read_text())["sources"]
        institutional_rows=json.loads((root/"config/institutional-owners.json").read_text())["entries"]
        self.assertNotIn("research-owner:atlas",{r["ownerResearchRef"] for r in sources})
        atlas=next(r for r in institutional_rows if r["institutionalOwnerRef"]=="institutional-owner:atlas")
        self.assertEqual(atlas["authorityClass"],"PROJECTION_OBSERVATORY_INFRASTRUCTURE")
        self.assertIn("generated projection as source of truth",atlas["nonClaims"])

    def test_workstation_is_explicitly_per_node_and_web_publication_boundary_is_separate(self):
        root=Path(__file__).resolve().parents[1]
        rows=json.loads((root/"config/institutional-owners.json").read_text())["entries"]
        workstation=next(r for r in rows if r["displayName"]=="Workstation")
        web=next(r for r in rows if r["displayName"]=="Web")
        self.assertEqual(workstation["cardinality"],"PER_EXECUTION_NODE")
        self.assertEqual(workstation["scope"],"THIS_ATTACHED_EXECUTION_NODE")
        self.assertIn("LIVE_PHYSICAL_CURRENTNESS_REMAINS_OPERATION_RELATIVE",workstation["sourceBoundary"])
        self.assertIn("WEB_PUBLICATION_ADMISSION_REMAINS_PROMOTION_RECEIPT_TAG_AUTHORITY",web["sourceBoundary"])


if __name__ == "__main__": unittest.main()
