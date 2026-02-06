import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../api';

global.fetch = vi.fn();

describe('api', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('listConversations', () => {
    it('calls fetch with the correct URL', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([{ id: '1', title: 'Test' }]),
      });

      const result = await api.listConversations();
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/conversations');
      expect(result).toEqual([{ id: '1', title: 'Test' }]);
    });

    it('calls fetch with the search parameter when provided', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([{ id: '1', title: 'Search Result' }]),
      });

      const result = await api.listConversations('Physics');
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8001/api/conversations?search=Physics');
      expect(result).toEqual([{ id: '1', title: 'Search Result' }]);
    });
  });
});
