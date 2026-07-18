import { ApiError, getJson } from '../../api/client';
import { parseProgram, parseProgramList, type ProgramRecord } from './programTypes';

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
