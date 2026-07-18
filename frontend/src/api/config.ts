const API_BASE_URL_ENV = 'VITE_API_BASE_URL';

export class ApiConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiConfigurationError';
  }
}

export function getApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL;

  if (typeof configured !== 'string' || configured.trim() === '') {
    throw new ApiConfigurationError(`${API_BASE_URL_ENV} is required. Configure it before starting the frontend.`);
  }

  let url: URL;
  try {
    url = new URL(configured.trim());
  } catch {
    throw new ApiConfigurationError(`${API_BASE_URL_ENV} must be a valid absolute HTTP or HTTPS URL.`);
  }

  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new ApiConfigurationError(`${API_BASE_URL_ENV} must be an absolute HTTP or HTTPS URL without credentials, a query, or a fragment.`);
  }

  url.pathname = url.pathname.replace(/\/+$/, '');
  return url.toString().replace(/\/$/, '');
}
