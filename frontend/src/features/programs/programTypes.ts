export interface ProgramRecord {
  program_id: string;
  program_name?: string;
  description?: string;
  customer?: string;
  phase?: string;
  health?: string;
  confidence?: string;
  milestones?: unknown[];
  next_actions?: unknown[];
  sponsor?: unknown;
  budget?: unknown;
  target_go_live?: unknown;
  architecture?: unknown;
  dependencies?: unknown;
  governance?: unknown;
  meeting_history?: unknown[];
  metadata?: {
    created_at?: string | null;
    updated_at?: string | null;
    [key: string]: unknown;
  };
  [key: string]: unknown;
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
    next_actions: Array.isArray(record.next_actions) ? record.next_actions : undefined,
    meeting_history: Array.isArray(record.meeting_history) ? record.meeting_history : undefined,
    metadata,
  };
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
