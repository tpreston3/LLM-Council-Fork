# Specification: Deliberation History View

## Goal
Implement a user-friendly interface to browse, search, and load past AI deliberations stored as JSON files in the `data/conversations/` directory.

## User Stories
- As a user, I want to see a list of my past deliberations so I can easily find previous work.
- As a user, I want to search through my past deliberations by query or content.
- As a user, I want to click on a past deliberation to reload it into the main view for inspection.

## Functional Requirements
- **Backend API:**
    - GET endpoint to list all saved conversation metadata (ID, timestamp, initial query).
    - GET endpoint to retrieve a specific conversation by ID.
    - Search functionality within the listing endpoint (optional but preferred).
- **Frontend UI:**
    - A dedicated "History" sidebar or modal.
    - Search bar to filter the list of past deliberations.
    - List items showing the first few words of the query and the date.
    - Loading state while fetching history.
    - Error handling for failed file reads.

## Technical Details
- **Storage:** Use the existing `backend/storage.py` and `data/conversations/` folder.
- **Data Format:** Conversations are stored as JSON files named `<id>.json`.
- **Performance:** For large numbers of files, consider basic pagination or metadata caching if needed.

## Design
- Adhere to the **"Council" aesthetic**: Use formal language like "Archives" or "Past Chambers."
- Integrate cleanly with the existing `Sidebar.jsx` and `ChatInterface.jsx`.
