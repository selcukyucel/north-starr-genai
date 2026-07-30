from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_artifacts", ROOT / "scripts" / "validate_artifacts.py"
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def sha(char: str) -> str:
    return "sha256:" + char * 64


def response(question: str, answer: str = "Example answer") -> dict:
    return {
        "question": question,
        "status": "answered",
        "answer": answer,
        "source_hashes": [sha("a")],
    }


class HandoffTests(unittest.TestCase):
    def handoff(self) -> dict:
        return {
            "schema_version": "0.1.0",
            "export_type": "north_starr_handoff",
            "handoff_type": "north_starr_handoff",
            "generated_at": "2026-07-29T12:00:00Z",
            "engagement_id": "example",
            "source_hashes": [sha("a")],
            "problem": response(validator.DISCOVERY_QUESTIONS[0][1]),
            "outcome": response(validator.DISCOVERY_QUESTIONS[2][1]),
            "mvp_scope": response(validator.DISCOVERY_QUESTIONS[5][1]),
            "architecture_profile": None,
            "constraints": [],
            "risks": [],
            "evaluation_examples": [],
            "open_questions": [],
            "artifact_references": [],
            "recommended_entrypoint": "assess",
            "human_boundary": "A human must approve architecture and implementation.",
        }

    def write(self, value: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(value, handle)
        handle.close()
        return Path(handle.name)

    def test_valid_handoff(self) -> None:
        validator.validate_handoff(self.write(self.handoff()))

    def test_rejects_bad_hash(self) -> None:
        value = self.handoff()
        value["source_hashes"] = ["not-a-hash"]
        with self.assertRaises(validator.ValidationError):
            validator.validate_handoff(self.write(value))


class BundleTests(unittest.TestCase):
    def bundle(self) -> Path:
        root = Path(tempfile.mkdtemp())
        recommendation = {
            "system_pattern": "governed_workflow",
            "model_selection": "benchmark_required",
        }
        cards = {"goal_scope": {"status": "complete"}}
        source_state_hash = sha("b")
        profile = {
            "engagement_id": "example",
            "status": "finalized",
            "source_state_hash": source_state_hash,
            "cards": cards,
            "recommendation": recommendation,
            "human_boundary": "This recommendation is not implementation authority.",
        }
        profile_export = {
            "schema_version": "0.1.0",
            "export_type": "architecture_profile",
            "exported_at": "2026-07-29T12:00:00Z",
            "engagement_id": "example",
            "profile": profile,
        }
        summary = {
            "schema_version": "0.1.0",
            "export_type": "client_summary",
            "exported_at": "2026-07-29T12:00:00Z",
            "engagement": {"title": "Example", "client_organization": "Example"},
            "responses": [
                {
                    "question": question,
                    "status": "answered",
                    "answer": f"Answer {index + 1}",
                    "source_hashes": [sha("c")],
                }
                for index, (_, question) in enumerate(validator.DISCOVERY_QUESTIONS)
            ],
            "review": {"groups": []},
            "human_boundary": "Client review is still required.",
        }
        handoff = {
            "schema_version": "0.1.0",
            "export_type": "north_starr_handoff",
            "handoff_type": "north_starr_handoff",
            "generated_at": "2026-07-29T12:00:00Z",
            "engagement_id": "example",
            "source_hashes": [sha("c")],
            "problem": response(validator.DISCOVERY_QUESTIONS[0][1]),
            "outcome": response(validator.DISCOVERY_QUESTIONS[2][1]),
            "mvp_scope": response(validator.DISCOVERY_QUESTIONS[5][1]),
            "architecture_profile": {
                "recommendation": recommendation,
                "cards": cards,
                "source_state_hash": source_state_hash,
            },
            "constraints": [],
            "risks": [],
            "evaluation_examples": [],
            "open_questions": [],
            "artifact_references": [],
            "recommended_entrypoint": "assess",
            "human_boundary": "A human must approve architecture and implementation.",
        }
        for name, value in (
            ("architecture-profile.json", profile_export),
            ("client-summary.json", summary),
            ("north-starr-handoff.json", handoff),
        ):
            (root / name).write_text(json.dumps(value))
        return root

    def test_valid_three_file_bundle(self) -> None:
        validator.validate_vignola_bundle(self.bundle())

    def test_rejects_profile_drift(self) -> None:
        root = self.bundle()
        path = root / "architecture-profile.json"
        value = json.loads(path.read_text())
        value["profile"]["recommendation"]["system_pattern"] = "multi_agent"
        path.write_text(json.dumps(value))
        with self.assertRaises(validator.ValidationError):
            validator.validate_vignola_bundle(root)


class DiscoveryTests(unittest.TestCase):
    def discovery(self) -> dict:
        questions = []
        for index, (question_id, text) in enumerate(validator.DISCOVERY_QUESTIONS):
            questions.append(
                {
                    "question_id": question_id,
                    "question": text,
                    "status": "answered" if index < 6 else "deferred",
                    "answer": f"Answer {index + 1}" if index < 6 else None,
                    "evidence_refs": [],
                    "architect_notes": [],
                }
            )
        return {
            "schema_version": "1.0.0",
            "artifact_type": "discovery",
            "engagement_id": "example",
            "generated_at": "2026-07-29T12:00:00Z",
            "status": "provisional",
            "questions": questions,
            "source_hashes": [],
            "human_boundary": "Architecture remains subject to human approval.",
        }

    def write(self, value: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(value, handle)
        handle.close()
        return Path(handle.name)

    def test_exact_twelve_question_catalogue(self) -> None:
        validator.validate_artifact(self.write(self.discovery()))

    def test_rejects_reordered_questions(self) -> None:
        value = self.discovery()
        value["questions"][0], value["questions"][1] = value["questions"][1], value["questions"][0]
        with self.assertRaises(validator.ValidationError):
            validator.validate_artifact(self.write(value))


class GovernanceTests(unittest.TestCase):
    def test_accepted_proposal_requires_named_approval(self) -> None:
        cards = {
            name: {
                "summary": "Example",
                "decisions": [
                    {
                        "decision_id": f"{name}-1",
                        "title": "Example",
                        "value": "example",
                        "selection_status": "proposed",
                        "rationale": "Example",
                        "evidence_refs": [],
                    }
                ],
                "evidence_refs": [],
                "unknowns": [],
            }
            for name in (
                "goal_scope",
                "system_shape",
                "information_tools",
                "human_control",
                "quality_operations",
                "runtime_technology",
            )
        }
        value = {
            "schema_version": "1.0.0",
            "artifact_type": "architecture_proposal",
            "proposal_id": "proposal-1",
            "engagement_id": "example",
            "generated_at": "2026-07-29T12:00:00Z",
            "status": "accepted",
            "source_hashes": [sha("a")],
            "cards": cards,
            "recommended_shape": "governed_workflow",
            "multi_agent_valid": False,
            "model_selection_status": "benchmark_required",
            "artifact_refs": {
                "technology_stack": ".north-starr/technology-stack.json",
                "tool_registry": ".north-starr/tool-registry.json",
                "manifest": ".north-starr/manifest.json",
            },
            "alternatives": [
                {"name": "deterministic", "disposition": "conditional", "rationale": "Example"},
                {"name": "multi-agent", "disposition": "rejected", "rationale": "No boundary"},
            ],
            "assumptions": [],
            "open_questions": [],
            "approval": {
                "status": "not_requested",
                "approver": None,
                "decided_at": None,
                "scope": None,
                "evidence_hashes": [],
                "residual_risk_owner": None,
            },
            "human_boundary": "No implementation authority.",
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            json.dump(value, handle)
            path = Path(handle.name)
        with self.assertRaises(validator.ValidationError):
            validator.validate_artifact(path)


if __name__ == "__main__":
    unittest.main()
