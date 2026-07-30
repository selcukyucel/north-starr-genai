from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # Dependency-free local runs still exercise the core validator.
    Draft202012Validator = None


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
HASH = "sha256:" + "a" * 64


@unittest.skipUnless(Draft202012Validator, "jsonschema is not installed")
class SchemaContractTests(unittest.TestCase):
    def schema(self, name: str) -> dict:
        return json.loads((SCHEMAS / name).read_text())

    def test_all_schemas_are_draft_2020_12(self) -> None:
        for path in sorted(SCHEMAS.glob("*.schema.json")):
            with self.subTest(path=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_architecture_requires_typed_decisions(self) -> None:
        decision = {
            "decision_id": "shape-1",
            "title": "System shape",
            "value": "governed_workflow",
            "selection_status": "proposed",
            "rationale": "Known stages and approvals remain explicit.",
            "evidence_refs": ["CLAIM-1"],
        }
        cards = {
            name: {
                "summary": "Example",
                "decisions": [decision],
                "evidence_refs": ["CLAIM-1"],
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
            "status": "proposed",
            "source_hashes": [HASH],
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
                {
                    "name": "deterministic_software",
                    "disposition": "conditional",
                    "rationale": "Use where fixed rules suffice.",
                },
                {
                    "name": "multi_agent",
                    "disposition": "rejected",
                    "rationale": "No separate task boundary.",
                },
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
            "human_boundary": "A named human must accept this proposal.",
        }
        Draft202012Validator(self.schema("architecture-proposal.schema.json")).validate(value)
        value["cards"]["system_shape"]["decisions"] = {}
        self.assertTrue(
            list(
                Draft202012Validator(
                    self.schema("architecture-proposal.schema.json")
                ).iter_errors(value)
            )
        )

    def test_technology_stack_models_layered_components(self) -> None:
        component = {
            "selection_status": "spike_required",
            "category": "portable_ai_sdk",
            "selected_candidate": None,
            "rationale": "Capability evidence is still required.",
            "evidence_refs": ["CLAIM-1"],
        }
        value = {
            "schema_version": "1.0.0",
            "artifact_type": "technology_stack_decision",
            "engagement_id": "example",
            "generated_at": "2026-07-29T12:00:00Z",
            "status": "proposed",
            "source_hashes": [HASH],
            "runtime": {
                "language": "Python",
                "deployment_target": None,
                "selection_status": "spike_required",
            },
            "sdk_decision": {
                "category": "agent_sdk",
                "selection_status": "spike_required",
                "selected_candidate": None,
                "rationale": "A bounded tool loop may add value.",
                "requirements": ["tool calling", "MCP"],
                "candidates": [],
            },
            "components": {
                name: dict(component)
                for name in (
                    "provider_client",
                    "structured_output_validation",
                    "orchestration",
                    "workflow_runtime",
                    "mcp_integration",
                    "evaluation",
                    "tracing",
                    "secrets",
                    "persistence",
                )
            },
            "model_decision": {
                "selection_status": "benchmark_required",
                "selected_model": None,
                "requirements": {
                    "quality": "task benchmark required",
                    "p50_latency": None,
                    "p95_latency": None,
                    "cost": "cost per successful outcome",
                    "context": None,
                    "capabilities": ["structured_output", "tool_calling"],
                    "tool_behavior": "bounded and evaluated",
                    "portability": "preferred",
                    "data_region": None,
                    "snapshot_pinning": "required after selection",
                },
                "benchmark_plan": ["Run representative gold and unsafe cases."],
            },
            "platform_components": {},
            "assumptions": [],
            "open_questions": [],
            "human_boundary": "This stack is proposed, not approved.",
        }
        Draft202012Validator(self.schema("technology-stack.schema.json")).validate(value)

    def test_tool_registry_can_represent_an_unnamed_mcp_capability(self) -> None:
        value = {
            "schema_version": "1.0.0",
            "artifact_type": "tool_registry",
            "engagement_id": "example",
            "generated_at": "2026-07-29T12:00:00Z",
            "status": "partial",
            "source_hashes": [HASH],
            "servers": [
                {
                    "server_id": "mentioned-server-1",
                    "name": None,
                    "kind": "mcp",
                    "capture_status": "mentioned",
                    "endpoint": None,
                    "transport": None,
                    "owner": None,
                    "trust_boundary": None,
                    "authentication": {"method": None, "scopes": []},
                    "tenant_boundary": None,
                    "version_policy": None,
                    "tools": [
                        {
                            "tool_id": "mentioned-tool-1",
                            "capture_status": "mentioned",
                            "name": None,
                            "purpose": None,
                            "authoritative_source": None,
                            "action_class": "unknown",
                            "allowed_actors": [],
                            "approval_required": None,
                            "timeout_ms": None,
                            "retry_policy": None,
                            "idempotency": None,
                            "quota": None,
                            "failure_behavior": None,
                            "data_classification": [],
                            "result_sanitization": None,
                            "audit_fields": [],
                            "contract_tests": [],
                            "evidence_refs": ["CLAIM-1"],
                            "unknown_fields": ["name", "purpose", "authority"],
                        }
                    ],
                    "evidence_refs": ["CLAIM-1"],
                    "open_questions": ["What server and tool were intended?"],
                    "unknown_fields": ["name", "endpoint", "transport", "owner"],
                }
            ],
            "human_boundary": "No tool authority is granted.",
        }
        Draft202012Validator(self.schema("tool-registry.schema.json")).validate(value)


if __name__ == "__main__":
    unittest.main()
