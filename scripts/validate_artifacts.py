#!/usr/bin/env python3
"""Dependency-free validation for North Starr handoffs and artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DISCOVERY_QUESTIONS = [
    ("INTAKE-001", "What problem are we trying to solve, and who is affected?"),
    ("INTAKE-002", "How is this work handled today, from start to finish?"),
    ("INTAKE-003", "If this succeeds, what should improve, and how would you notice?"),
    ("INTAKE-004", "Who will use, operate, approve, or be affected by the system?"),
    ("INTAKE-005", "What everyday, difficult, and unsafe examples should it handle?"),
    ("INTAKE-006", "What must the first release do, and deliberately leave out?"),
    (
        "INTAKE-007",
        "What information and systems are needed, and which sources are authoritative?",
    ),
    ("INTAKE-008", "What may each user see or do, and what must remain out of reach?"),
    (
        "INTAKE-009",
        "What could go wrong, what must never happen, and what should happen under uncertainty or failure?",
    ),
    ("INTAKE-010", "What makes a result correct, useful, complete, and testable?"),
    (
        "INTAKE-011",
        "What response time, usage, availability, budget, and delivery constraints apply?",
    ),
    (
        "INTAKE-012",
        "Who owns the outcome, operation, remaining risk, and authority to stop or restore the service?",
    ),
]

HANDOFF_REQUIRED = {
    "schema_version",
    "export_type",
    "handoff_type",
    "generated_at",
    "engagement_id",
    "source_hashes",
    "problem",
    "outcome",
    "mvp_scope",
    "architecture_profile",
    "constraints",
    "risks",
    "evaluation_examples",
    "open_questions",
    "artifact_references",
    "recommended_entrypoint",
    "human_boundary",
}

ARTIFACT_REQUIRED: dict[str, set[str]] = {
    "project_context": {
        "schema_version",
        "generated_at",
        "project",
        "commands",
        "stack",
        "modules",
        "external_systems",
        "ai_components",
        "mcp_servers",
        "quality_controls",
        "risks",
        "unknowns",
        "evidence",
        "source_hashes",
    },
    "discovery": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "status",
        "questions",
        "source_hashes",
        "human_boundary",
    },
    "intake_validation": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "status",
        "source_artifacts",
        "facts",
        "inferences",
        "assumptions",
        "unknowns",
        "deferred",
        "conflicts",
        "systems_and_tools",
        "blocking_questions",
        "freshness",
        "human_boundary",
    },
    "assessment": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "status",
        "source_hashes",
        "problem_summary",
        "recommended_shape",
        "build_strategy",
        "alternatives",
        "required_specialists",
        "risks",
        "assumptions",
        "blocking_questions",
        "model_selection_status",
        "human_boundary",
    },
    "technology_stack_decision": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "status",
        "source_hashes",
        "runtime",
        "sdk_decision",
        "model_decision",
        "platform_components",
        "assumptions",
        "open_questions",
        "human_boundary",
    },
    "tool_registry": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "status",
        "source_hashes",
        "servers",
        "human_boundary",
    },
    "architecture_proposal": {
        "schema_version",
        "proposal_id",
        "engagement_id",
        "generated_at",
        "status",
        "source_hashes",
        "cards",
        "recommended_shape",
        "multi_agent_valid",
        "model_selection_status",
        "artifact_refs",
        "alternatives",
        "assumptions",
        "open_questions",
        "approval",
        "human_boundary",
    },
    "artifact_manifest": {
        "schema_version",
        "engagement_id",
        "generated_at",
        "source_artifacts",
        "artifacts",
        "stale",
        "recommended_next_step",
    },
}


class ValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: root must be an object")
    return value


def require_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - value.keys())
    if missing:
        raise ValidationError(f"{label}: missing required fields: {', '.join(missing)}")


def require_exact_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    require_keys(value, required, label)
    extra = sorted(value.keys() - required)
    if extra:
        raise ValidationError(f"{label}: unsupported fields: {', '.join(extra)}")


def require_rfc3339(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise ValidationError(f"{label}: expected RFC3339 timestamp")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{label}: expected RFC3339 timestamp") from exc


def require_hash(value: Any, label: str) -> None:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise ValidationError(f"{label}: expected sha256:<64 lowercase hex characters>")


def require_hash_list(value: Any, label: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise ValidationError(f"{label}: expected {qualifier} of hashes")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label}: duplicate hashes are not allowed")
    for index, item in enumerate(value):
        require_hash(item, f"{label}[{index}]")


def validate_handoff(path: Path) -> None:
    value = load_json(path)
    require_exact_keys(value, HANDOFF_REQUIRED, str(path))
    expected = {
        "schema_version": "0.1.0",
        "export_type": "north_starr_handoff",
        "handoff_type": "north_starr_handoff",
        "recommended_entrypoint": "assess",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise ValidationError(f"{path}: {key} must be {expected_value!r}")
    require_rfc3339(value["generated_at"], f"{path}: generated_at")
    require_hash_list(value["source_hashes"], f"{path}: source_hashes", allow_empty=True)
    for field in ("problem", "outcome", "mvp_scope"):
        validate_vignola_response(value[field], f"{path}: {field}")
    for field in ("constraints", "risks", "evaluation_examples", "open_questions"):
        if not isinstance(value[field], list):
            raise ValidationError(f"{path}: {field} must be an array")
        for index, response in enumerate(value[field]):
            validate_vignola_response(response, f"{path}: {field}[{index}]")
    if not isinstance(value["artifact_references"], list):
        raise ValidationError(f"{path}: artifact_references must be an array")
    for index, ref in enumerate(value["artifact_references"]):
        if not isinstance(ref, dict):
            raise ValidationError(f"{path}: artifact_references[{index}] must be an object")
        require_exact_keys(
            ref,
            {"type", "relative_path", "content_hash"},
            f"{path}: artifact_references[{index}]",
        )
        if not all(isinstance(ref[key], str) and ref[key] for key in ("type", "relative_path")):
            raise ValidationError(f"{path}: artifact_references[{index}] has empty fields")
        require_hash(ref["content_hash"], f"{path}: artifact_references[{index}].content_hash")
    profile = value["architecture_profile"]
    if profile is not None:
        if not isinstance(profile, dict):
            raise ValidationError(f"{path}: architecture_profile must be an object or null")
        require_exact_keys(
            profile,
            {"recommendation", "cards", "source_state_hash"},
            f"{path}: architecture_profile",
        )
        if not isinstance(profile["recommendation"], dict) or not isinstance(profile["cards"], dict):
            raise ValidationError(f"{path}: architecture_profile objects are malformed")
        require_hash(profile["source_state_hash"], f"{path}: architecture_profile.source_state_hash")
    if not isinstance(value["human_boundary"], str) or not value["human_boundary"].strip():
        raise ValidationError(f"{path}: human_boundary must be non-empty")


def validate_vignola_response(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{label}: expected response object")
    require_exact_keys(value, {"question", "status", "answer", "source_hashes"}, label)
    if not isinstance(value["question"], str) or not value["question"].strip():
        raise ValidationError(f"{label}: question must be non-empty")
    if value["status"] not in {"answered", "unanswered", "unknown", "deferred", "conflicted"}:
        raise ValidationError(f"{label}: unsupported response status")
    if value["status"] == "answered" and (
        not isinstance(value["answer"], str) or not value["answer"].strip()
    ):
        raise ValidationError(f"{label}: answered response needs answer text")
    if value["answer"] is not None and not isinstance(value["answer"], str):
        raise ValidationError(f"{label}: answer must be a string or null")
    require_hash_list(value["source_hashes"], f"{label}.source_hashes", allow_empty=True)


def validate_vignola_bundle(path: Path) -> list[str]:
    root = path if path.is_dir() else path.parent
    handoff_path = root / "north-starr-handoff.json"
    profile_path = root / "architecture-profile.json"
    summary_path = root / "client-summary.json"
    for required_path in (handoff_path, profile_path, summary_path):
        if not required_path.is_file():
            raise ValidationError(f"{root}: missing {required_path.name}")

    validate_handoff(handoff_path)
    handoff = load_json(handoff_path)
    profile_export = load_json(profile_path)
    summary = load_json(summary_path)

    for label, value, export_type in (
        (profile_path, profile_export, "architecture_profile"),
        (summary_path, summary, "client_summary"),
    ):
        if value.get("schema_version") != "0.1.0":
            raise ValidationError(f"{label}: schema_version must be '0.1.0'")
        if value.get("export_type") != export_type:
            raise ValidationError(f"{label}: export_type must be {export_type!r}")

    profile = profile_export.get("profile")
    if not isinstance(profile, dict):
        raise ValidationError(f"{profile_path}: profile must be an object")
    require_keys(
        profile,
        {
            "engagement_id",
            "status",
            "source_state_hash",
            "cards",
            "recommendation",
            "human_boundary",
        },
        f"{profile_path}: profile",
    )
    if profile["engagement_id"] != handoff["engagement_id"]:
        raise ValidationError(f"{root}: handoff and architecture profile engagement IDs differ")
    require_hash(profile["source_state_hash"], f"{profile_path}: profile.source_state_hash")
    if profile["status"] not in {"draft", "finalized", "stale"}:
        raise ValidationError(f"{profile_path}: profile.status is invalid")

    embedded_profile = handoff.get("architecture_profile")
    if not isinstance(embedded_profile, dict):
        raise ValidationError(f"{handoff_path}: architecture_profile must be an object for a bundle")
    for key in ("recommendation", "cards", "source_state_hash"):
        if embedded_profile.get(key) != profile.get(key):
            raise ValidationError(f"{root}: handoff architecture_profile.{key} differs from export")

    responses = summary.get("responses")
    if not isinstance(responses, list) or len(responses) != 12:
        raise ValidationError(f"{summary_path}: responses must contain exactly 12 items")
    for index, (_, expected_question) in enumerate(DISCOVERY_QUESTIONS):
        response = responses[index]
        if not isinstance(response, dict):
            raise ValidationError(f"{summary_path}: responses[{index}] must be an object")
        if response.get("question") != expected_question:
            raise ValidationError(f"{summary_path}: responses[{index}] differs from the catalogue")
        status = response.get("status")
        if status not in {"answered", "unknown", "deferred"}:
            raise ValidationError(f"{summary_path}: responses[{index}].status is invalid")
        if status == "answered" and (
            not isinstance(response.get("answer"), str) or not response["answer"].strip()
        ):
            raise ValidationError(f"{summary_path}: answered response {index} needs answer text")
        require_hash_list(
            response.get("source_hashes"),
            f"{summary_path}: responses[{index}].source_hashes",
            allow_empty=True,
        )
    if not isinstance(summary.get("human_boundary"), str) or not summary["human_boundary"].strip():
        raise ValidationError(f"{summary_path}: human_boundary must be non-empty")
    warnings = []
    for ref in handoff["artifact_references"]:
        referenced_path = root / ref["relative_path"]
        if not referenced_path.is_file():
            warnings.append(
                f"referenced evidence artifact is not included: {ref['relative_path']}"
            )
    if "engagement_id" not in summary:
        warnings.append("client-summary.json has no engagement_id for cross-file binding")
    return warnings


def validate_discovery(value: dict[str, Any], label: str) -> None:
    questions = value.get("questions")
    if not isinstance(questions, list) or len(questions) != 12:
        raise ValidationError(f"{label}: questions must contain exactly 12 items")
    for index, (expected_id, expected_text) in enumerate(DISCOVERY_QUESTIONS):
        question = questions[index]
        if not isinstance(question, dict):
            raise ValidationError(f"{label}: questions[{index}] must be an object")
        if question.get("question_id") != expected_id:
            raise ValidationError(f"{label}: questions[{index}].question_id must be {expected_id}")
        if question.get("question") != expected_text:
            raise ValidationError(f"{label}: questions[{index}] text differs from the catalogue")
        if question.get("status") not in {"answered", "unknown", "deferred"}:
            raise ValidationError(f"{label}: questions[{index}].status is invalid")
        if question.get("status") == "answered":
            if not isinstance(question.get("answer"), str) or not question["answer"].strip():
                raise ValidationError(f"{label}: answered questions require non-empty answer text")
        for key in ("evidence_refs", "architect_notes"):
            if not isinstance(question.get(key), list):
                raise ValidationError(f"{label}: questions[{index}].{key} must be an array")


def recursively_validate_hash_fields(value: Any, label: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            if key in {"source_hashes", "evidence_hashes", "upstream_hashes", "evidence_refs"}:
                if key == "evidence_refs" and all(
                    isinstance(item, str) and not item.startswith("sha256:") for item in child or []
                ):
                    pass
                else:
                    require_hash_list(child, child_label, allow_empty=True)
            elif key == "sha256":
                require_hash(child, child_label)
            recursively_validate_hash_fields(child, child_label)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            recursively_validate_hash_fields(child, f"{label}[{index}]")


def validate_artifact(path: Path) -> None:
    value = load_json(path)
    artifact_type = value.get("artifact_type")
    if artifact_type not in ARTIFACT_REQUIRED:
        raise ValidationError(f"{path}: unsupported artifact_type {artifact_type!r}")
    require_keys(value, ARTIFACT_REQUIRED[artifact_type] | {"artifact_type"}, str(path))
    if value.get("schema_version") != "1.0.0":
        raise ValidationError(f"{path}: schema_version must be '1.0.0'")
    if artifact_type == "discovery":
        validate_discovery(value, str(path))
    if artifact_type in {"intake_validation", "assessment"}:
        blockers = value.get("blocking_questions", [])
        if not isinstance(blockers, list) or len(blockers) > 3:
            raise ValidationError(f"{path}: blocking_questions may contain at most 3 items")
    if artifact_type == "intake_validation":
        for index, source in enumerate(value.get("source_artifacts", [])):
            if not isinstance(source, dict) or not all(
                key in source for key in ("path", "sha256", "role", "evidence_level")
            ):
                raise ValidationError(
                    f"{path}: source_artifacts[{index}] lacks provenance fields"
                )
        freshness = value.get("freshness")
        if not isinstance(freshness, dict) or freshness.get("status") not in {
            "current",
            "stale",
            "unknown",
        }:
            raise ValidationError(f"{path}: freshness.status is invalid")
    if artifact_type in {"architecture_proposal", "technology_stack_decision"}:
        questions = value.get("open_questions", [])
        if not isinstance(questions, list) or len(questions) > 3:
            raise ValidationError(f"{path}: open_questions may contain at most 3 items")
    if artifact_type == "assessment" and value.get("model_selection_status") != "benchmark_required":
        raise ValidationError(f"{path}: assessment model_selection_status must be benchmark_required")
    if artifact_type == "architecture_proposal":
        if value.get("model_selection_status") != "benchmark_required":
            raise ValidationError(
                f"{path}: proposed architecture model_selection_status must be benchmark_required"
            )
        if value.get("status") == "accepted":
            approval = value.get("approval", {})
            required = ("approver", "decided_at", "scope", "residual_risk_owner")
            if approval.get("status") != "accepted" or any(not approval.get(key) for key in required):
                raise ValidationError(f"{path}: accepted proposal requires complete named approval")
        cards = value.get("cards")
        expected_cards = {
            "goal_scope",
            "system_shape",
            "information_tools",
            "human_control",
            "quality_operations",
            "runtime_technology",
        }
        if not isinstance(cards, dict) or set(cards) != expected_cards:
            raise ValidationError(f"{path}: architecture proposal requires exactly six design cards")
        for name, card in cards.items():
            decisions = card.get("decisions") if isinstance(card, dict) else None
            if not isinstance(decisions, list) or not decisions:
                raise ValidationError(f"{path}: card {name} requires typed decision records")
            for index, decision in enumerate(decisions):
                required = {
                    "decision_id",
                    "title",
                    "value",
                    "selection_status",
                    "rationale",
                    "evidence_refs",
                }
                if not isinstance(decision, dict) or not required.issubset(decision):
                    raise ValidationError(
                        f"{path}: card {name} decision {index} is incomplete"
                    )
    if artifact_type == "technology_stack_decision":
        components = value.get("components")
        expected_components = {
            "provider_client",
            "structured_output_validation",
            "orchestration",
            "workflow_runtime",
            "mcp_integration",
            "evaluation",
            "tracing",
            "secrets",
            "persistence",
        }
        if not isinstance(components, dict) or set(components) != expected_components:
            raise ValidationError(f"{path}: technology stack requires nine component decisions")
        if value.get("status") == "proposed":
            model = value.get("model_decision", {})
            if model.get("selection_status") != "benchmark_required":
                raise ValidationError(f"{path}: proposed model must be benchmark_required")
    if artifact_type == "tool_registry":
        for server_index, server in enumerate(value.get("servers", [])):
            if not isinstance(server, dict) or "unknown_fields" not in server:
                raise ValidationError(
                    f"{path}: servers[{server_index}] must make unknown fields explicit"
                )
            for tool_index, tool in enumerate(server.get("tools", [])):
                if not isinstance(tool, dict) or not all(
                    field in tool for field in ("capture_status", "unknown_fields")
                ):
                    raise ValidationError(
                        f"{path}: servers[{server_index}].tools[{tool_index}] lacks capture metadata"
                    )
    recursively_validate_hash_fields(value)


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_manifest_path(manifest_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    project_root = manifest_path.parent.parent
    return (project_root / candidate).resolve()


def validate_manifest(path: Path) -> None:
    value = load_json(path)
    if value.get("artifact_type") != "artifact_manifest":
        raise ValidationError(f"{path}: artifact_type must be artifact_manifest")
    validate_artifact(path)
    for section in ("source_artifacts", "artifacts"):
        for index, ref in enumerate(value[section]):
            if not isinstance(ref, dict):
                raise ValidationError(f"{path}: {section}[{index}] must be an object")
            target = resolve_manifest_path(path, ref.get("path", ""))
            if not target.is_file():
                raise ValidationError(f"{path}: referenced file does not exist: {target}")
            expected = ref.get("sha256")
            require_hash(expected, f"{path}: {section}[{index}].sha256")
            actual = file_hash(target)
            if actual != expected:
                raise ValidationError(
                    f"{path}: stale hash for {target}: expected {expected}, actual {actual}"
                )


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise ValidationError(f"{path}: missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValidationError(f"{path}: unterminated YAML frontmatter") from exc
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith(" "):
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: malformed frontmatter line: {line}")
        key, raw = line.split(":", 1)
        fields[key.strip()] = raw.strip().strip("\"'")
    return fields


def validate_repo(root: Path) -> None:
    plugin_path = root / ".codex-plugin" / "plugin.json"
    plugin = load_json(plugin_path)
    require_keys(
        plugin,
        {"name", "version", "description", "author", "skills", "interface"},
        str(plugin_path),
    )
    if plugin.get("name") != "north-starr-genai":
        raise ValidationError(f"{plugin_path}: unexpected plugin name")
    if plugin.get("skills") != "./skills/":
        raise ValidationError(f"{plugin_path}: skills path must be './skills/'")

    hook_config = load_json(root / "hooks" / "hooks.json")
    if "hooks" not in hook_config:
        raise ValidationError(f"{root / 'hooks/hooks.json'}: missing hooks")

    names: set[str] = set()
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if len(skill_files) < 26:
        raise ValidationError(f"{root}: expected at least 26 skills, found {len(skill_files)}")
    allowed_frontmatter = {"name", "description", "license", "allowed-tools", "metadata"}
    for path in skill_files:
        fields = parse_skill_frontmatter(path)
        unexpected = sorted(set(fields) - allowed_frontmatter)
        if unexpected:
            raise ValidationError(
                f"{path}: unsupported frontmatter fields: {', '.join(unexpected)}"
            )
        name = fields.get("name", "")
        description = fields.get("description", "")
        if not SKILL_NAME_RE.fullmatch(name):
            raise ValidationError(f"{path}: invalid or missing name")
        if name in names:
            raise ValidationError(f"{path}: duplicate skill name {name}")
        names.add(name)
        if not description:
            raise ValidationError(f"{path}: missing description")
        if path.parent.name != name:
            raise ValidationError(f"{path}: directory and skill name differ")

    schema_files = sorted((root / "schemas").glob("*.schema.json"))
    if len(schema_files) < 7:
        raise ValidationError(f"{root}: expected the North Starr artifact schema set")
    for path in schema_files:
        schema = load_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValidationError(f"{path}: schema draft must be 2020-12")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("handoff", "bundle", "artifact", "manifest"):
        command = subparsers.add_parser(name)
        command.add_argument("path", type=Path)
    repo = subparsers.add_parser("repo")
    repo.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    warnings: list[str] = []
    try:
        if args.command == "handoff":
            validate_handoff(args.path.resolve())
        elif args.command == "bundle":
            warnings = validate_vignola_bundle(args.path.resolve())
        elif args.command == "artifact":
            validate_artifact(args.path.resolve())
        elif args.command == "manifest":
            validate_manifest(args.path.resolve())
        elif args.command == "repo":
            validate_repo(args.path.resolve())
        else:
            raise AssertionError(args.command)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
