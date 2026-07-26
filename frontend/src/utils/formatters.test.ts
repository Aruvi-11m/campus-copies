import { describe, it, expect } from 'vitest';
import { formatCurrency, formatDate, formatRelativeTime } from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('formats numbers to INR currency', () => {
      // The exact string representation might vary slightly by environment
      // so we check for the currency symbol and the formatted number.
      const result = formatCurrency(1234.56);
      expect(result).toMatch(/₹/);
      expect(result).toMatch(/1,234\.56/);
    });
  });

  describe('formatDate', () => {
    it('formats ISO dates correctly', () => {
      const dateStr = '2023-10-15T14:30:00Z';
      const result = formatDate(dateStr);
      // Ensure it contains year and month
      expect(result).toContain('2023');
      expect(result).toContain('Oct');
    });
  });

  describe('formatRelativeTime', () => {
    it('returns "Just now" for times less than 1 minute ago', () => {
      const now = new Date();
      expect(formatRelativeTime(now.toISOString())).toBe('Just now');
    });

    it('returns minutes ago for times less than 1 hour ago', () => {
      const date = new Date(Date.now() - 5 * 60000);
      expect(formatRelativeTime(date.toISOString())).toBe('5m ago');
    });

    it('returns hours ago for times less than 24 hours ago', () => {
      const date = new Date(Date.now() - 2 * 3600000);
      expect(formatRelativeTime(date.toISOString())).toBe('2h ago');
    });

    it('returns days ago for times less than 7 days ago', () => {
      const date = new Date(Date.now() - 3 * 86400000);
      expect(formatRelativeTime(date.toISOString())).toBe('3d ago');
    });
  });
});
