export interface ProgramRecord {
  program_id: string;
  program_name?: string;
  description?: string;
  customer?: string;
  phase?: string;
  health?: string;
  confidence?: string;
  meeting_history?: unknown[];
  metadata?: {
    created_at?: string | null;
    updated_at?: string | null;
    [key: string]: unknown;
  };
  [key: string]: unknown;
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
    meeting_history: Array.isArray(record.meeting_history) ? record.meeting_history : undefined,
    metadata,
  };
}

export function parseProgramList(value: unknown): ProgramRecord[] {
  if (!Array.isArray(value)) return [];
  return value.map(parseProgram).filter((program): program is ProgramRecord => program !== null);
}
