# ZenithFlow &bull; Enterprise Kanban & Todo Platform

> A task-management platform built with **Python, Flask, SQLAlchemy, and Vanilla JavaScript/CSS**. Features dual-view support (Kanban Board + Flask.io inspired Minimalist Checklist), native drag-and-drop, sprint velocity metrics, subtasks/checklists, priority filters, and dark/light modes.

---

## 🌟 Key Features

### 1. Dual-View Workflow
- **Kanban Board View (Trello / Jira style):** 4 columns (`To Do`, `In Progress`, `Review & QA`, `Completed`) with native HTML5 drag-and-drop, dropzone highlights, and real-time state synchronization.
- **List View (Flask.io style):** Fast, minimalist checklist with instant completion toggle, animated checkboxes, and strikethroughs.

### 2. Management & Sprint Velocity Metrics
- Real-time Sprint Completion Bar with dynamic percentage calculation.
- Live metric counters for **Total Tasks**, **In Progress**, **Completed**, and **Overdue Tasks**.
- Visual priority badges: **Urgent 🔥**, **High ⚡**, **Medium 🔹**, and **Low ☕**.

### 3. Task Details & Subtask Checklist
- Modal editor for task titles, context/descriptions, due dates, and tags.
- Nested subtasks/checklists with live progress indicator (e.g. `2/3 Completed`).
- Keyboard shortcuts (`N` for new task, `/` for search, `Esc` to close modals).

### 4. Aesthetics & Polish
- Tailored dark/light mode toggle with preference persistence (`localStorage`).
- Glassmorphic card styling, responsive layouts, micro-animations, and celebratory confetti upon task completion.
- One-click **Demo Reset** button to restore sample sprint data during interviews and reviews.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Flask & Flask-SQLAlchemy (included in `.venv`)

### Running Locally

1. Navigate to the project directory:
   ```bash
   cd to-do-website
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Open your browser:
   ```
   http://127.0.0.1:5000
   ```

The application automatically seeds an initial database with sprint roadmap tasks and career prep goals on first launch.

---

## 📡 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` / `POST` | `/api/boards` | Fetch all boards or create a new board |
| `GET` / `PUT` / `DELETE` | `/api/boards/<id>` | Inspect, rename, or delete a board |
| `GET` / `POST` | `/api/tasks` | Filtered task list (`board_id`, `status`, `priority`, `search`) or create task |
| `GET` / `PUT` / `DELETE` | `/api/tasks/<id>` | Full task details, update, or delete |
| `PATCH` | `/api/tasks/<id>/status` | Quick status change (Drag-and-drop & completion toggle) |
| `POST` | `/api/tasks/<id>/subtasks` | Add a subtask/checklist item |
| `PUT` / `DELETE` | `/api/subtasks/<id>` | Toggle subtask completed state or delete item |
| `GET` | `/api/stats` | Sprint completion rates and status distribution |
| `POST` | `/api/reset` | Restore demo sprint dataset |
