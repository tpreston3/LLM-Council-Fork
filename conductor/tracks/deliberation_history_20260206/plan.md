# Implementation Plan: Deliberation History View

This plan follows the project's Test-Driven Development (TDD) workflow and includes mandatory phase verification checkpoints.

## Phase 1: Backend Archives API [checkpoint: 122591a]

- [x] **Task: Implement Archive Listing and Retrieval API** (ac11487)
    - [x] **Sub-task: Write Tests (Red Phase)**: Create `backend/tests/test_storage_api.py` and define tests for listing files in `data/conversations/` and reading a specific JSON file.
    - [x] **Sub-task: Implement Feature (Green Phase)**: Update `backend/storage.py` or create a new router to expose the history listing and retrieval via FastAPI.
    - [x] **Sub-task: Verify Coverage**: Ensure backend coverage for new logic is >80%.
- [ ] **Task: Conductor - User Manual Verification 'Backend Archives API' (Protocol in workflow.md)**

## Phase 2: Frontend History Components [checkpoint: 0216226]

- [x] **Task: Create History Listing Components** (ee58bf8)
    - [x] **Sub-task: Write Tests (Red Phase)**: Create unit tests for a new `HistorySidebar` or `ArchiveView` component, mocking API calls.
    - [x] **Sub-task: Implement Feature (Green Phase)**: Build the UI to display the list of deliberations fetched from the backend.
- [x] **Task: Implement Search and Loading Logic** (5841e1d)
    - [x] **Sub-task: Write Tests (Red Phase)**: Add tests for filtering the list and handling loading/error states.
    - [x] **Sub-task: Implement Feature (Green Phase)**: Add search bar functionality and integrate loading spinners.
- [ ] **Task: Conductor - User Manual Verification 'Frontend History Components' (Protocol in workflow.md)**

## Phase 3: Integration and Polish

- [~] **Task: Link History to Main Chat Interface**
    - [x] **Sub-task: Write Tests (Red Phase)**: Add integration tests for selecting a history item and having it populate the `App` state.
    - [x] **Sub-task: Implement Feature (Green Phase)**: Connect the `HistorySidebar` to the main `App` component so clicking an item reloads the conversation.
- [~] **Task: Council Aesthetic Polish**
    - [x] **Sub-task: Implement Feature (Green Phase)**: Apply thematic styling (gavels, scrolls, "Archives") to match the product guidelines.
- [ ] **Task: Conductor - User Manual Verification 'Integration and Polish' (Protocol in workflow.md)**
