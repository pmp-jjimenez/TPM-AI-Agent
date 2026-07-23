import { displayDate, ENGLISH_DATE_FORMATTER } from './dateFormatting';

describe('displayDate', () => {
  it('uses an explicit English locale and UTC instead of host defaults', () => {
    const options = ENGLISH_DATE_FORMATTER.resolvedOptions();

    expect(options.locale).toBe('en-US');
    expect(options.timeZone).toBe('UTC');
  });

  it('renders date-only values in English without shifting the calendar date', () => {
    expect(displayDate('2026-08-01')).toBe('Aug 1, 2026');
  });

  it('renders timestamps with the same deterministic English UTC contract', () => {
    expect(displayDate('2026-07-22T00:00:00Z')).toBe('Jul 22, 2026');
    expect(displayDate('2026-07-22T23:30:00-05:00')).toBe('Jul 23, 2026');
  });

  it('preserves non-date and invalid date values', () => {
    expect(displayDate('Not scheduled')).toBe('Not scheduled');
    expect(displayDate('2026-99-99')).toBe('2026-99-99');
    expect(displayDate(null)).toBeUndefined();
  });
});
