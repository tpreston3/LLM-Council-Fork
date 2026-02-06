import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import { api } from '../api';

vi.mock('../api', () => ({
  api: {
    listConversations: vi.fn(),
    getConversation: vi.fn(),
    createConversation: vi.fn(),
  },
}));

describe('App Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads and displays conversations in the sidebar', async () => {
    api.listConversations.mockResolvedValue([
      { id: '1', title: 'Test Conversation', created_at: new Date().toISOString(), message_count: 5 },
    ]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Test Conversation/)).toBeInTheDocument();
    });
  });

  it('loads conversation details when a sidebar item is clicked', async () => {
    api.listConversations.mockResolvedValue([
      { id: '1', title: 'Test Conversation', created_at: new Date().toISOString(), message_count: 1 },
    ]);
    api.getConversation.mockResolvedValue({
      id: '1',
      title: 'Test Conversation',
      messages: [{ role: 'user', content: 'Hello World' }],
    });

    render(<App />);

    const item = await waitFor(() => screen.getByText(/Test Conversation/));
    fireEvent.click(item);

    await waitFor(() => {
      expect(api.getConversation).toHaveBeenCalledWith('1');
      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });
  });
});
