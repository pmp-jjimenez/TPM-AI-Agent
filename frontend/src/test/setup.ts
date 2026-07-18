import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';

vi.stubEnv('VITE_API_BASE_URL', 'https://api.test/');

afterEach(() => {
  vi.restoreAllMocks();
});
