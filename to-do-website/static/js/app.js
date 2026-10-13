/**
 * ZenithFlow - Enterprise Kanban & Task Management Platform
 * Frontend Reactive Logic & Drag-and-Drop Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------------------------
    // Application State
    // ---------------------------------------------------------------------------
    const state = {
        boards: [],
        currentBoardId: null,
        tasks: [],
        currentView: 'kanban', // 'kanban' | 'list'
        filterPriority: 'all',
        filterTag: '',
        searchQuery: '',
        draggedTaskId: null,
        activeEditingTask: null
    };

    // ---------------------------------------------------------------------------
    // DOM Element Selectors
    // ---------------------------------------------------------------------------
    const dom = {
        // Theme
        themeToggleBtn: document.getElementById('themeToggleBtn'),

        // Board Selector
        boardDropdownBtn: document.getElementById('boardDropdownBtn'),
        boardDropdownMenu: document.getElementById('boardDropdownMenu'),
        boardWrapper: document.querySelector('.board-selector-wrapper'),
        currentBoardIndicator: document.getElementById('currentBoardIndicator'),
        currentBoardName: document.getElementById('currentBoardName'),
        boardItemsList: document.getElementById('boardItemsList'),
        openNewBoardModalBtn: document.getElementById('openNewBoardModalBtn'),
        resetDataBtn: document.getElementById('resetDataBtn'),

        // Navigation & Search
        searchInput: document.getElementById('searchInput'),
        openNewTaskModalBtn: document.getElementById('openNewTaskModalBtn'),

        // Metrics
        statTotal: document.getElementById('statTotal'),
        statInProgress: document.getElementById('statInProgress'),
        statDone: document.getElementById('statDone'),
        statOverdue: document.getElementById('statOverdue'),
        statCompletionRate: document.getElementById('statCompletionRate'),
        progressBarFill: document.getElementById('progressBarFill'),

        // View Tabs
        viewKanbanBtn: document.getElementById('viewKanbanBtn'),
        viewListBtn: document.getElementById('viewListBtn'),
        kanbanView: document.getElementById('kanbanView'),
        listView: document.getElementById('listView'),

        // Filters
        priorityFilterGroup: document.getElementById('priorityFilterGroup'),
        tagFilterSelect: document.getElementById('tagFilterSelect'),
        activeFilterBadge: document.getElementById('activeFilterBadge'),
        clearFiltersBtn: document.getElementById('clearFiltersBtn'),

        // Dropzones & Columns
        columns: {
            todo: document.getElementById('zone-todo'),
            in_progress: document.getElementById('zone-in_progress'),
            review: document.getElementById('zone-review'),
            done: document.getElementById('zone-done')
        },
        counts: {
            todo: document.getElementById('count-todo'),
            in_progress: document.getElementById('count-in_progress'),
            review: document.getElementById('count-review'),
            done: document.getElementById('count-done')
        },

        // List View specific
        quickListInput: document.getElementById('quickListInput'),
        quickListPriority: document.getElementById('quickListPriority'),
        quickListSubmitBtn: document.getElementById('quickListSubmitBtn'),
        listGroupsWrapper: document.getElementById('listGroupsWrapper'),

        // Task Modal
        taskModal: document.getElementById('taskModal'),
        taskForm: document.getElementById('taskForm'),
        closeTaskModalBtn: document.getElementById('closeTaskModalBtn'),
        cancelTaskModalBtn: document.getElementById('cancelTaskModalBtn'),
        taskModalHeading: document.getElementById('taskModalHeading'),
        taskId: document.getElementById('taskId'),
        taskTitle: document.getElementById('taskTitle'),
        taskStatus: document.getElementById('taskStatus'),
        taskPriority: document.getElementById('taskPriority'),
        taskDueDate: document.getElementById('taskDueDate'),
        taskTags: document.getElementById('taskTags'),
        taskDesc: document.getElementById('taskDesc'),
        modalSubtaskList: document.getElementById('modalSubtaskList'),
        newSubtaskInput: document.getElementById('newSubtaskInput'),
        addSubtaskBtn: document.getElementById('addSubtaskBtn'),
        subtaskProgressText: document.getElementById('subtaskProgressText'),
        deleteTaskBtn: document.getElementById('deleteTaskBtn'),

        // Board Modal
        boardModal: document.getElementById('boardModal'),
        boardForm: document.getElementById('boardForm'),
        closeBoardModalBtn: document.getElementById('closeBoardModalBtn'),
        cancelBoardModalBtn: document.getElementById('cancelBoardModalBtn'),
        boardName: document.getElementById('boardName'),
        boardDesc: document.getElementById('boardDesc'),

        // Toast Container
        toastContainer: document.getElementById('toastContainer')
    };

    // ---------------------------------------------------------------------------
    // Theme Management
    // ---------------------------------------------------------------------------
    const savedTheme = localStorage.getItem('zf_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    dom.themeToggleBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const nextTheme = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('zf_theme', nextTheme);
        showToast(`Switched to ${nextTheme} theme`, 'info');
    });

    // ---------------------------------------------------------------------------
    // Toast Notification System
    // ---------------------------------------------------------------------------
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'circle-info';
        if (type === 'success') icon = 'circle-check';
        if (type === 'error') icon = 'triangle-exclamation';

        toast.innerHTML = `<i class="fa-solid fa-${icon}"></i> <span>${escapeHtml(message)}</span>`;
        dom.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(8px)';
            toast.style.transition = 'all 0.25s ease';
            setTimeout(() => toast.remove(), 250);
        }, 2800);
    }

    // ---------------------------------------------------------------------------
    // Utility Helpers
    // ---------------------------------------------------------------------------
    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }

    function formatDateDisplay(isoDateStr) {
        if (!isoDateStr) return null;
        const [year, month, day] = isoDateStr.split('-').map(Number);
        const target = new Date(year, month - 1, day);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const diffTime = target.getTime() - today.getTime();
        const diffDays = Math.round(diffTime / (1000 * 3600 * 24));

        let text = target.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        let statusClass = '';

        if (diffDays < 0) {
            text = `Overdue (${Math.abs(diffDays)}d)`;
            statusClass = 'is-overdue';
        } else if (diffDays === 0) {
            text = 'Due Today';
            statusClass = 'is-today';
        } else if (diffDays === 1) {
            text = 'Tomorrow';
        }

        return { text, statusClass, isOverdue: diffDays < 0 };
    }

    function triggerConfetti() {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 50,
                spread: 60,
                origin: { y: 0.75 },
                colors: ['#6366f1', '#10b981', '#f59e0b', '#ec4899']
            });
        }
    }

    // ---------------------------------------------------------------------------
    // API Communication
    // ---------------------------------------------------------------------------
    async function apiRequest(endpoint, options = {}) {
        try {
            const res = await fetch(endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${res.status}`);
            }
            return await res.json();
        } catch (err) {
            showToast(`API Error: ${err.message}`, 'error');
            throw err;
        }
    }

    // ---------------------------------------------------------------------------
    // Data Loading & Render Loop
    // ---------------------------------------------------------------------------
    async function loadInitialData() {
        await loadBoards();
        if (state.boards.length > 0) {
            setActiveBoard(state.boards[0].id);
        }
    }

    async function loadBoards() {
        state.boards = await apiRequest('/api/boards');
        renderBoardMenu();
    }

    function renderBoardMenu() {
        dom.boardItemsList.innerHTML = '';
        state.boards.forEach(b => {
            const item = document.createElement('div');
            item.className = `board-menu-item ${b.id === state.currentBoardId ? 'active' : ''}`;
            item.innerHTML = `
                <span class="board-color-indicator" style="background: ${b.color};"></span>
                <span class="board-menu-item-title">${escapeHtml(b.name)}</span>
                <span class="board-menu-item-count">${b.completed_count}/${b.task_count}</span>
            `;
            item.addEventListener('click', () => {
                setActiveBoard(b.id);
                closeBoardDropdown();
            });
            dom.boardItemsList.appendChild(item);
        });
    }

    async function setActiveBoard(boardId) {
        state.currentBoardId = boardId;
        const current = state.boards.find(b => b.id === boardId);
        if (current) {
            dom.currentBoardName.textContent = current.name;
            dom.currentBoardIndicator.style.background = current.color;
        }
        renderBoardMenu();
        await refreshBoardTasks();
    }

    async function refreshBoardTasks() {
        let url = `/api/tasks?board_id=${state.currentBoardId}`;
        state.tasks = await apiRequest(url);
        updateTagFilterOptions();
        renderFilteredView();
        updateStats();
    }

    async function updateStats() {
        const stats = await apiRequest(`/api/stats?board_id=${state.currentBoardId}`);
        dom.statTotal.textContent = stats.total;
        dom.statInProgress.textContent = stats.in_progress;
        dom.statDone.textContent = stats.done;
        dom.statOverdue.textContent = stats.overdue;
        dom.statCompletionRate.textContent = `${stats.completion_rate}%`;
        dom.progressBarFill.style.width = `${stats.completion_rate}%`;
    }

    function updateTagFilterOptions() {
        const tagSet = new Set();
        state.tasks.forEach(t => {
            t.tags.forEach(tag => tagSet.add(tag));
        });

        const currentVal = dom.tagFilterSelect.value;
        dom.tagFilterSelect.innerHTML = '<option value="">All Tags</option>';
        Array.from(tagSet).sort().forEach(tag => {
            const opt = document.createElement('option');
            opt.value = tag;
            opt.textContent = tag;
            dom.tagFilterSelect.appendChild(opt);
        });

        if (tagSet.has(currentVal)) {
            dom.tagFilterSelect.value = currentVal;
        }
    }

    // ---------------------------------------------------------------------------
    // Filter & Search Logic
    // ---------------------------------------------------------------------------
    function getFilteredTasks() {
        return state.tasks.filter(task => {
            // Priority match
            if (state.filterPriority !== 'all' && task.priority !== state.filterPriority) {
                return false;
            }
            // Tag match
            if (state.filterTag && !task.tags.includes(state.filterTag)) {
                return false;
            }
            // Search query match
            if (state.searchQuery) {
                const q = state.searchQuery.toLowerCase();
                const titleMatch = task.title.toLowerCase().includes(q);
                const descMatch = (task.description || '').toLowerCase().includes(q);
                const tagsMatch = task.tags.some(t => t.toLowerCase().includes(q));
                if (!titleMatch && !descMatch && !tagsMatch) return false;
            }
            return true;
        });
    }

    function renderFilteredView() {
        const isFiltered = state.filterPriority !== 'all' || state.filterTag !== '' || state.searchQuery !== '';
        dom.activeFilterBadge.style.display = isFiltered ? 'flex' : 'none';

        if (state.currentView === 'kanban') {
            renderKanbanView();
        } else {
            renderListView();
        }
    }

    // ---------------------------------------------------------------------------
    // View Rendering: Kanban Board
    // ---------------------------------------------------------------------------
    function renderKanbanView() {
        // Clear all columns
        Object.values(dom.columns).forEach(col => col.innerHTML = '');

        const filtered = getFilteredTasks();
        const counts = { todo: 0, in_progress: 0, review: 0, done: 0 };

        filtered.forEach(task => {
            counts[task.status] = (counts[task.status] || 0) + 1;
            const cardEl = createTaskCard(task);
            if (dom.columns[task.status]) {
                dom.columns[task.status].appendChild(cardEl);
            }
        });

        // Update counts
        Object.keys(counts).forEach(status => {
            if (dom.counts[status]) dom.counts[status].textContent = counts[status];
        });
    }

    function createTaskCard(task) {
        const card = document.createElement('div');
        card.className = `task-card ${task.status === 'done' ? 'status-done-card' : ''}`;
        card.setAttribute('draggable', 'true');
        card.dataset.taskId = task.id;

        // Priority icon & label
        let priorityIcon = 'circle';
        if (task.priority === 'urgent') priorityIcon = 'fire';
        if (task.priority === 'high') priorityIcon = 'bolt';
        if (task.priority === 'medium') priorityIcon = 'diamond';
        if (task.priority === 'low') priorityIcon = 'mug-hot';

        // Due date badge
        const dateInfo = formatDateDisplay(task.due_date);
        let dateHtml = '';
        if (dateInfo) {
            dateHtml = `
                <span class="due-date-badge ${dateInfo.statusClass}">
                    <i class="fa-regular fa-clock"></i> ${dateInfo.text}
                </span>
            `;
        }

        // Subtask badge
        let subtaskHtml = '';
        if (task.subtasks && task.subtasks.length > 0) {
            const completedCount = task.subtasks.filter(s => s.is_completed).length;
            const allDone = completedCount === task.subtasks.length;
            subtaskHtml = `
                <span class="checklist-indicator ${allDone ? 'all-done' : ''}">
                    <i class="fa-solid fa-list-check"></i> ${completedCount}/${task.subtasks.length}
                </span>
            `;
        }

        // Tags
        const tagsHtml = task.tags.map(t => `<span class="task-tag">#${escapeHtml(t)}</span>`).join('');

        card.innerHTML = `
            <div class="card-top">
                <span class="priority-badge priority-${task.priority}">
                    <i class="fa-solid fa-${priorityIcon}"></i> ${task.priority}
                </span>
                <div class="card-actions-quick">
                    <button class="card-icon-action complete-action" title="${task.status === 'done' ? 'Mark uncompleted' : 'Mark completed'}" data-action="toggle-complete">
                        <i class="fa-${task.status === 'done' ? 'solid' : 'regular'} fa-circle-check"></i>
                    </button>
                    <button class="card-icon-action" title="Edit task" data-action="edit">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                </div>
            </div>
            <h4 class="card-title">${escapeHtml(task.title)}</h4>
            ${task.description ? `<p class="card-desc">${escapeHtml(task.description)}</p>` : ''}
            ${tagsHtml ? `<div class="card-tags">${tagsHtml}</div>` : ''}
            <div class="card-footer">
                ${dateHtml || '<span></span>'}
                ${subtaskHtml}
            </div>
        `;

        // Event listeners
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);

        // Click card to open modal (unless quick action buttons were clicked)
        card.addEventListener('click', (e) => {
            const quickActionBtn = e.target.closest('[data-action]');
            if (quickActionBtn) {
                const action = quickActionBtn.dataset.action;
                if (action === 'toggle-complete') {
                    toggleTaskCompletion(task);
                } else if (action === 'edit') {
                    openEditTaskModal(task);
                }
                return;
            }
            openEditTaskModal(task);
        });

        return card;
    }

    // ---------------------------------------------------------------------------
    // View Rendering: List Mode (Flask.io inspired)
    // ---------------------------------------------------------------------------
    function renderListView() {
        dom.listGroupsWrapper.innerHTML = '';
        const filtered = getFilteredTasks();

        const groups = [
            { id: 'todo', title: 'To Do', icon: 'clipboard-list' },
            { id: 'in_progress', title: 'In Progress', icon: 'spinner' },
            { id: 'review', title: 'Review & QA', icon: 'code-pull-request' },
            { id: 'done', title: 'Completed', icon: 'check-double' }
        ];

        groups.forEach(group => {
            const tasksInGroup = filtered.filter(t => t.status === group.id);
            if (tasksInGroup.length === 0) return;

            const groupEl = document.createElement('div');
            groupEl.className = 'list-group';
            groupEl.innerHTML = `
                <div class="list-group-header">
                    <span class="list-group-title">
                        <i class="fa-solid fa-${group.icon}"></i> ${group.title}
                    </span>
                    <span class="col-badge">${tasksInGroup.length}</span>
                </div>
                <div class="list-group-items" id="list-group-${group.id}"></div>
            `;

            const itemsContainer = groupEl.querySelector(`#list-group-${group.id}`);

            tasksInGroup.forEach(task => {
                const row = document.createElement('div');
                row.className = `list-item-row ${task.status === 'done' ? 'is-done' : ''}`;
                
                const dateInfo = formatDateDisplay(task.due_date);
                const isCompleted = task.status === 'done';

                row.innerHTML = `
                    <div class="custom-checkbox ${isCompleted ? 'checked' : ''}" data-task-id="${task.id}">
                        <i class="fa-solid fa-check"></i>
                    </div>
                    <div class="list-item-content">
                        <div class="list-item-title">${escapeHtml(task.title)}</div>
                        <div class="list-item-meta">
                            <span class="priority-badge priority-${task.priority}" style="padding: 0.1rem 0.35rem; font-size: 0.6rem;">${task.priority}</span>
                            ${dateInfo ? `<span class="${dateInfo.statusClass}"><i class="fa-regular fa-clock"></i> ${dateInfo.text}</span>` : ''}
                            ${task.subtasks.length > 0 ? `<span><i class="fa-solid fa-list-check"></i> ${task.subtasks.filter(s => s.is_completed).length}/${task.subtasks.length}</span>` : ''}
                            ${task.tags.map(t => `<span class="task-tag">#${escapeHtml(t)}</span>`).join('')}
                        </div>
                    </div>
                    <div class="list-item-actions">
                        <button class="card-icon-action" data-action="edit" title="Edit Task"><i class="fa-solid fa-pen"></i></button>
                        <button class="card-icon-action" data-action="delete" title="Delete Task"><i class="fa-solid fa-trash-can"></i></button>
                    </div>
                `;

                // Checkbox toggle
                const checkbox = row.querySelector('.custom-checkbox');
                checkbox.addEventListener('click', (e) => {
                    e.stopPropagation();
                    toggleTaskCompletion(task);
                });

                // Row click to edit
                const content = row.querySelector('.list-item-content');
                content.addEventListener('click', () => openEditTaskModal(task));

                const editBtn = row.querySelector('[data-action="edit"]');
                editBtn.addEventListener('click', () => openEditTaskModal(task));

                const delBtn = row.querySelector('[data-action="delete"]');
                delBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm(`Delete task "${task.title}"?`)) {
                        await deleteTask(task.id);
                    }
                });

                itemsContainer.appendChild(row);
            });

            dom.listGroupsWrapper.appendChild(groupEl);
        });

        if (filtered.length === 0) {
            dom.listGroupsWrapper.innerHTML = `
                <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
                    <i class="fa-solid fa-inbox" style="font-size: 2.5rem; margin-bottom: 0.75rem; opacity: 0.5;"></i>
                    <p style="font-size: 1rem; font-weight: 600;">No tasks found matching your filters</p>
                </div>
            `;
        }
    }

    // ---------------------------------------------------------------------------
    // Quick List Input Add Action
    // ---------------------------------------------------------------------------
    dom.quickListSubmitBtn.addEventListener('click', handleQuickListAdd);
    dom.quickListInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleQuickListAdd();
    });

    async function handleQuickListAdd() {
        const title = dom.quickListInput.value.trim();
        if (!title) return;
        const priority = dom.quickListPriority.value;

        await apiRequest('/api/tasks', {
            method: 'POST',
            body: JSON.stringify({
                board_id: state.currentBoardId,
                title,
                priority,
                status: 'todo'
            })
        });

        dom.quickListInput.value = '';
        showToast('Task added to checklist!', 'success');
        await refreshBoardTasks();
    }

    // ---------------------------------------------------------------------------
    // Drag & Drop Kanban Handlers
    // ---------------------------------------------------------------------------
    function handleDragStart(e) {
        state.draggedTaskId = this.dataset.taskId;
        this.classList.add('dragging');
        e.dataTransfer.setData('text/plain', this.dataset.taskId);
        e.dataTransfer.effectAllowed = 'move';
    }

    function handleDragEnd() {
        this.classList.remove('dragging');
        state.draggedTaskId = null;
        Object.values(dom.columns).forEach(col => col.classList.remove('drag-over'));
    }

    // Bind dropzone listeners for each column
    Object.values(dom.columns).forEach(dropzone => {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            dropzone.classList.add('drag-over');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('drag-over');
        });

        dropzone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');

            const taskId = e.dataTransfer.getData('text/plain');
            const newStatus = dropzone.dataset.status;

            if (!taskId || !newStatus) return;

            const task = state.tasks.find(t => t.id === parseInt(taskId, 10));
            if (!task || task.status === newStatus) return;

            // Optimistic update
            task.status = newStatus;
            renderFilteredView();

            if (newStatus === 'done') {
                triggerConfetti();
            }

            try {
                await apiRequest(`/api/tasks/${taskId}/status`, {
                    method: 'PATCH',
                    body: JSON.stringify({ status: newStatus })
                });
                showToast(`Moved to ${newStatus.replace('_', ' ').toUpperCase()}`, 'info');
                updateStats();
            } catch (err) {
                await refreshBoardTasks();
            }
        });
    });

    // ---------------------------------------------------------------------------
    // Quick Task Actions
    // ---------------------------------------------------------------------------
    async function toggleTaskCompletion(task) {
        const newStatus = task.status === 'done' ? 'todo' : 'done';
        task.status = newStatus;
        renderFilteredView();

        if (newStatus === 'done') {
            triggerConfetti();
            showToast('Task completed! 🎉', 'success');
        }

        try {
            await apiRequest(`/api/tasks/${task.id}/status`, {
                method: 'PATCH',
                body: JSON.stringify({ status: newStatus })
            });
            updateStats();
        } catch (err) {
            await refreshBoardTasks();
        }
    }

    async function deleteTask(taskId) {
        await apiRequest(`/api/tasks/${taskId}`, { method: 'DELETE' });
        showToast('Task deleted', 'info');
        closeTaskModal();
        await refreshBoardTasks();
    }

    // ---------------------------------------------------------------------------
    // Task Detail / Edit Modal
    // ---------------------------------------------------------------------------
    function openNewTaskModal(presetStatus = 'todo') {
        state.activeEditingTask = null;
        dom.taskModalHeading.textContent = 'Create New Task';
        dom.taskId.value = '';
        dom.taskTitle.value = '';
        dom.taskDesc.value = '';
        dom.taskStatus.value = presetStatus;
        dom.taskPriority.value = 'medium';
        dom.taskDueDate.value = '';
        dom.taskTags.value = '';
        dom.deleteTaskBtn.style.display = 'none';
        dom.modalSubtaskList.innerHTML = '';
        dom.subtaskProgressText.textContent = '0/0 Completed';

        dom.taskModal.classList.add('show');
        setTimeout(() => dom.taskTitle.focus(), 50);
    }

    function openEditTaskModal(task) {
        state.activeEditingTask = task;
        dom.taskModalHeading.textContent = 'Edit Task Details';
        dom.taskId.value = task.id;
        dom.taskTitle.value = task.title;
        dom.taskDesc.value = task.description || '';
        dom.taskStatus.value = task.status;
        dom.taskPriority.value = task.priority;
        dom.taskDueDate.value = task.due_date || '';
        dom.taskTags.value = task.tags.join(', ');
        dom.deleteTaskBtn.style.display = 'inline-flex';

        renderModalSubtasks(task.subtasks || []);

        dom.taskModal.classList.add('show');
        setTimeout(() => dom.taskTitle.focus(), 50);
    }

    function renderModalSubtasks(subtasks) {
        dom.modalSubtaskList.innerHTML = '';
        const completed = subtasks.filter(s => s.is_completed).length;
        dom.subtaskProgressText.textContent = `${completed}/${subtasks.length} Completed`;

        subtasks.forEach(s => {
            const item = document.createElement('div');
            item.className = `subtask-item ${s.is_completed ? 'completed' : ''}`;
            item.innerHTML = `
                <div class="custom-checkbox ${s.is_completed ? 'checked' : ''}" style="width: 16px; height: 16px;">
                    <i class="fa-solid fa-check" style="font-size: 0.6rem;"></i>
                </div>
                <span>${escapeHtml(s.title)}</span>
                <button type="button" class="subtask-del-btn" title="Delete checklist item">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;

            // Checkbox toggle
            item.querySelector('.custom-checkbox').addEventListener('click', async () => {
                const updated = await apiRequest(`/api/subtasks/${s.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ is_completed: !s.is_completed })
                });
                s.is_completed = updated.is_completed;
                renderModalSubtasks(subtasks);
                refreshBoardTasks();
            });

            // Delete subtask
            item.querySelector('.subtask-del-btn').addEventListener('click', async () => {
                await apiRequest(`/api/subtasks/${s.id}`, { method: 'DELETE' });
                const idx = subtasks.findIndex(sub => sub.id === s.id);
                if (idx !== -1) subtasks.splice(idx, 1);
                renderModalSubtasks(subtasks);
                refreshBoardTasks();
            });

            dom.modalSubtaskList.appendChild(item);
        });
    }

    async function handleAddSubtask() {
        const title = dom.newSubtaskInput.value.trim();
        if (!title) return;

        if (state.activeEditingTask) {
            const created = await apiRequest(`/api/tasks/${state.activeEditingTask.id}/subtasks`, {
                method: 'POST',
                body: JSON.stringify({ title })
            });
            state.activeEditingTask.subtasks.push(created);
            renderModalSubtasks(state.activeEditingTask.subtasks);
            refreshBoardTasks();
        } else {
            // For new task in draft mode, add temporary DOM element
            showToast('Save the task first to attach subtasks', 'info');
        }
        dom.newSubtaskInput.value = '';
    }

    dom.addSubtaskBtn.addEventListener('click', handleAddSubtask);
    dom.newSubtaskInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddSubtask();
        }
    });

    function closeTaskModal() {
        dom.taskModal.classList.remove('show');
        state.activeEditingTask = null;
    }

    dom.closeTaskModalBtn.addEventListener('click', closeTaskModal);
    dom.cancelTaskModalBtn.addEventListener('click', closeTaskModal);

    dom.taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const taskId = dom.taskId.value;
        const payload = {
            board_id: state.currentBoardId,
            title: dom.taskTitle.value.trim(),
            description: dom.taskDesc.value.trim(),
            status: dom.taskStatus.value,
            priority: dom.taskPriority.value,
            due_date: dom.taskDueDate.value || null,
            tags: dom.taskTags.value.split(',').map(s => s.trim()).filter(Boolean)
        };

        if (taskId) {
            await apiRequest(`/api/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            showToast('Task updated successfully', 'success');
        } else {
            await apiRequest('/api/tasks', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            showToast('Task created successfully', 'success');
        }

        closeTaskModal();
        await refreshBoardTasks();
    });

    dom.deleteTaskBtn.addEventListener('click', async () => {
        if (state.activeEditingTask) {
            if (confirm(`Are you sure you want to delete "${state.activeEditingTask.title}"?`)) {
                await deleteTask(state.activeEditingTask.id);
            }
        }
    });

    // ---------------------------------------------------------------------------
    // Column Inline Add Buttons
    // ---------------------------------------------------------------------------
    document.querySelectorAll('.col-add-btn, .col-quick-add').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const status = e.currentTarget.dataset.status;
            openNewTaskModal(status);
        });
    });

    dom.openNewTaskModalBtn.addEventListener('click', () => openNewTaskModal('todo'));

    // ---------------------------------------------------------------------------
    // Board Dropdown & Board Creation
    // ---------------------------------------------------------------------------
    dom.boardDropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dom.boardWrapper.classList.toggle('open');
    });

    function closeBoardDropdown() {
        dom.boardWrapper.classList.remove('open');
    }

    document.addEventListener('click', (e) => {
        if (!dom.boardWrapper.contains(e.target)) {
            closeBoardDropdown();
        }
    });

    dom.openNewBoardModalBtn.addEventListener('click', () => {
        closeBoardDropdown();
        dom.boardName.value = '';
        dom.boardDesc.value = '';
        dom.boardModal.classList.add('show');
        setTimeout(() => dom.boardName.focus(), 50);
    });

    function closeBoardModal() {
        dom.boardModal.classList.remove('show');
    }

    dom.closeBoardModalBtn.addEventListener('click', closeBoardModal);
    dom.cancelBoardModalBtn.addEventListener('click', closeBoardModal);

    dom.boardForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const selectedColor = dom.boardForm.querySelector('input[name="boardColor"]:checked').value;
        const payload = {
            name: dom.boardName.value.trim(),
            description: dom.boardDesc.value.trim(),
            color: selectedColor
        };

        const newBoard = await apiRequest('/api/boards', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        showToast(`Created board "${newBoard.name}"`, 'success');
        closeBoardModal();
        await loadBoards();
        setActiveBoard(newBoard.id);
    });

    // ---------------------------------------------------------------------------
    // Demo Reset Button
    // ---------------------------------------------------------------------------
    dom.resetDataBtn.addEventListener('click', async () => {
        if (confirm('Reset to sample sprint tasks and boards? Any custom edits will be refreshed.')) {
            await apiRequest('/api/reset', { method: 'POST' });
            showToast('Sprint demo data restored', 'success');
            await loadBoards();
            if (state.boards.length > 0) setActiveBoard(state.boards[0].id);
        }
    });

    // ---------------------------------------------------------------------------
    // View Switcher (Kanban vs List)
    // ---------------------------------------------------------------------------
    dom.viewKanbanBtn.addEventListener('click', () => {
        state.currentView = 'kanban';
        dom.viewKanbanBtn.classList.add('active');
        dom.viewListBtn.classList.remove('active');
        dom.kanbanView.style.display = 'grid';
        dom.listView.style.display = 'none';
        renderFilteredView();
    });

    dom.viewListBtn.addEventListener('click', () => {
        state.currentView = 'list';
        dom.viewListBtn.classList.add('active');
        dom.viewKanbanBtn.classList.remove('active');
        dom.kanbanView.style.display = 'none';
        dom.listView.style.display = 'block';
        renderFilteredView();
    });

    // ---------------------------------------------------------------------------
    // Filters & Search Handlers
    // ---------------------------------------------------------------------------
    dom.priorityFilterGroup.querySelectorAll('.filter-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            dom.priorityFilterGroup.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.filterPriority = pill.dataset.priority;
            renderFilteredView();
        });
    });

    dom.tagFilterSelect.addEventListener('change', () => {
        state.filterTag = dom.tagFilterSelect.value;
        renderFilteredView();
    });

    dom.searchInput.addEventListener('input', () => {
        state.searchQuery = dom.searchInput.value.trim();
        renderFilteredView();
    });

    dom.clearFiltersBtn.addEventListener('click', () => {
        state.filterPriority = 'all';
        state.filterTag = '';
        state.searchQuery = '';
        dom.searchInput.value = '';
        dom.tagFilterSelect.value = '';
        dom.priorityFilterGroup.querySelectorAll('.filter-pill').forEach(p => {
            p.classList.toggle('active', p.dataset.priority === 'all');
        });
        renderFilteredView();
        showToast('Filters cleared', 'info');
    });

    // ---------------------------------------------------------------------------
    // Global Keyboard Shortcuts
    // ---------------------------------------------------------------------------
    document.addEventListener('keydown', (e) => {
        // Don't trigger shortcuts when typing inside form inputs
        const isEditingInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);

        if (e.key === 'Escape') {
            closeTaskModal();
            closeBoardModal();
            closeBoardDropdown();
            return;
        }

        if (!isEditingInput) {
            if (e.key === '/' || e.key === 'f') {
                e.preventDefault();
                dom.searchInput.focus();
            } else if (e.key === 'n' || e.key === 'N') {
                e.preventDefault();
                openNewTaskModal('todo');
            }
        }
    });

    // Initial boot
    loadInitialData();
});
