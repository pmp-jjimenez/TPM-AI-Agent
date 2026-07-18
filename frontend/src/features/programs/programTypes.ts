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

export interface IntelligenceResponse {
  program_id: string;
  generated_at: string;
  source: 'ai' | 'deterministic_fallback';
  routing: {
    version: string;
    primary_persona: IntelligencePersona;
    supporting_personas: IntelligencePersona[];
  };
  summary: string;
  attention_items: string[];
  risks: string[];
  missing_information: string[];
  recommended_actions: string[];
  confidence: 'High' | 'Medium' | 'Low';
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
  const routing = record.routing;
  if (!routing || typeof routing !== 'object' || Array.isArray(routing)) return null;
  const routingRecord = routing as Record<string, unknown>;
  const primary = parsePersona(routingRecord.primary_persona);
  const supporting = Array.isArray(routingRecord.supporting_personas)
    ? routingRecord.supporting_personas.map(parsePersona).filter((persona): persona is IntelligencePersona => persona !== null)
    : null;
  const source = record.source;
  const confidence = record.confidence;
  const listFields = ['attention_items', 'risks', 'missing_information', 'recommended_actions', 'limitations'] as const;
  if (
    !usableText(record.program_id) || !usableText(record.generated_at) ||
    (source !== 'ai' && source !== 'deterministic_fallback') ||
    !primary || !supporting || !usableText(routingRecord.version) ||
    typeof record.summary !== 'string' ||
    (confidence !== 'High' && confidence !== 'Medium' && confidence !== 'Low') ||
    listFields.some((field) => !isStringArray(record[field]))
  ) return null;
  return {
    program_id: usableText(record.program_id)!,
    generated_at: usableText(record.generated_at)!,
    source,
    routing: { version: usableText(routingRecord.version)!, primary_persona: primary, supporting_personas: supporting },
    summary: record.summary,
    attention_items: record.attention_items as string[],
    risks: record.risks as string[],
    missing_information: record.missing_information as string[],
    recommended_actions: record.recommended_actions as string[],
    confidence,
    limitations: record.limitations as string[],
  };
}

function parsePersona(value: unknown): IntelligencePersona | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  const id = usableText(record.id);
  const displayName = usableText(record.display_name);
  return id && displayName ? { id, display_name: displayName } : null;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}
