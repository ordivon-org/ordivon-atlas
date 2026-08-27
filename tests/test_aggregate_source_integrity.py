from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ordivon_atlas.atlas import Atlas, HealthState, SourceSpec


def run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout.strip()


class AggregateSourceIntegrityTests(unittest.TestCase):
    def fixture(self, *, broken_manifest_digest: bool = False, broken_anchor_digest: bool = False):
        td = tempfile.TemporaryDirectory()
        work = Path(td.name) / "owner"
        run("git", "init", "-b", "main", str(work))
        run("git", "config", "user.email", "aggregate@example.invalid", cwd=work)
        run("git", "config", "user.name", "Aggregate Fixture", cwd=work)
        root = work / "research"
        root.mkdir(parents=True)
        (root / "README.md").write_text("aggregate owner recovery\n")
        capsule = root / "CAPSULE.md"
        capsule.write_text("exact capsule\n")
        run("git", "add", ".", cwd=work)
        run("git", "commit", "-m", "anchor", cwd=work)
        anchor_revision = run("git", "rev-parse", "HEAD", cwd=work)
        anchor_bytes = capsule.read_bytes()
        anchor_digest = "sha256:" + hashlib.sha256(anchor_bytes).hexdigest()
        if broken_anchor_digest:
            anchor_digest = "sha256:" + "0" * 64
        authority = "authority:ordivon:research-owner:aggregate"
        owner = "research-owner:aggregate"
        manifest = {
            "schemaVersion": 1,
            "kind": "fixture.aggregate-manifest",
            "authorityRef": authority,
            "ownerResearchRef": owner,
            "anchors": [{
                "role": "CAPSULE",
                "revision": anchor_revision,
                "path": "research/CAPSULE.md",
                "bytes": len(anchor_bytes),
                "sha256": anchor_digest,
            }],
        }
        auth = root / "authority"
        (auth / "publications").mkdir(parents=True)
        manifest_path = auth / "MANIFEST.json"
        manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        manifest_path.write_bytes(manifest_bytes)
        manifest_digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
        declared_manifest_digest = "sha256:" + "1" * 64 if broken_manifest_digest else manifest_digest
        publication = {
            "schemaVersion": 1,
            "kind": "ordivon.research-owner-publication",
            "profile": "MULTI_REF_AGGREGATE",
            "authorityRef": authority,
            "ownerResearchRef": owner,
            "source": {
                "kind": "git-multi-ref-aggregate",
                "aggregateManifest": "research/authority/MANIFEST.json",
                "aggregateManifestDigest": declared_manifest_digest,
            },
            "currentRecovery": {"targetRole": "OWNER_RESEARCH_CORPUS", "locator": "research/README.md"},
            "statements": [],
            "closeouts": [],
        }
        pub_bytes = (json.dumps(publication, indent=2, sort_keys=True) + "\n").encode()
        pub_digest = hashlib.sha256(pub_bytes).hexdigest()
        (auth / f"publications/{pub_digest}.json").write_bytes(pub_bytes)
        current = {
            "schemaVersion": 1,
            "kind": "ordivon.research-owner-current",
            "authorityRef": authority,
            "ownerResearchRef": owner,
            "currentAuthorityVersionRef": "sha256:" + pub_digest,
            "publication": f"authority/publications/{pub_digest}.json",
        }
        (auth / "CURRENT.json").write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        run("git", "add", ".", cwd=work)
        run("git", "commit", "-m", "publication", cwd=work)
        spec = SourceSpec(owner, authority, str(work), None, "refs/heads/main", "research", transportMode="local_git")
        return td, spec

    def test_exact_aggregate_manifest_and_anchor_are_current(self):
        td, spec = self.fixture(); self.addCleanup(td.cleanup)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.CURRENT_TO_SOURCE)

    def test_aggregate_manifest_digest_mismatch_fails_closed(self):
        td, spec = self.fixture(broken_manifest_digest=True); self.addCleanup(td.cleanup)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.BROKEN_POINTER)
        self.assertIn("DECLARED_SOURCE_INTEGRITY_INVALID", obs.reason or "")
        self.assertIn("manifest digest mismatch", obs.reason or "")

    def test_aggregate_anchor_digest_mismatch_fails_closed(self):
        td, spec = self.fixture(broken_anchor_digest=True); self.addCleanup(td.cleanup)
        obs = Atlas([spec]).observe(spec)
        self.assertEqual(obs.health, HealthState.BROKEN_POINTER)
        self.assertIn("DECLARED_SOURCE_INTEGRITY_INVALID", obs.reason or "")
        self.assertIn("anchor 0 digest mismatch", obs.reason or "")


if __name__ == "__main__":
    unittest.main()
