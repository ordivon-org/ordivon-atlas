from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.atlas import SourceSpec
from ordivon_atlas.owner_coverage import (
    CoverageConfig,
    DiscoveryRoot,
    FrontierEntry,
    build_owner_coverage,
)


def source(repo: Path, owner: str = "research-owner:registered") -> SourceSpec:
    return SourceSpec(
        ownerResearchRef=owner,
        authorityRef=f"authority:ordivon:{owner}",
        repo=str(repo),
        remote="unused",
        ref="refs/heads/main",
        corpusRoot="research",
    )


def git_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / ".git").mkdir()
    return path


class OwnerCoverageTests(unittest.TestCase):
    def test_registered_and_explicit_non_owner_close_repository_classification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            non_owner = git_repo(root / "ordivon-container")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[
                    FrontierEntry(
                        subjectRef="project:container",
                        displayName="Container",
                        repo=str(non_owner),
                        disposition="NON_OWNER",
                        reason="durability only",
                    )
                ],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertTrue(projection["summary"]["coverageClassificationComplete"])
            self.assertTrue(projection["summary"]["researchOwnerAdmissionComplete"])
            self.assertEqual(projection["unclassifiedRepositories"], [])

    def test_candidate_is_visible_reconciliation_without_becoming_registered_owner(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            candidate = git_repo(root / "ordivon-candidate")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[
                    FrontierEntry(
                        subjectRef="project:candidate",
                        displayName="Candidate",
                        repo=str(candidate),
                        disposition="OWNER_CANDIDATE",
                        reason="responsibility boundary needs adjudication",
                        ownerResearchRef="research-owner:candidate",
                    )
                ],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertTrue(projection["summary"]["coverageClassificationComplete"])
            self.assertFalse(projection["summary"]["researchOwnerAdmissionComplete"])
            self.assertEqual(projection["summary"]["registeredResearchOwners"], 1)
            self.assertEqual(projection["summary"]["reconciliationRequired"], 1)
            candidate_row = next(
                row for row in projection["coverageRows"] if row["subjectRef"] == "project:candidate"
            )
            self.assertEqual(candidate_row["coverageDisposition"], "OWNER_CANDIDATE")
            self.assertEqual(candidate_row["truthRole"], "non-authoritative-owner-coverage-classification")

    def test_unclassified_discovered_repository_fails_coverage_classification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            unknown = git_repo(root / "ordivon-new-owner-shaped-repo")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertFalse(projection["summary"]["coverageClassificationComplete"])
            self.assertEqual(projection["unclassifiedRepositories"], [str(unknown.resolve())])
            self.assertEqual(
                projection["reconciliationFrontier"][0]["coverageDisposition"],
                "UNCLASSIFIED_REPOSITORY",
            )

    def test_deferred_owner_requires_reconsideration_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            deferred = git_repo(root / "ordivon-deferred")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[
                    FrontierEntry(
                        subjectRef="project:deferred",
                        displayName="Deferred",
                        repo=str(deferred),
                        disposition="ADMISSION_DEFERRED",
                        reason="temporary collision",
                        ownerResearchRef="research-owner:deferred",
                    )
                ],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertIn(
                "DEFERRED_WITHOUT_RECONSIDERATION_TRIGGER:project:deferred",
                projection["configurationErrors"],
            )
            self.assertFalse(projection["summary"]["coverageClassificationComplete"])

    def test_existing_candidate_current_surface_is_reported_not_auto_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            candidate = git_repo(root / "ordivon-candidate")
            current = candidate / "research" / "authority" / "CURRENT.json"
            current.parent.mkdir(parents=True)
            current.write_text("{}", encoding="utf-8")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[
                    FrontierEntry(
                        subjectRef="project:candidate",
                        displayName="Candidate",
                        repo=str(candidate),
                        disposition="OWNER_CANDIDATE",
                        reason="publication needs owner-side validation",
                        ownerResearchRef="research-owner:candidate",
                        corpusRootCandidate="research",
                    )
                ],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertEqual(projection["summary"]["publicationSurfacePresentButUnregistered"], 1)
            self.assertEqual(projection["summary"]["registeredResearchOwners"], 1)


    def test_unavailable_discovery_root_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            missing = root / "missing-inventory-root"
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(missing), namePrefixes=["ordivon-"])],
                entries=[],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertFalse(projection["summary"]["coverageClassificationComplete"])
            self.assertEqual(projection["unavailableDiscoveryRoots"], [str(missing.resolve())])


    def test_represented_institutional_owner_closes_coverage_without_becoming_research_owner(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registered = git_repo(root / "ordivon-registered")
            institutional = git_repo(root / "ordivon-web")
            config = CoverageConfig(
                discoveryRoots=[DiscoveryRoot(path=str(root), namePrefixes=["ordivon-"])],
                entries=[FrontierEntry(
                    subjectRef="project:web", displayName="Web", repo=str(institutional),
                    disposition="INSTITUTIONAL_OWNER_REPRESENTED", reason="publication owner represented separately",
                    coverageScope="INSTITUTIONAL_PUBLICATION",
                )],
            )
            projection = build_owner_coverage([source(registered)], config)
            self.assertTrue(projection["summary"]["coverageClassificationComplete"])
            self.assertTrue(projection["summary"]["institutionalCoverageReconciled"])
            self.assertTrue(projection["summary"]["researchOwnerAdmissionComplete"])
            self.assertEqual(projection["summary"]["recognizedNonResearchInstitutionalOwners"], 1)
            self.assertEqual(projection["summary"]["reconciliationRequired"], 0)



if __name__ == "__main__":
    unittest.main()
