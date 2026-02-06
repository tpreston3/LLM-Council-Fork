import { useState, useEffect } from 'react';
import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onSearch,
  isSearching,
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (onSearch) {
      onSearch(query);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>LLM Council</h1>
        <button className="new-conversation-btn" onClick={onNewConversation}>
          📜 Summon New Council
        </button>
      </div>

      <div className="sidebar-search">
        <input
          type="text"
          placeholder="Search Archives..."
          value={searchQuery}
          onChange={handleSearchChange}
          className="search-input"
        />
        {isSearching && <div className="searching-indicator">Searching...</div>}
      </div>

      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="no-conversations">The Archives are empty</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${
                conv.id === currentConversationId ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-title">
                🏛️ {conv.title || 'New Deliberation'}
              </div>
              <div className="conversation-meta">
                {conv.message_count} Records
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
