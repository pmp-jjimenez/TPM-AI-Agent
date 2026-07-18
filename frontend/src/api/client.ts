import { ApiConfigurationError, getApiBaseUrl } from './config';

export type ApiErrorKind = 'configuration' | 'network' | 'http' | 'malformed' | 'aborted';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly code?: string;

  constructor(kind: ApiErrorKind, message: string, options: { status?: number; code?: string; cause?: unknown } = {}) {
    super(message, { cause: options.cause });
    this.name = 'ApiError';
    this.kind = kind;
    this.status = options.status;
    this.code = options.code;
  }
}

function buildApiUrl(pathSegments: string[]): string {
  const baseUrl = getApiBaseUrl();
  const encodedPath = pathSegments.map((segment) => encodeURIComponent(segment)).join('/');
  return encodedPath ? `${baseUrl}/${encodedPath}` : baseUrl;
}

async function parseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch (cause) {
    throw new ApiError('malformed', 'The API returned an invalid JSON response.', { status: response.status, cause });
  }
}

function backendError(payload: unknown): { code?: string; message?: string } {
  if (!payload || typeof payload !== 'object' || !('error' in payload)) return {};
  const error = payload.error;
  if (!error || typeof error !== 'object') return {};
  const errorRecord = error as Record<string, unknown>;
  return {
    code: typeof errorRecord.code === 'string' ? errorRecord.code : undefined,
    message: typeof errorRecord.message === 'string' ? errorRecord.message : undefined,
  };
}

export async function getJson(pathSegments: string[], signal?: AbortSignal): Promise<unknown> {
  let response: Response;

  try {
    response = await fetch(buildApiUrl(pathSegments), { method: 'GET', headers: { Accept: 'application/json' }, signal });
  } catch (cause) {
    if (cause instanceof ApiConfigurationError) {
      throw new ApiError('configuration', cause.message, { cause });
    }
    if (signal?.aborted || (cause instanceof DOMException && cause.name === 'AbortError')) {
      throw new ApiError('aborted', 'The request was cancelled.', { cause });
    }
    throw new ApiError('network', 'The API could not be reached.', { cause });
  }

  const payload = await parseJson(response);
  if (!response.ok) {
    const error = backendError(payload);
    throw new ApiError('http', error.message ?? `The API request failed with status ${response.status}.`, {
      status: response.status,
      code: error.code,
    });
  }

  return payload;
}
