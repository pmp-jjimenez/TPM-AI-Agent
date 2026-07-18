import { ApiError, getJson } from '../../api/client';
import { parseIntelligence, parseProgram, parseProgramList, type IntelligenceResponse, type ProgramRecord } from './programTypes';

export async function getPrograms(signal?: AbortSignal): Promise<ProgramRecord[]> {
  const payload = await getJson(['programs'], signal);
  if (!Array.isArray(payload)) {
    throw new ApiError('malformed', 'The programs response was not in the expected format.');
  }
  return parseProgramList(payload);
}

export async function getProgram(programId: string, signal?: AbortSignal): Promise<ProgramRecord> {
  const payload = await getJson(['programs', programId], signal);
  const program = parseProgram(payload);
  if (!program || program.program_id !== programId) {
    throw new ApiError('malformed', 'The program response was not in the expected format.');
  }
  return program;
}

export async function getProgramIntelligence(programId: string, signal?: AbortSignal): Promise<IntelligenceResponse> {
  const payload = await getJson(['programs', programId, 'intelligence'], signal);
  const intelligence = parseIntelligence(payload);
  if (!intelligence || intelligence.program_id !== programId) {
    throw new ApiError('malformed', 'The intelligence response was not in the expected format.');
  }
  return intelligence;
}
