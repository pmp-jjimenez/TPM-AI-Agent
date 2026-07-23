export interface ProgramRecord {
  program_id: string;
  program_name?: string;
  description?: string;
  customer?: string;
  phase?: string;
  health?: string;
  confidence?: string;
  milestones?: unknown[];
  risks?: ProgramRisk[];
  issues?: ProgramIssue[];
  dependencies?: ProgramDependency[];
  decisions?: ProgramDecisionRecord[];
  next_actions?: ProgramAction[];
  sponsor?: unknown;
  budget?: unknown;
  target_go_live?: unknown;
  architecture?: unknown;
  governance?: unknown;
  meeting_history?: unknown[];
  metadata?: {
    created_at?: string | null;
    updated_at?: string | null;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

export type ProgramActionStatus = 'open' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
export type ProgramActionPriority = 'low' | 'medium' | 'high' | 'critical';

export interface ProgramAction {
  object_id: string;
  object_type: 'action';
  title: string;
  description: string | null;
  status: ProgramActionStatus;
  priority: ProgramActionPriority | null;
  owner: { display_name: string; stakeholder_id: string | null } | null;
  lifecycle_phase: 'discovery' | 'initiation' | 'planning' | 'execution' | 'readiness_go_live' | 'transition_handoff' | 'operations_closure' | null;
  due_date: string | null;
  completed_at: string | null;
  completion_summary: string | null;
  audit: { created_at: string | null; updated_at: string | null; source: 'manual' | 'cli' | 'sow_analysis' | 'legacy_import' | 'api' };
}

export type ProgramRiskStatus = 'open' | 'monitoring' | 'mitigating' | 'accepted' | 'closed';
export type ProgramRiskProbability = 'low' | 'medium' | 'high';
export type ProgramRiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ProgramRisk {
  object_id: string;
  object_type: 'risk';
  title: string;
  description: string | null;
  owner: { display_name: string; stakeholder_id: string | null } | null;
  lifecycle_phase: 'discovery' | 'initiation' | 'planning' | 'execution' | 'readiness_go_live' | 'transition_handoff' | 'operations_closure' | null;
  audit: { created_at: string | null; updated_at: string | null; source: 'manual' | 'cli' | 'sow_analysis' | 'legacy_import' | 'api' };
  status: ProgramRiskStatus;
  probability: ProgramRiskProbability | null;
  impact: ProgramRiskLevel | null;
  priority: ProgramRiskLevel | null;
  mitigation_plan: string | null;
  contingency_plan: string | null;
  review_date: string | null;
  acceptance_rationale: string | null;
  accepted_by: { display_name: string; stakeholder_id: string | null } | null;
}

export type ProgramIssueStatus = 'open' | 'in_progress' | 'blocked' | 'resolved' | 'closed';
export type ProgramIssueSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface ProgramIssue {
  object_id: string;
  object_type: 'issue';
  title: string;
  description: string | null;
  owner: { display_name: string; stakeholder_id: string | null } | null;
  lifecycle_phase: 'discovery' | 'initiation' | 'planning' | 'execution' | 'readiness_go_live' | 'transition_handoff' | 'operations_closure' | null;
  audit: { created_at: string | null; updated_at: string | null; source: 'manual' | 'cli' | 'sow_analysis' | 'legacy_import' | 'api' };
  status: ProgramIssueStatus;
  severity: ProgramIssueSeverity | null;
  impact: string | null;
  due_date: string | null;
  resolution_summary: string | null;
  resolved_at: string | null;
  root_cause: string | null;
}

export type ProgramDependencyStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type ProgramDependencyType = 'internal' | 'external' | 'vendor' | 'customer' | 'technical' | 'business';

export interface ProgramDependency {
  object_id: string;
  object_type: 'dependency';
  title: string;
  description: string | null;
  owner: { display_name: string; stakeholder_id: string | null } | null;
  lifecycle_phase: 'discovery' | 'initiation' | 'planning' | 'execution' | 'readiness_go_live' | 'transition_handoff' | 'operations_closure' | null;
  audit: { created_at: string | null; updated_at: string | null; source: 'manual' | 'cli' | 'sow_analysis' | 'legacy_import' | 'api' };
  status: ProgramDependencyStatus;
  dependency_type: ProgramDependencyType;
  depends_on: string | null;
  external_party: string | null;
  required_by_date: string | null;
  impact: string | null;
  mitigation_plan: string | null;
}

export type ProgramDecisionStatus = 'proposed' | 'approved' | 'superseded' | 'rejected';

export interface ProgramDecisionRecord {
  object_id: string;
  object_type: 'decision_record';
  title: string;
  decision: string | null;
  rationale: string | null;
  alternatives_considered: string[];
  owner: { display_name: string; stakeholder_id: string | null } | null;
  status: ProgramDecisionStatus;
  decision_date: string | null;
  review_date: string | null;
  impact: string | null;
  audit: { created_at: string | null; updated_at: string | null; source: 'manual' | 'cli' | 'sow_analysis' | 'legacy_import' | 'api' };
  lifecycle_phase: 'discovery' | 'initiation' | 'planning' | 'execution' | 'readiness_go_live' | 'transition_handoff' | 'operations_closure' | null;
}

export interface IntelligencePersona { id: string; display_name: string }
export type IntelligenceConfidence = 'High' | 'Medium' | 'Low';
export type IntelligencePriority = 'Critical' | 'High' | 'Medium' | 'Low';
export type FindingCategory = 'fact' | 'missing_information' | 'assumption' | 'risk' | 'dependency' | 'conflict';

export interface IntelligenceFinding {
  id: string; category: FindingCategory; statement: string; confidence: IntelligenceConfidence;
  evidence_refs: string[]; impact?: string;
}

export interface IntelligenceRecommendation {
  id: string; priority: IntelligencePriority; statement: string; rationale: string;
  evidence_refs: string[]; related_finding_ids: string[];
}

export interface IntelligenceDecisionRequired {
  id: string; priority: IntelligencePriority; statement: string; reason: string;
  related_finding_ids: string[]; related_recommendation_ids: string[];
}

export interface IntelligenceNextAction {
  id: string; priority: IntelligencePriority; statement: string; rationale: string;
  related_finding_ids: string[]; related_recommendation_ids: string[];
}

export interface IntelligenceResponse {
  schema_version: '1.0.0';
  program_id: string;
  generated_at: string;
  source: 'ai' | 'deterministic_fallback';
  routing: {
    version: string;
    primary_persona: IntelligencePersona;
    supporting_personas: IntelligencePersona[];
  };
  summary: string;
  confidence: IntelligenceConfidence;
  findings: IntelligenceFinding[];
  recommendations: IntelligenceRecommendation[];
  decisions_required: IntelligenceDecisionRequired[];
  next_action: IntelligenceNextAction;
  limitations: string[];
}

export function usableText(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

export function parseProgram(value: unknown): ProgramRecord | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  const programId = usableText(record.program_id);
  if (!programId) return null;

  const metadata = record.metadata && typeof record.metadata === 'object' && !Array.isArray(record.metadata)
    ? record.metadata as ProgramRecord['metadata']
    : undefined;
  const parsedRisks = Array.isArray(record.risks) ? parseArray(record.risks, parseProgramRisk) : undefined;
  if (Array.isArray(record.risks) && !parsedRisks) return null;
  const risks = parsedRisks ?? undefined;
  const parsedIssues = Array.isArray(record.issues) ? parseArray(record.issues, parseProgramIssue) : undefined;
  if (Array.isArray(record.issues) && !parsedIssues) return null;
  const parsedDependencies = Array.isArray(record.dependencies) ? parseArray(record.dependencies, parseProgramDependency) : undefined;
  if (Array.isArray(record.dependencies) && !parsedDependencies) return null;
  const parsedDecisions = Array.isArray(record.decisions) ? parseArray(record.decisions, parseProgramDecisionRecord) : undefined;
  if (Array.isArray(record.decisions) && !parsedDecisions) return null;

  return {
    ...record,
    program_id: programId,
    program_name: usableText(record.program_name),
    description: usableText(record.description),
    customer: usableText(record.customer),
    phase: usableText(record.phase),
    health: usableText(record.health),
    confidence: usableText(record.confidence),
    milestones: Array.isArray(record.milestones) ? record.milestones : undefined,
    risks,
    issues: parsedIssues ?? undefined,
    dependencies: parsedDependencies ?? undefined,
    decisions: parsedDecisions ?? undefined,
    next_actions: Array.isArray(record.next_actions) ? parseArray(record.next_actions, parseProgramAction) ?? undefined : undefined,
    meeting_history: Array.isArray(record.meeting_history) ? record.meeting_history : undefined,
    metadata,
  };
}

const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function parseProgramAction(value: unknown): ProgramAction | null {
  const record = objectRecord(value);
  if (!record || !exactKeys(record, ['object_id', 'object_type', 'title', 'description', 'owner', 'lifecycle_phase', 'audit', 'status', 'priority', 'due_date', 'completed_at', 'completion_summary'])) return null;
  if (typeof record.object_id !== 'string' || !uuidPattern.test(record.object_id) || record.object_type !== 'action' || !usableText(record.title)) return null;
  if (record.description !== null && !usableText(record.description)) return null;
  if (!['open', 'in_progress', 'blocked', 'completed', 'cancelled'].includes(record.status as string)) return null;
  if (record.priority !== null && !['low', 'medium', 'high', 'critical'].includes(record.priority as string)) return null;
  if (record.lifecycle_phase !== null && !['discovery', 'initiation', 'planning', 'execution', 'readiness_go_live', 'transition_handoff', 'operations_closure'].includes(record.lifecycle_phase as string)) return null;
  if (record.due_date !== null && !usableText(record.due_date)) return null;
  if (record.completed_at !== null && !usableText(record.completed_at)) return null;
  if (record.completion_summary !== null && !usableText(record.completion_summary)) return null;
  const owner = record.owner === null ? null : objectRecord(record.owner);
  if (owner && (!exactKeys(owner, ['display_name', 'stakeholder_id']) || !usableText(owner.display_name) || (owner.stakeholder_id !== null && (typeof owner.stakeholder_id !== 'string' || !uuidPattern.test(owner.stakeholder_id))))) return null;
  if (record.owner !== null && !owner) return null;
  const audit = objectRecord(record.audit);
  if (!audit || !exactKeys(audit, ['created_at', 'updated_at', 'source']) || !['manual', 'cli', 'sow_analysis', 'legacy_import', 'api'].includes(audit.source as string)) return null;
  if (audit.created_at !== null && !usableText(audit.created_at)) return null;
  if (audit.updated_at !== null && !usableText(audit.updated_at)) return null;
  return record as unknown as ProgramAction;
}

function parseProgramRisk(value: unknown): ProgramRisk | null {
  const record = objectRecord(value);
  const fields = ['object_id', 'object_type', 'title', 'description', 'owner', 'lifecycle_phase', 'audit', 'status', 'probability', 'impact', 'priority', 'mitigation_plan', 'contingency_plan', 'review_date', 'acceptance_rationale', 'accepted_by'];
  if (!record || !exactKeys(record, fields)) return null;
  if (typeof record.object_id !== 'string' || !uuidPattern.test(record.object_id) || record.object_type !== 'risk' || !usableText(record.title)) return null;
  if (record.description !== null && !usableText(record.description)) return null;
  if (!['open', 'monitoring', 'mitigating', 'accepted', 'closed'].includes(record.status as string)) return null;
  if (record.probability !== null && !['low', 'medium', 'high'].includes(record.probability as string)) return null;
  if (record.impact !== null && !['low', 'medium', 'high', 'critical'].includes(record.impact as string)) return null;
  if (record.priority !== null && !['low', 'medium', 'high', 'critical'].includes(record.priority as string)) return null;
  if (record.lifecycle_phase !== null && !['discovery', 'initiation', 'planning', 'execution', 'readiness_go_live', 'transition_handoff', 'operations_closure'].includes(record.lifecycle_phase as string)) return null;
  for (const field of ['mitigation_plan', 'contingency_plan', 'acceptance_rationale'] as const) if (record[field] !== null && !usableText(record[field])) return null;
  if (record.review_date !== null && !isIsoDate(record.review_date)) return null;
  const owner = parseOwner(record.owner);
  const acceptedBy = parseOwner(record.accepted_by);
  if ((record.owner !== null && !owner) || (record.accepted_by !== null && !acceptedBy)) return null;
  if (record.status === 'accepted' && (!usableText(record.acceptance_rationale) || !acceptedBy)) return null;
  const audit = objectRecord(record.audit);
  if (!audit || !exactKeys(audit, ['created_at', 'updated_at', 'source']) || !['manual', 'cli', 'sow_analysis', 'legacy_import', 'api'].includes(audit.source as string)) return null;
  if (audit.created_at !== null && !isIsoDatetime(audit.created_at)) return null;
  if (audit.updated_at !== null && !isIsoDatetime(audit.updated_at)) return null;
  return record as unknown as ProgramRisk;
}

function parseProgramIssue(value: unknown): ProgramIssue | null {
  const record = objectRecord(value);
  const fields = ['object_id', 'object_type', 'title', 'description', 'owner', 'lifecycle_phase', 'audit', 'status', 'severity', 'impact', 'due_date', 'resolution_summary', 'resolved_at', 'root_cause'];
  if (!record || !exactKeys(record, fields)) return null;
  if (typeof record.object_id !== 'string' || !uuidPattern.test(record.object_id) || record.object_type !== 'issue' || !usableText(record.title)) return null;
  if (record.description !== null && !usableText(record.description)) return null;
  if (!['open', 'in_progress', 'blocked', 'resolved', 'closed'].includes(record.status as string)) return null;
  if (record.severity !== null && !['low', 'medium', 'high', 'critical'].includes(record.severity as string)) return null;
  for (const field of ['impact', 'resolution_summary', 'root_cause'] as const) if (record[field] !== null && !usableText(record[field])) return null;
  if (record.due_date !== null && !isIsoDate(record.due_date)) return null;
  if (record.resolved_at !== null && !isUtcDatetime(record.resolved_at)) return null;
  if (record.lifecycle_phase !== null && !['discovery', 'initiation', 'planning', 'execution', 'readiness_go_live', 'transition_handoff', 'operations_closure'].includes(record.lifecycle_phase as string)) return null;
  if (record.owner !== null && !parseOwner(record.owner)) return null;
  const audit = objectRecord(record.audit);
  if (!audit || !exactKeys(audit, ['created_at', 'updated_at', 'source']) || !['manual', 'cli', 'sow_analysis', 'legacy_import', 'api'].includes(audit.source as string)) return null;
  if (audit.created_at !== null && !isIsoDatetime(audit.created_at)) return null;
  if (audit.updated_at !== null && !isIsoDatetime(audit.updated_at)) return null;
  return record as unknown as ProgramIssue;
}

function parseProgramDependency(value: unknown): ProgramDependency | null {
  const record = objectRecord(value);
  const fields = ['object_id', 'object_type', 'title', 'description', 'owner', 'lifecycle_phase', 'audit', 'status', 'dependency_type', 'depends_on', 'external_party', 'required_by_date', 'impact', 'mitigation_plan'];
  if (!record || !exactKeys(record, fields)) return null;
  if (typeof record.object_id !== 'string' || !uuidPattern.test(record.object_id) || record.object_type !== 'dependency' || !usableText(record.title)) return null;
  if (record.description !== null && !usableText(record.description)) return null;
  if (!['open', 'in_progress', 'resolved', 'closed'].includes(record.status as string)) return null;
  if (!['internal', 'external', 'vendor', 'customer', 'technical', 'business'].includes(record.dependency_type as string)) return null;
  for (const field of ['depends_on', 'external_party', 'impact', 'mitigation_plan'] as const) if (record[field] !== null && !usableText(record[field])) return null;
  if (record.required_by_date !== null && !isIsoDate(record.required_by_date)) return null;
  if (record.lifecycle_phase !== null && !['discovery', 'initiation', 'planning', 'execution', 'readiness_go_live', 'transition_handoff', 'operations_closure'].includes(record.lifecycle_phase as string)) return null;
  if (record.owner !== null && !parseOwner(record.owner)) return null;
  const audit = objectRecord(record.audit);
  if (!audit || !exactKeys(audit, ['created_at', 'updated_at', 'source']) || !['manual', 'cli', 'sow_analysis', 'legacy_import', 'api'].includes(audit.source as string)) return null;
  if (audit.created_at !== null && !isIsoDatetime(audit.created_at)) return null;
  if (audit.updated_at !== null && !isIsoDatetime(audit.updated_at)) return null;
  return record as unknown as ProgramDependency;
}

function parseProgramDecisionRecord(value: unknown): ProgramDecisionRecord | null {
  const record = objectRecord(value);
  const fields = ['object_id', 'object_type', 'title', 'decision', 'rationale', 'alternatives_considered', 'owner', 'status', 'decision_date', 'review_date', 'impact', 'audit', 'lifecycle_phase'];
  if (!record || !exactKeys(record, fields)) return null;
  if (typeof record.object_id !== 'string' || !uuidPattern.test(record.object_id) || record.object_type !== 'decision_record' || !usableText(record.title)) return null;
  if (!['proposed', 'approved', 'superseded', 'rejected'].includes(record.status as string)) return null;
  for (const field of ['decision', 'rationale', 'impact'] as const) if (record[field] !== null && !usableText(record[field])) return null;
  if (!Array.isArray(record.alternatives_considered) || !record.alternatives_considered.every((item) => usableText(item))) return null;
  if (new Set(record.alternatives_considered).size !== record.alternatives_considered.length) return null;
  if (record.decision_date !== null && !isIsoDate(record.decision_date)) return null;
  if (record.review_date !== null && !isIsoDate(record.review_date)) return null;
  if (record.lifecycle_phase !== null && !['discovery', 'initiation', 'planning', 'execution', 'readiness_go_live', 'transition_handoff', 'operations_closure'].includes(record.lifecycle_phase as string)) return null;
  if (record.owner !== null && !parseOwner(record.owner)) return null;
  const audit = objectRecord(record.audit);
  if (!audit || !exactKeys(audit, ['created_at', 'updated_at', 'source']) || !['manual', 'cli', 'sow_analysis', 'legacy_import', 'api'].includes(audit.source as string)) return null;
  if (audit.created_at !== null && !isIsoDatetime(audit.created_at)) return null;
  if (audit.updated_at !== null && !isIsoDatetime(audit.updated_at)) return null;
  return record as unknown as ProgramDecisionRecord;
}

function parseOwner(value: unknown): Record<string, unknown> | null {
  if (value === null) return null;
  const owner = objectRecord(value);
  if (!owner || !exactKeys(owner, ['display_name', 'stakeholder_id']) || !usableText(owner.display_name)) return null;
  if (owner.stakeholder_id !== null && (typeof owner.stakeholder_id !== 'string' || !uuidPattern.test(owner.stakeholder_id))) return null;
  return owner;
}

function isIsoDate(value: unknown): value is string {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function isIsoDatetime(value: unknown): value is string {
  return typeof value === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/.test(value) && !Number.isNaN(Date.parse(value));
}

function isUtcDatetime(value: unknown): value is string {
  return isIsoDatetime(value) && /(?:Z|\+00:00)$/.test(value);
}

export function parseProgramList(value: unknown): ProgramRecord[] {
  if (!Array.isArray(value)) return [];
  return value.map(parseProgram).filter((program): program is ProgramRecord => program !== null);
}

export function parseIntelligence(value: unknown): IntelligenceResponse | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  if (!exactKeys(record, ['schema_version', 'program_id', 'generated_at', 'source', 'routing', 'summary', 'confidence', 'findings', 'recommendations', 'decisions_required', 'next_action', 'limitations'])) return null;
  const routing = record.routing;
  if (!routing || typeof routing !== 'object' || Array.isArray(routing)) return null;
  const routingRecord = routing as Record<string, unknown>;
  if (!exactKeys(routingRecord, ['version', 'primary_persona', 'supporting_personas'])) return null;
  const primary = parsePersona(routingRecord.primary_persona);
  const supporting = parseArray(routingRecord.supporting_personas, parsePersona);
  const source = record.source;
  const confidence = record.confidence;
  const findings = parseArray(record.findings, parseFinding);
  const recommendations = parseArray(record.recommendations, parseRecommendation);
  const decisions = parseArray(record.decisions_required, parseDecision);
  const nextAction = parseNextAction(record.next_action);
  const findingIds = new Set(findings?.map((item) => item.id));
  const recommendationIds = new Set(recommendations?.map((item) => item.id));
  if (
    record.schema_version !== '1.0.0' ||
    !usableText(record.program_id) || !usableText(record.generated_at) ||
    (source !== 'ai' && source !== 'deterministic_fallback') ||
    !primary || !supporting || !usableText(routingRecord.version) ||
    typeof record.summary !== 'string' || !isConfidence(confidence) ||
    !findings || !recommendations || !decisions || !nextAction || !isUniqueStringArray(record.limitations) ||
    findingIds.size !== findings.length || recommendationIds.size !== recommendations.length || new Set(decisions.map((item) => item.id)).size !== decisions.length ||
    !recommendations.every((item) => item.related_finding_ids.every((id) => findingIds.has(id))) ||
    !decisions.every((item) => item.related_finding_ids.every((id) => findingIds.has(id)) && item.related_recommendation_ids.every((id) => recommendationIds.has(id))) ||
    !nextAction.related_finding_ids.every((id) => findingIds.has(id)) ||
    !nextAction.related_recommendation_ids.every((id) => recommendationIds.has(id))
  ) return null;
  return {
    schema_version: '1.0.0',
    program_id: usableText(record.program_id)!,
    generated_at: usableText(record.generated_at)!,
    source,
    routing: { version: usableText(routingRecord.version)!, primary_persona: primary, supporting_personas: supporting },
    summary: record.summary,
    confidence,
    findings, recommendations, decisions_required: decisions, next_action: nextAction,
    limitations: record.limitations as string[],
  };
}

const idPatterns = { fnd: /^fnd_[0-9a-f]{16}(?:[0-9a-f]{8}|[0-9a-f]{48})?$/, rec: /^rec_[0-9a-f]{16}(?:[0-9a-f]{8}|[0-9a-f]{48})?$/, dec: /^dec_[0-9a-f]{16}(?:[0-9a-f]{8}|[0-9a-f]{48})?$/, act: /^act_[0-9a-f]{16}(?:[0-9a-f]{8}|[0-9a-f]{48})?$/ };
const pointerPattern = /^(?:\/(?:[^~/]|~0|~1)*)+$/;

function parseFinding(value: unknown): IntelligenceFinding | null {
  const record = objectRecord(value); if (!record) return null;
  const allowed = ['id', 'category', 'statement', 'confidence', 'evidence_refs', 'impact'];
  if (!exactKeys(record, allowed, ['id', 'category', 'statement', 'confidence', 'evidence_refs'])) return null;
  const category = record.category;
  if (!idValue(record.id, 'fnd') || !isCategory(category) || !usableText(record.statement) || !isConfidence(record.confidence) || !isEvidenceRefs(record.evidence_refs) || (record.impact !== undefined && !usableText(record.impact))) return null;
  return { id: record.id as string, category, statement: usableText(record.statement)!, confidence: record.confidence, evidence_refs: record.evidence_refs as string[], ...(record.impact === undefined ? {} : { impact: usableText(record.impact)! }) };
}

function parseRecommendation(value: unknown): IntelligenceRecommendation | null {
  const record = objectRecord(value); if (!record || !exactKeys(record, ['id', 'priority', 'statement', 'rationale', 'evidence_refs', 'related_finding_ids'])) return null;
  if (!idValue(record.id, 'rec') || !isPriority(record.priority) || !usableText(record.statement) || !usableText(record.rationale) || !isEvidenceRefs(record.evidence_refs) || !isUniqueStringArray(record.related_finding_ids)) return null;
  return record as unknown as IntelligenceRecommendation;
}

function parseDecision(value: unknown): IntelligenceDecisionRequired | null {
  const record = objectRecord(value); if (!record || !exactKeys(record, ['id', 'priority', 'statement', 'reason', 'related_finding_ids', 'related_recommendation_ids'])) return null;
  if (!idValue(record.id, 'dec') || !isPriority(record.priority) || !usableText(record.statement) || !usableText(record.reason) || !isUniqueStringArray(record.related_finding_ids) || !isUniqueStringArray(record.related_recommendation_ids)) return null;
  return record as unknown as IntelligenceDecisionRequired;
}

function parseNextAction(value: unknown): IntelligenceNextAction | null {
  const record = objectRecord(value); if (!record || !exactKeys(record, ['id', 'priority', 'statement', 'rationale', 'related_finding_ids', 'related_recommendation_ids'])) return null;
  if (!idValue(record.id, 'act') || !isPriority(record.priority) || !usableText(record.statement) || !usableText(record.rationale) || !isUniqueStringArray(record.related_finding_ids) || !isUniqueStringArray(record.related_recommendation_ids)) return null;
  return record as unknown as IntelligenceNextAction;
}

function objectRecord(value: unknown): Record<string, unknown> | null { return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function exactKeys(record: Record<string, unknown>, allowed: string[], required = allowed): boolean { return Object.keys(record).every((key) => allowed.includes(key)) && required.every((key) => key in record); }
function parseArray<T>(value: unknown, parser: (item: unknown) => T | null): T[] | null { if (!Array.isArray(value)) return null; const parsed = value.map(parser); return parsed.every((item): item is T => item !== null) ? parsed : null; }
function isConfidence(value: unknown): value is IntelligenceConfidence { return value === 'High' || value === 'Medium' || value === 'Low'; }
function isPriority(value: unknown): value is IntelligencePriority { return value === 'Critical' || value === 'High' || value === 'Medium' || value === 'Low'; }
function isCategory(value: unknown): value is FindingCategory { return value === 'fact' || value === 'missing_information' || value === 'assumption' || value === 'risk' || value === 'dependency' || value === 'conflict'; }
function idValue(value: unknown, prefix: keyof typeof idPatterns): boolean { return typeof value === 'string' && idPatterns[prefix].test(value); }
function isUniqueStringArray(value: unknown): value is string[] { return isStringArray(value) && value.every((item) => Boolean(usableText(item))) && new Set(value).size === value.length; }
function isEvidenceRefs(value: unknown): value is string[] { return isUniqueStringArray(value) && value.every((item) => pointerPattern.test(item)); }

function parsePersona(value: unknown): IntelligencePersona | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  if (!exactKeys(record, ['id', 'display_name'])) return null;
  const id = usableText(record.id);
  const displayName = usableText(record.display_name);
  return id && displayName ? { id, display_name: displayName } : null;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}
