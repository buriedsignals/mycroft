#!/usr/bin/env python3
"""Validate Mycroft perspective-audit JSON and its cross-record lineage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ID_PATTERNS = {
    "audit_id": re.compile(r"^PA-[A-Za-z0-9._-]+$"),
    "evidence": re.compile(r"^E-[A-Za-z0-9._-]+$"),
    "perspective": re.compile(r"^P-[A-Za-z0-9._-]+$"),
    "summary": re.compile(r"^S-[A-Za-z0-9._-]+$"),
    "draft": re.compile(r"^D-[A-Za-z0-9._-]+$"),
    "finding": re.compile(r"^F-[A-Za-z0-9._-]+$"),
    "gap": re.compile(r"^G-[A-Za-z0-9._-]+$"),
}
EVIDENCE_REF = re.compile(r"^E-[A-Za-z0-9._-]+(?:#[A-Za-z0-9._:-]+)?$")
REVIEW_STATES = {"unreviewed", "in_review", "approved", "rejected"}
CONFIDENCE = {"high", "medium", "low"}
REPRESENTATIVENESS = {"corpus_only", "unknown"}
SUPPORT_TYPES = {"direct", "indirect", "inferred"}
RELATIONS = {"supports", "summarized_as", "merged_into", "propagates_to", "contradicts"}
FINDING_TYPES = {
    "unsupported_assertion",
    "omitted_perspective",
    "overrepresented_perspective",
    "collapsed_disagreement",
    "attribution_drift",
    "certainty_inflation",
    "loaded_language",
    "stereotyping",
    "false_balance",
    "factual_disagreement_as_opinion",
    "other",
}
SEVERITIES = {"info", "warning", "critical"}
GAP_TYPES = {
    "possible_unobserved_viewpoint",
    "missing_source_type",
    "insufficient_corpus",
    "unresolved_disagreement",
    "other",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path, help="Path to perspective-audit.json")
    parser.add_argument(
        "--evidence-bundle",
        type=Path,
        help="Optional Mycroft evidence-bundle.json used to resolve corpus evidence IDs",
    )
    return parser.parse_args()


def load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"{label}: cannot read {path}: {exc}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label}: top-level value must be an object")
        return {}
    return data


def require(mapping: Any, keys: tuple[str, ...], where: str, errors: list[str]) -> bool:
    if not isinstance(mapping, dict):
        errors.append(f"{where}: must be an object")
        return False
    missing = [key for key in keys if key not in mapping]
    if missing:
        errors.append(f"{where}: missing required fields: {', '.join(missing)}")
        return False
    return True


def require_list(value: Any, where: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{where}: must be an array")
        return []
    return value


def require_string(value: Any, where: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}: must be a non-empty string")
        return ""
    return value


def validate_id(value: Any, kind: str, where: str, errors: list[str]) -> str:
    text = require_string(value, where, errors)
    if text and not ID_PATTERNS[kind].fullmatch(text):
        errors.append(f"{where}: invalid {kind} format: {text!r}")
    return text


def evidence_base(ref: str) -> str:
    return ref.split("#", 1)[0]


def validate_evidence_refs(
    refs: Any,
    where: str,
    evidence_ids: set[str],
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    values = require_list(refs, where, errors)
    if nonempty and not values:
        errors.append(f"{where}: must contain at least one evidence reference")
    seen: set[str] = set()
    valid: list[str] = []
    for index, value in enumerate(values):
        item_where = f"{where}[{index}]"
        if not isinstance(value, str) or not EVIDENCE_REF.fullmatch(value):
            errors.append(f"{item_where}: invalid evidence reference: {value!r}")
            continue
        if value in seen:
            errors.append(f"{item_where}: duplicate evidence reference: {value}")
        seen.add(value)
        if evidence_base(value) not in evidence_ids:
            errors.append(f"{item_where}: unresolved corpus evidence ID: {evidence_base(value)}")
        valid.append(value)
    return valid


def validate_ref_list(
    refs: Any,
    where: str,
    allowed: set[str],
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    values = require_list(refs, where, errors)
    if nonempty and not values:
        errors.append(f"{where}: must contain at least one reference")
    seen: set[str] = set()
    valid: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            errors.append(f"{where}[{index}]: reference must be a string")
            continue
        if value in seen:
            errors.append(f"{where}[{index}]: duplicate reference: {value}")
        seen.add(value)
        if value not in allowed:
            errors.append(f"{where}[{index}]: unresolved reference: {value}")
        valid.append(value)
    return valid


def validate_review(value: Any, where: str, errors: list[str]) -> None:
    if not require(value, ("state",), where, errors):
        return
    state = value.get("state")
    if state not in REVIEW_STATES:
        errors.append(f"{where}.state: expected one of {sorted(REVIEW_STATES)}, got {state!r}")


def collect_records(
    data: dict[str, Any],
    key: str,
    kind: str,
    errors: list[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    records = require_list(data.get(key), key, errors)
    objects: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, record in enumerate(records):
        where = f"{key}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where}: must be an object")
            continue
        record_id = validate_id(record.get("id"), kind, f"{where}.id", errors)
        if record_id in ids:
            errors.append(f"{where}.id: duplicate ID: {record_id}")
        ids.add(record_id)
        objects.append(record)
    return objects, ids


def validate_audit(data: dict[str, Any], bundle_ids: set[str] | None) -> list[str]:
    errors: list[str] = []
    required_top = (
        "schema",
        "audit_id",
        "created_at",
        "topic",
        "corpus",
        "perspectives",
        "summaries",
        "draft_sentences",
        "lineage",
        "audit_findings",
        "reporting_gaps",
        "human_review",
    )
    if not require(data, required_top, "audit", errors):
        return errors
    if data.get("schema") != "perspective-audit-v1":
        errors.append("audit.schema: expected 'perspective-audit-v1'")
    validate_id(data.get("audit_id"), "audit_id", "audit.audit_id", errors)
    require_string(data.get("topic"), "audit.topic", errors)
    created_at = require_string(data.get("created_at"), "audit.created_at", errors)
    if created_at:
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("audit.created_at: timestamp must include a timezone")
        except ValueError:
            errors.append("audit.created_at: must be an ISO 8601 date-time")
    validate_review(data.get("human_review"), "audit.human_review", errors)

    corpus = data.get("corpus")
    corpus_required = (
        "description",
        "evidence_ids",
        "included_source_count",
        "included_passage_count",
        "excluded",
        "sampling_notes",
        "deduplication_notes",
        "representativeness_statement",
    )
    evidence_ids: set[str] = set()
    if require(corpus, corpus_required, "audit.corpus", errors):
        require_string(corpus.get("description"), "audit.corpus.description", errors)
        require_string(
            corpus.get("representativeness_statement"),
            "audit.corpus.representativeness_statement",
            errors,
        )
        for field in ("included_source_count", "included_passage_count"):
            value = corpus.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"audit.corpus.{field}: must be a non-negative integer")
        for index, value in enumerate(require_list(corpus.get("evidence_ids"), "audit.corpus.evidence_ids", errors)):
            evidence_id = validate_id(value, "evidence", f"audit.corpus.evidence_ids[{index}]", errors)
            if evidence_id in evidence_ids:
                errors.append(f"audit.corpus.evidence_ids[{index}]: duplicate ID: {evidence_id}")
            evidence_ids.add(evidence_id)
        require_list(corpus.get("excluded"), "audit.corpus.excluded", errors)
        if bundle_ids is not None:
            missing = sorted(evidence_ids - bundle_ids)
            if missing:
                errors.append(f"audit.corpus.evidence_ids: not found in evidence bundle: {', '.join(missing)}")

    perspectives, perspective_ids = collect_records(data, "perspectives", "perspective", errors)
    summaries, summary_ids = collect_records(data, "summaries", "summary", errors)
    drafts, draft_ids = collect_records(data, "draft_sentences", "draft", errors)
    findings, finding_ids = collect_records(data, "audit_findings", "finding", errors)
    gaps, gap_ids = collect_records(data, "reporting_gaps", "gap", errors)

    groups = {
        "perspective": perspective_ids,
        "summary": summary_ids,
        "draft": draft_ids,
        "finding": finding_ids,
        "gap": gap_ids,
    }
    all_record_ids: set[str] = set()
    for kind, ids in groups.items():
        overlap = all_record_ids & ids
        if overlap:
            errors.append(f"{kind} IDs collide with another record type: {', '.join(sorted(overlap))}")
        all_record_ids.update(ids)

    perspective_links: dict[str, list[str]] = {}
    for index, record in enumerate(perspectives):
        where = f"perspectives[{index}]"
        require_string(record.get("label"), f"{where}.label", errors)
        require_string(record.get("description"), f"{where}.description", errors)
        axes = require_list(record.get("stance_axes"), f"{where}.stance_axes", errors)
        if not axes or any(not isinstance(axis, str) or not axis.strip() for axis in axes):
            errors.append(f"{where}.stance_axes: must contain non-empty strings")
        perspective_links[record.get("id", "")] = validate_evidence_refs(
            record.get("evidence_refs"), f"{where}.evidence_refs", evidence_ids, errors, nonempty=True
        )
        validate_evidence_refs(
            record.get("counterevidence_refs"), f"{where}.counterevidence_refs", evidence_ids, errors
        )
        count = record.get("observed_source_count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            errors.append(f"{where}.observed_source_count: must be a positive integer")
        if record.get("extraction_confidence") not in CONFIDENCE:
            errors.append(f"{where}.extraction_confidence: expected one of {sorted(CONFIDENCE)}")
        if record.get("representativeness") not in REPRESENTATIVENESS:
            errors.append(f"{where}.representativeness: expected corpus_only or unknown")
        validate_review(record.get("human_review"), f"{where}.human_review", errors)

    summary_links: dict[str, tuple[list[str], list[str]]] = {}
    for index, record in enumerate(summaries):
        where = f"summaries[{index}]"
        require_string(record.get("text"), f"{where}.text", errors)
        p_refs = validate_ref_list(
            record.get("perspective_refs"), f"{where}.perspective_refs", perspective_ids, errors, nonempty=True
        )
        e_refs = validate_evidence_refs(
            record.get("evidence_refs"), f"{where}.evidence_refs", evidence_ids, errors, nonempty=True
        )
        summary_links[record.get("id", "")] = (p_refs, e_refs)
        validate_evidence_refs(
            record.get("omitted_evidence_refs"), f"{where}.omitted_evidence_refs", evidence_ids, errors
        )
        if record.get("support_type") not in SUPPORT_TYPES:
            errors.append(f"{where}.support_type: expected one of {sorted(SUPPORT_TYPES)}")
        validate_review(record.get("human_review"), f"{where}.human_review", errors)

    draft_links: dict[str, tuple[list[str], list[str], list[str]]] = {}
    for index, record in enumerate(drafts):
        where = f"draft_sentences[{index}]"
        require_string(record.get("text"), f"{where}.text", errors)
        s_refs = validate_ref_list(record.get("summary_refs"), f"{where}.summary_refs", summary_ids, errors)
        p_refs = validate_ref_list(
            record.get("perspective_refs"), f"{where}.perspective_refs", perspective_ids, errors
        )
        e_refs = validate_evidence_refs(record.get("evidence_refs"), f"{where}.evidence_refs", evidence_ids, errors)
        draft_links[record.get("id", "")] = (s_refs, p_refs, e_refs)
        flags = require_list(record.get("flags"), f"{where}.flags", errors)
        unknown_flags = sorted({flag for flag in flags if flag not in FINDING_TYPES})
        if unknown_flags:
            errors.append(f"{where}.flags: unknown values: {', '.join(map(str, unknown_flags))}")
        if not s_refs and not p_refs and not e_refs and "unsupported_assertion" not in flags:
            errors.append(f"{where}: unlinked sentence must carry unsupported_assertion")
        require_list(record.get("model_signals"), f"{where}.model_signals", errors)
        for rewrite_index, rewrite in enumerate(require_list(record.get("suggested_rewrites"), f"{where}.suggested_rewrites", errors)):
            rewrite_where = f"{where}.suggested_rewrites[{rewrite_index}]"
            if not require(
                rewrite,
                ("proposed_text", "problem_addressed", "rationale", "claim_meaning_changed", "human_review"),
                rewrite_where,
                errors,
            ):
                continue
            require_string(rewrite.get("proposed_text"), f"{rewrite_where}.proposed_text", errors)
            require_string(rewrite.get("rationale"), f"{rewrite_where}.rationale", errors)
            if rewrite.get("problem_addressed") not in FINDING_TYPES:
                errors.append(f"{rewrite_where}.problem_addressed: unknown finding type")
            if not isinstance(rewrite.get("claim_meaning_changed"), bool):
                errors.append(f"{rewrite_where}.claim_meaning_changed: must be boolean")
            validate_review(rewrite.get("human_review"), f"{rewrite_where}.human_review", errors)
        validate_review(record.get("human_review"), f"{where}.human_review", errors)

    resolvable_refs = all_record_ids | evidence_ids
    edge_set: set[tuple[str, str, str]] = set()
    for index, edge in enumerate(require_list(data.get("lineage"), "lineage", errors)):
        where = f"lineage[{index}]"
        if not require(edge, ("from_ref", "to_ref", "relation", "note"), where, errors):
            continue
        from_ref = edge.get("from_ref")
        to_ref = edge.get("to_ref")
        relation = edge.get("relation")
        if not isinstance(from_ref, str) or (
            from_ref not in resolvable_refs and evidence_base(from_ref) not in evidence_ids
        ):
            errors.append(f"{where}.from_ref: unresolved reference: {from_ref!r}")
        if not isinstance(to_ref, str) or (
            to_ref not in resolvable_refs and evidence_base(to_ref) not in evidence_ids
        ):
            errors.append(f"{where}.to_ref: unresolved reference: {to_ref!r}")
        if relation not in RELATIONS:
            errors.append(f"{where}.relation: expected one of {sorted(RELATIONS)}")
        if isinstance(from_ref, str) and isinstance(to_ref, str) and isinstance(relation, str):
            edge = (from_ref, to_ref, relation)
            if edge in edge_set:
                errors.append(f"{where}: duplicate lineage edge: {edge}")
            edge_set.add(edge)

    for perspective_id, refs in perspective_links.items():
        for ref in refs:
            if (ref, perspective_id, "supports") not in edge_set:
                errors.append(f"lineage: missing supports edge {ref} -> {perspective_id}")
    for summary_id, (p_refs, e_refs) in summary_links.items():
        for ref in p_refs:
            if not any((ref, summary_id, relation) in edge_set for relation in ("summarized_as", "merged_into")):
                errors.append(f"lineage: missing perspective-to-summary edge {ref} -> {summary_id}")
        for ref in e_refs:
            if (ref, summary_id, "supports") not in edge_set:
                errors.append(f"lineage: missing supports edge {ref} -> {summary_id}")
    for draft_id, (s_refs, p_refs, e_refs) in draft_links.items():
        for ref in s_refs + p_refs:
            if (ref, draft_id, "propagates_to") not in edge_set:
                errors.append(f"lineage: missing propagates_to edge {ref} -> {draft_id}")
        for ref in e_refs:
            if (ref, draft_id, "supports") not in edge_set:
                errors.append(f"lineage: missing supports edge {ref} -> {draft_id}")

    for index, record in enumerate(findings):
        where = f"audit_findings[{index}]"
        if record.get("type") not in FINDING_TYPES:
            errors.append(f"{where}.type: unknown finding type")
        if record.get("severity") not in SEVERITIES:
            errors.append(f"{where}.severity: expected one of {sorted(SEVERITIES)}")
        validate_ref_list(record.get("target_refs"), f"{where}.target_refs", resolvable_refs, errors, nonempty=True)
        validate_evidence_refs(record.get("evidence_refs"), f"{where}.evidence_refs", evidence_ids, errors)
        require_string(record.get("rationale"), f"{where}.rationale", errors)
        require_string(record.get("suggested_action"), f"{where}.suggested_action", errors)
        validate_review(record.get("human_review"), f"{where}.human_review", errors)

    for index, record in enumerate(gaps):
        where = f"reporting_gaps[{index}]"
        if record.get("type") not in GAP_TYPES:
            errors.append(f"{where}.type: expected one of {sorted(GAP_TYPES)}")
        require_string(record.get("description"), f"{where}.description", errors)
        require_string(record.get("basis"), f"{where}.basis", errors)
        if record.get("observed_in_corpus") is not False:
            errors.append(f"{where}.observed_in_corpus: must be false")

    if not perspectives and not any(gap.get("type") == "insufficient_corpus" for gap in gaps):
        errors.append("audit: an empty perspective set requires an insufficient_corpus reporting gap")
    return errors


def evidence_bundle_ids(path: Path, errors: list[str]) -> set[str]:
    data = load_object(path, "evidence bundle", errors)
    ids: set[str] = set()
    for index, item in enumerate(require_list(data.get("items"), "evidence bundle.items", errors)):
        if not isinstance(item, dict):
            errors.append(f"evidence bundle.items[{index}]: must be an object")
            continue
        evidence_id = validate_id(item.get("id"), "evidence", f"evidence bundle.items[{index}].id", errors)
        if evidence_id in ids:
            errors.append(f"evidence bundle.items[{index}].id: duplicate ID: {evidence_id}")
        ids.add(evidence_id)
    return ids


def main() -> int:
    args = parse_args()
    load_errors: list[str] = []
    data = load_object(args.audit, "audit", load_errors)
    bundle_ids = evidence_bundle_ids(args.evidence_bundle, load_errors) if args.evidence_bundle else None
    errors = load_errors + (validate_audit(data, bundle_ids) if data else [])
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"perspective audit invalid: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"perspective audit valid: {args.audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
