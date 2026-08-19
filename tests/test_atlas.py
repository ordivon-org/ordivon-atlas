from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState, SourceSpec, compare_projected_version


def run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout.strip()


def write_publication(work: Path, *, owner: str = "fixture", authority: str = "authority:fixture", recovery: str = "research/README.md", corrupt_digest: bool = False, statements: list[dict] | None = None) -> tuple[str, SourceSpec]:
    root = work / "research"
    (root / "authority/publications").mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("fixture\n")
    payload = {"schemaVersion": 1, "kind": "ordivon.research-owner-publication", "profile": "NATIVE", "authorityRef": authority, "ownerResearchRef": f"research-owner:{owner}", "source": {"kind": "git", "repository": str(work), "authorityBranch": "refs/heads/main", "sourceRevision": "fixture", "corpusRoot": "research"}, "currentRecovery": {"targetRole": "OWNER_RESEARCH_CORPUS", "locator": recovery}, "statements": list(statements or []), "closeouts": [{"researchRef": "research:fixture", "profile": "NATIVE", "resultRefs": ["result:fixture"], "closure": [{"scope": "ITEM", "status": "ESTABLISHED"}], "residualState": "NONE", "reopenPolicy": "UNKNOWN"}]}
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    digest = hashlib.sha256(content.encode()).hexdigest()
    (root / f"authority/publications/{digest}.json").write_text(content)
    current_ref = "sha256:" + ("0" * 64 if corrupt_digest else digest)
    current = {"schemaVersion": 1, "kind": "ordivon.research-owner-current", "authorityRef": authority, "ownerResearchRef": f"research-owner:{owner}", "currentAuthorityVersionRef": current_ref, "publication": f"authority/publications/{digest}.json"}
    (root / "authority/CURRENT.json").write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    run("git", "add", ".", cwd=work)
    run("git", "commit", "-m", "fixture", cwd=work)
    run("git", "push", "origin", "main", cwd=work)
    spec = SourceSpec(f"research-owner:{owner}", authority, str(work), str(work.parent / "remote.git"), "refs/heads/main", "research")
    return "sha256:" + digest, spec


class AtlasTests(unittest.TestCase):
    def fixture_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        base = Path(td.name)
        remote = base / "remote.git"
        work = base / "work"
        run("git", "init", "--bare", str(remote))
        run("git", "init", "-b", "main", str(work))
        run("git", "config", "user.email", "atlas@example.invalid", cwd=work)
        run("git", "config", "user.name", "Atlas Fixture", cwd=work)
        run("git", "remote", "add", "origin", str(remote), cwd=work)
        return td, work

    def test_current_and_stale_comparison(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        version, spec = write_publication(work)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(compare_projected_version(version, obs), HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(compare_projected_version("sha256:" + "1" * 64, obs), HealthState.SOURCE_ADVANCED_STALE)

    def test_owner_descriptor_projects_canonical_name_without_changing_identity(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        statements = [
            {"predicate": "CANONICAL_NAME", "scope": "OWNER", "subjectRef": "research-owner:fixture", "value": "Interlocus"},
            {"predicate": "CANONICAL_REFERENT", "scope": "OWNER", "subjectRef": "research-owner:fixture", "value": "Interlocus Capability"},
            {"predicate": "HISTORICAL_NAME", "scope": "OWNER", "subjectRef": "research-owner:fixture", "value": "Network"},
            {"predicate": "OWNER_BINDING", "scope": "OWNER", "subjectRef": "research-owner:fixture", "value": "fixture"},
        ]
        _, spec = write_publication(work, statements=statements)
        owner = Atlas([spec]).build()["owners"][0]
        self.assertEqual(owner["ownerResearchRef"], "research-owner:fixture")
        self.assertEqual(owner["canonicalName"], "Interlocus")
        self.assertEqual(owner["canonicalReferent"], "Interlocus Capability")
        self.assertEqual(owner["historicalNames"], ["Network"])

    def test_digest_mismatch_fails_closed(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        _, spec = write_publication(work, corrupt_digest=True)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.BROKEN_POINTER)
        self.assertIn("DIGEST_MISMATCH", obs.reason or "")

    def test_missing_recovery_fails_closed(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        _, spec = write_publication(work, recovery="research/DOES-NOT-EXIST.md")
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.BROKEN_POINTER)
        self.assertIn("CURRENT_RECOVERY_MISSING", obs.reason or "")

    def test_missing_current_is_unknown(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        (work / "research").mkdir(); (work / "research/README.md").write_text("no publication\n")
        run("git", "add", ".", cwd=work); run("git", "commit", "-m", "no-current", cwd=work); run("git", "push", "origin", "main", cwd=work)
        spec = SourceSpec("research-owner:missing", "authority:missing", str(work), str(work.parent / "remote.git"), "refs/heads/main", "research")
        self.assertEqual(Atlas([spec]).observe(spec).health, HealthState.CURRENTNESS_UNKNOWN)

    def test_identity_mismatch_fails_closed(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        _, spec = write_publication(work, owner="fixture", authority="authority:fixture")
        wrong = SourceSpec("research-owner:other", "authority:other", spec.repo, spec.remote, spec.ref, spec.corpusRoot)
        self.assertEqual(Atlas([wrong]).observe(wrong).health, HealthState.AUTHORITY_CHANGED_UNRESOLVED)


if __name__ == "__main__":
    unittest.main()


class BrokenPublicationTests(unittest.TestCase):
    def fixture_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        base = Path(td.name)
        remote = base / "remote.git"
        work = base / "work"
        run("git", "init", "--bare", str(remote))
        run("git", "init", "-b", "main", str(work))
        run("git", "config", "user.email", "atlas@example.invalid", cwd=work)
        run("git", "config", "user.name", "Atlas Fixture", cwd=work)
        run("git", "remote", "add", "origin", str(remote), cwd=work)
        return td, work

    def test_missing_publication_fails_closed(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        _, spec = write_publication(work)
        current_path = work / "research/authority/CURRENT.json"
        current = json.loads(current_path.read_text())
        current["publication"] = "authority/publications/does-not-exist.json"
        current_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        run("git", "add", ".", cwd=work); run("git", "commit", "-m", "break-publication", cwd=work); run("git", "push", "origin", "main", cwd=work)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.BROKEN_POINTER)
        self.assertIn("PUBLICATION_MISSING", obs.reason or "")


class RefreshPublicationTests(unittest.TestCase):
    def fixture_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        base = Path(td.name)
        remote = base / "remote.git"
        work = base / "work"
        run("git", "init", "--bare", str(remote))
        run("git", "init", "-b", "main", str(work))
        run("git", "config", "user.email", "atlas@example.invalid", cwd=work)
        run("git", "config", "user.name", "Atlas Fixture", cwd=work)
        run("git", "remote", "add", "origin", str(remote), cwd=work)
        return td, work

    def test_unhealthy_refresh_retains_last_known_owner_data(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        version, spec = write_publication(work)
        atlas = Atlas([spec])
        out = Path(td.name) / "generated"
        first = atlas.write(out)
        self.assertEqual(first["projectionHealth"][0]["health"], HealthState.CURRENT_TO_SOURCE)
        self.assertEqual(first["owners"][0]["authorityVersionRef"], version)
        first_results = [row["resultRef"] for row in first["results"]]

        current_path = work / "research/authority/CURRENT.json"
        current = json.loads(current_path.read_text())
        current["publication"] = "authority/publications/missing-after-good-snapshot.json"
        current_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        run("git", "add", ".", cwd=work); run("git", "commit", "-m", "break-after-good", cwd=work); run("git", "push", "origin", "main", cwd=work)

        projection = atlas.write(out)
        self.assertEqual(projection["projectionHealth"][0]["health"], HealthState.BROKEN_POINTER)
        owner = projection["owners"][0]
        self.assertEqual(owner["authorityVersionRef"], version)
        self.assertEqual(owner["projectionCurrentness"], HealthState.BROKEN_POINTER)
        self.assertTrue(owner["retainedFromPreviousProjection"])
        self.assertEqual([row["resultRef"] for row in projection["results"]], first_results)
        self.assertTrue(all(row["retainedFromPreviousProjection"] for row in projection["results"]))
        self.assertTrue(all(row["projectionCurrentness"] == HealthState.BROKEN_POINTER for row in projection["results"]))
        canonical = json.loads((out / "atlas.json").read_text())
        latest_health = json.loads((out / "projection-health-latest.json").read_text())
        self.assertEqual(canonical["owners"][0]["authorityVersionRef"], version)
        self.assertEqual(canonical["projectionHealth"][0]["health"], HealthState.BROKEN_POINTER)
        self.assertEqual(latest_health[0]["health"], HealthState.BROKEN_POINTER)


class ResultClassificationTests(unittest.TestCase):
    def fixture_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        base = Path(td.name)
        remote = base / "remote.git"
        work = base / "work"
        run("git", "init", "--bare", str(remote))
        run("git", "init", "-b", "main", str(work))
        run("git", "config", "user.email", "atlas@example.invalid", cwd=work)
        run("git", "config", "user.name", "Atlas Fixture", cwd=work)
        run("git", "remote", "add", "origin", str(remote), cwd=work)
        return td, work

    def write_heterogeneous_publication(self, work: Path) -> SourceSpec:
        root = work / "research"
        (root / "authority/publications").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("fixture\n")
        payload = {
            "schemaVersion": 1,
            "kind": "ordivon.research-owner-publication",
            "profile": "LEGACY_EXTRACTION",
            "authorityRef": "authority:fixture",
            "ownerResearchRef": "research-owner:fixture",
            "source": {"kind": "git", "repository": str(work), "authorityBranch": "refs/heads/main", "sourceRevision": "fixture", "corpusRoot": "research"},
            "currentRecovery": {"targetRole": "OWNER_RESEARCH_CORPUS", "locator": "research/README.md"},
            "closeouts": [{
                "researchRef": "research:fixture:heterogeneous",
                "profile": "LEGACY_EXTRACTION",
                "standing": ["CURRENT", "FROZEN"],
                "epistemicVerdict": "ESTABLISHED_IN_SCOPE",
                "evidenceScope": "closeout-wide scope that must not be inherited",
                "resultRefs": ["result:fixture:current", "result:fixture:historical", "result:fixture:unclassified"],
                "closure": [{"scope": "ITEM", "status": "ESTABLISHED"}],
                "residualState": "NONE",
                "reopenPolicy": "UNKNOWN",
            }],
            "statements": [
                {"subjectRef": "result:fixture:current", "predicate": "STANDING:CURRENT", "scope": "RESULT", "value": True},
                {"subjectRef": "result:fixture:current", "predicate": "STANDING:FROZEN", "scope": "RESULT", "value": True},
                {"subjectRef": "result:fixture:current", "predicate": "EPISTEMIC_VERDICT", "scope": "RESULT", "value": "ESTABLISHED_IN_SCOPE"},
                {"subjectRef": "result:fixture:current", "predicate": "EVIDENCE_SCOPE", "scope": "RESULT", "value": "current-result-scope"},
                {"subjectRef": "result:fixture:historical", "predicate": "STANDING:HISTORICAL_PRESERVED", "scope": "RESULT", "value": True},
                {"subjectRef": "result:fixture:historical", "predicate": "STANDING:SUPERSEDED", "scope": "RESULT", "value": True},
                {"subjectRef": "result:fixture:historical", "predicate": "STANDING:WITHDRAWN", "scope": "RESULT", "value": True},
                {"subjectRef": "result:fixture:historical", "predicate": "EPISTEMIC_VERDICT", "scope": "RESULT", "value": "HISTORICAL_RESULT"},
                {"subjectRef": "result:fixture:historical", "predicate": "EVIDENCE_SCOPE", "scope": "RESULT", "value": "historical-result-scope"},
            ],
        }
        content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        digest = hashlib.sha256(content.encode()).hexdigest()
        (root / f"authority/publications/{digest}.json").write_text(content)
        current = {"schemaVersion": 1, "kind": "ordivon.research-owner-current", "authorityRef": "authority:fixture", "ownerResearchRef": "research-owner:fixture", "currentAuthorityVersionRef": "sha256:" + digest, "publication": f"authority/publications/{digest}.json"}
        (root / "authority/CURRENT.json").write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        run("git", "add", ".", cwd=work)
        run("git", "commit", "-m", "heterogeneous", cwd=work)
        run("git", "push", "origin", "main", cwd=work)
        return SourceSpec("research-owner:fixture", "authority:fixture", str(work), str(work.parent / "remote.git"), "refs/heads/main", "research")

    def test_result_standing_is_per_result_not_closeout_inherited(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        spec = self.write_heterogeneous_publication(work)
        projection = Atlas([spec]).build()
        rows = {row["resultRef"]: row for row in projection["results"]}
        self.assertEqual(rows["result:fixture:current"]["classificationHealth"], "EXPLICIT")
        self.assertEqual(rows["result:fixture:current"]["standing"], ["CURRENT", "FROZEN"])
        self.assertEqual(rows["result:fixture:current"]["evidenceScope"], "current-result-scope")
        self.assertEqual(rows["result:fixture:historical"]["standing"], ["HISTORICAL_PRESERVED", "SUPERSEDED", "WITHDRAWN"])
        self.assertNotIn("CURRENT", rows["result:fixture:historical"]["standing"])
        self.assertEqual(rows["result:fixture:historical"]["evidenceScope"], "historical-result-scope")

    def test_unclassified_result_fails_closed_instead_of_inheriting_closeout(self) -> None:
        td, work = self.fixture_repo(); self.addCleanup(td.cleanup)
        spec = self.write_heterogeneous_publication(work)
        row = next(row for row in Atlas([spec]).build()["results"] if row["resultRef"] == "result:fixture:unclassified")
        self.assertEqual(row["classificationHealth"], "UNKNOWN")
        self.assertEqual(row["standing"], [])
        self.assertIsNone(row["epistemicVerdict"])
        self.assertIsNone(row["evidenceScope"])
