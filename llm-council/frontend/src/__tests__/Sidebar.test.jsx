import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Sidebar from '../components/Sidebar';

describe('Sidebar', () => {
  it('calls onSearch when the search input changes', () => {
    const onSearch = vi.fn();
    render(
      <Sidebar 
        conversations={[]} 
        onSearch={onSearch}
        onSelectConversation={() => {}}
        onNewConversation={() => {}}
      />
    );

    const input = screen.getByPlaceholderText(/search archives/i);
    fireEvent.change(input, { target: { value: 'Physics' } });

    expect(onSearch).toHaveBeenCalledWith('Physics');
  });
});
