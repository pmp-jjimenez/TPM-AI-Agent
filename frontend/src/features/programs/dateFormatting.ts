import { usableText } from './programTypes';

export const ENGLISH_DATE_FORMATTER = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  timeZone: 'UTC',
});

export function displayDate(value: unknown): string | undefined {
  const text = usableText(value);
  if (!text) return undefined;
  if (!/^\d{4}-\d{2}-\d{2}(?:T.*)?$/.test(text)) return text;
  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) return text;
  return ENGLISH_DATE_FORMATTER.format(parsed);
}
