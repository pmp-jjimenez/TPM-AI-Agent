import hashlib
import json
import re
import unicodedata


INTELLIGENCE_SCHEMA_VERSION = "1.0.0"
PROVIDER_FIELDS = {
    "summary", "confidence", "findings", "recommendations",
    "decisions_required", "next_action", "limitations",
}
FINDING_CATEGORIES = {
    "fact", "missing_information", "assumption", "risk", "dependency", "conflict",
}
CONFIDENCE_LEVELS = {"High", "Medium", "Low"}
PRIORITY_LEVELS = {"Critical", "High", "Medium", "Low"}
MAX_SUMMARY_LENGTH = 2000
MAX_ITEM_LENGTH = 500
MAX_LIST_ITEMS = 20
MAX_EVIDENCE_REFS = 20
JSON_POINTER = re.compile(r"^(?:/(?:[^~/]|~0|~1)*)+$")


class IntelligenceAnalysisError(ValueError):
    """Raised when provider output is not a complete intelligence contract."""


def parse_intelligence_analysis(response_text, evidence_catalog):
    if not isinstance(response_text, str) or not response_text.strip():
        raise IntelligenceAnalysisError("Intelligence response is empty.")
    try:
        parsed = json.loads(response_text.strip())
    except json.JSONDecodeError as error:
        raise IntelligenceAnalysisError("Intelligence response is not strict JSON.") from error
    return finalize_intelligence_analysis(parsed, evidence_catalog)


def finalize_intelligence_analysis(parsed, evidence_catalog):
    """Validate an untrusted provider-shaped result and emit the public contract body."""
    _exact_object(parsed, PROVIDER_FIELDS, "response")
    catalog = set(evidence_catalog)
    summary = _text(parsed["summary"], MAX_SUMMARY_LENGTH, "summary", allow_empty=True)
    confidence = _enum(parsed["confidence"], CONFIDENCE_LEVELS, "confidence")
    findings = _parse_findings(parsed["findings"], catalog)
    recommendations = _parse_recommendations(parsed["recommendations"], catalog, len(findings))
    decisions = _parse_decisions(parsed["decisions_required"], len(findings), len(recommendations))
    next_action = _parse_next_action(parsed["next_action"], len(findings), len(recommendations))
    limitations = _string_list(parsed["limitations"], "limitations")

    _reject_semantic_duplicates(findings, ("category", "statement"), "findings")
    _reject_semantic_duplicates(recommendations, ("priority", "statement", "rationale"), "recommendations")
    _reject_semantic_duplicates(decisions, ("priority", "statement", "reason"), "decisions_required")

    _assign_ids(findings, "fnd", ("category", "statement"))
    _assign_ids(recommendations, "rec", ("priority", "statement", "rationale"))
    _assign_ids(decisions, "dec", ("priority", "statement", "reason"))
    _assign_ids([next_action], "act", ("priority", "statement", "rationale"))

    for item in recommendations:
        item["related_finding_ids"] = _resolve(item.pop("related_finding_indexes"), findings)
    for item in decisions:
        item["related_finding_ids"] = _resolve(item.pop("related_finding_indexes"), findings)
        item["related_recommendation_ids"] = _resolve(item.pop("related_recommendation_indexes"), recommendations)
    next_action["related_finding_ids"] = _resolve(next_action.pop("related_finding_indexes"), findings)
    next_action["related_recommendation_ids"] = _resolve(next_action.pop("related_recommendation_indexes"), recommendations)

    return {
        "schema_version": INTELLIGENCE_SCHEMA_VERSION,
        "summary": summary,
        "confidence": confidence,
        "findings": findings,
        "recommendations": recommendations,
        "decisions_required": decisions,
        "next_action": next_action,
        "limitations": limitations,
    }


def _parse_findings(value, catalog):
    items = _object_list(value, "findings", require_nonempty=False)
    result = []
    required = {"category", "statement", "confidence", "evidence_refs"}
    for index, item in enumerate(items):
        fields = set(item)
        if fields not in (required, required | {"impact"}):
            raise IntelligenceAnalysisError(f"Intelligence finding {index} fields are unsupported.")
        parsed = {
            "category": _enum(item["category"], FINDING_CATEGORIES, f"findings[{index}].category"),
            "statement": _text(item["statement"], MAX_ITEM_LENGTH, f"findings[{index}].statement"),
            "confidence": _enum(item["confidence"], CONFIDENCE_LEVELS, f"findings[{index}].confidence"),
            "evidence_refs": _evidence_refs(item["evidence_refs"], catalog, f"findings[{index}].evidence_refs"),
        }
        if "impact" in item:
            parsed["impact"] = _text(item["impact"], MAX_ITEM_LENGTH, f"findings[{index}].impact")
        result.append(parsed)
    return result


def _parse_recommendations(value, catalog, finding_count):
    items = _object_list(value, "recommendations", require_nonempty=False)
    result = []
    fields = {"priority", "statement", "rationale", "evidence_refs", "related_finding_indexes"}
    for index, item in enumerate(items):
        _exact_object(item, fields, f"recommendations[{index}]")
        result.append({
            "priority": _enum(item["priority"], PRIORITY_LEVELS, f"recommendations[{index}].priority"),
            "statement": _text(item["statement"], MAX_ITEM_LENGTH, f"recommendations[{index}].statement"),
            "rationale": _text(item["rationale"], MAX_ITEM_LENGTH, f"recommendations[{index}].rationale"),
            "evidence_refs": _evidence_refs(item["evidence_refs"], catalog, f"recommendations[{index}].evidence_refs"),
            "related_finding_indexes": _indexes(item["related_finding_indexes"], finding_count, f"recommendations[{index}].related_finding_indexes"),
        })
    return result


def _parse_decisions(value, finding_count, recommendation_count):
    items = _object_list(value, "decisions_required", require_nonempty=False)
    result = []
    fields = {"priority", "statement", "reason", "related_finding_indexes", "related_recommendation_indexes"}
    for index, item in enumerate(items):
        _exact_object(item, fields, f"decisions_required[{index}]")
        result.append({
            "priority": _enum(item["priority"], PRIORITY_LEVELS, f"decisions_required[{index}].priority"),
            "statement": _text(item["statement"], MAX_ITEM_LENGTH, f"decisions_required[{index}].statement"),
            "reason": _text(item["reason"], MAX_ITEM_LENGTH, f"decisions_required[{index}].reason"),
            "related_finding_indexes": _indexes(item["related_finding_indexes"], finding_count, f"decisions_required[{index}].related_finding_indexes"),
            "related_recommendation_indexes": _indexes(item["related_recommendation_indexes"], recommendation_count, f"decisions_required[{index}].related_recommendation_indexes"),
        })
    return result


def _parse_next_action(value, finding_count, recommendation_count):
    fields = {"priority", "statement", "rationale", "related_finding_indexes", "related_recommendation_indexes"}
    _exact_object(value, fields, "next_action")
    return {
        "priority": _enum(value["priority"], PRIORITY_LEVELS, "next_action.priority"),
        "statement": _text(value["statement"], MAX_ITEM_LENGTH, "next_action.statement"),
        "rationale": _text(value["rationale"], MAX_ITEM_LENGTH, "next_action.rationale"),
        "related_finding_indexes": _indexes(value["related_finding_indexes"], finding_count, "next_action.related_finding_indexes"),
        "related_recommendation_indexes": _indexes(value["related_recommendation_indexes"], recommendation_count, "next_action.related_recommendation_indexes"),
    }


def _exact_object(value, fields, name):
    if not isinstance(value, dict) or set(value) != fields:
        raise IntelligenceAnalysisError(f"Intelligence field '{name}' has unsupported fields.")


def _object_list(value, field, require_nonempty=False):
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS or (require_nonempty and not value):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    if not all(isinstance(item, dict) for item in value):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    return value


def _string_list(value, field):
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    result = [_text(item, MAX_ITEM_LENGTH, field) for item in value]
    if len({_identity_text(item) for item in result}) != len(result):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' contains duplicates.")
    return result


def _evidence_refs(value, catalog, field):
    if not isinstance(value, list) or len(value) > MAX_EVIDENCE_REFS:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    refs = []
    for ref in value:
        if not isinstance(ref, str) or ref != ref.strip() or not JSON_POINTER.fullmatch(ref) or ref not in catalog:
            raise IntelligenceAnalysisError(f"Intelligence field '{field}' contains unsupported evidence.")
        refs.append(ref)
    if len(set(refs)) != len(refs):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' contains duplicate evidence.")
    return refs


def _indexes(value, upper_bound, field):
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 or item >= upper_bound for item in value):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' contains an invalid index.")
    if len(set(value)) != len(value):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' contains duplicate indexes.")
    return value


def _enum(value, allowed, field):
    if value not in allowed:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    return value


def _text(value, limit, field, allow_empty=False):
    if not isinstance(value, str):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    normalized = unicodedata.normalize("NFKC", " ".join(value.split()))
    if (not normalized and not allow_empty) or len(normalized) > limit:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    return normalized


def _identity_text(value):
    return unicodedata.normalize("NFKC", " ".join(value.split())).casefold()


def _identity_payload(item, fields):
    return json.dumps(
        {field: _identity_text(item[field]) for field in fields},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )


def _digest(payload):
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _assign_ids(items, prefix, fields):
    payloads = [_identity_payload(item, fields) for item in items]
    digests = [_digest(payload) for payload in payloads]
    lengths = [16] * len(items)
    for size in (16, 24):
        groups = {}
        for index, digest in enumerate(digests):
            groups.setdefault(digest[:size], []).append(index)
        for indexes in groups.values():
            if len(indexes) > 1 and len({payloads[index] for index in indexes}) > 1:
                for index in indexes:
                    lengths[index] = 24 if size == 16 else 64
    ids = [f"{prefix}_{digest[:length]}" for digest, length in zip(digests, lengths)]
    if len(set(ids)) != len(ids):
        raise IntelligenceAnalysisError(f"Intelligence {prefix} identifiers are duplicated.")
    for item, item_id in zip(items, ids):
        item["id"] = item_id


def _reject_semantic_duplicates(items, fields, name):
    payloads = [_identity_payload(item, fields) for item in items]
    if len(set(payloads)) != len(payloads):
        raise IntelligenceAnalysisError(f"Intelligence field '{name}' contains duplicate semantic items.")


def _resolve(indexes, items):
    return [items[index]["id"] for index in indexes]
