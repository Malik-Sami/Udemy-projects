import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify
from typing import cast
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Database Models
# ---------------------------------------------------------------------------

class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), default="")
    icon = db.Column(db.String(50), default="folder")
    color = db.Column(db.String(20), default="#6366f1")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='board', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        tasks = cast(list, self.tasks) if self.tasks else []
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'task_count': len(tasks),
            'completed_count': sum(1 for t in tasks if getattr(t, 'status', '') == 'done')
        }


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="todo")  # todo, in_progress, review, done
    priority = db.Column(db.String(20), default="medium")  # low, medium, high, urgent
    due_date = db.Column(db.Date, nullable=True)
    tags = db.Column(db.String(200), default="")  # comma separated
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subtasks = db.relationship('Subtask', backref='task', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        tag_list = [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []
        return {
            'id': self.id,
            'board_id': self.board_id,
            'title': self.title,
            'description': self.description or "",
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': tag_list,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'subtasks': [s.to_dict() for s in self.subtasks]
        }


class Subtask(db.Model):
    __tablename__ = 'subtasks'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'is_completed': self.is_completed
        }


# ---------------------------------------------------------------------------
# Default Sample Data
# ---------------------------------------------------------------------------

def seed_sample_data():
    if Board.query.first():
        return  # Data already seeded

    # Default Project 1: Product Sprint
    sprint_board = Board(
        name="Sprint Roadmap & Delivery",
        description="Core product features and engineering deliverables",
        icon="rocket",
        color="#6366f1"
    )
    # Default Project 2: Personal & Growth
    personal_board = Board(
        name="Personal & Career Goals",
        description="Interview prep, portfolio polish, and learning tracks",
        icon="user-astronaut",
        color="#ec4899"
    )

    db.session.add_all([sprint_board, personal_board])
    db.session.commit()

    today = date.today()

    tasks_data = [
        {
            "board_id": sprint_board.id,
            "title": "Design responsive Kanban UI & task modal",
            "description": "Create glassmorphic dark-mode interface with smooth drag & drop animations and accessible contrast ratios.",
            "status": "done",
            "priority": "high",
            "due_date": today - timedelta(days=1),
            "tags": "Design, Frontend",
            "subtasks": [
                ("Draft responsive column layout", True),
                ("Add dark/light glass theme CSS tokens", True),
                ("Verify mobile viewports", True)
            ]
        },
        {
            "board_id": sprint_board.id,
            "title": "Build RESTful API & SQLite ORM persistence",
            "description": "Implement Flask endpoints for board/task CRUD, subtask management, and status updates.",
            "status": "done",
            "priority": "urgent",
            "due_date": today,
            "tags": "Backend, API",
            "subtasks": [
                ("Setup SQLAlchemy models", True),
                ("Create drag-and-drop reorder endpoints", True)
            ]
        },
        {
            "board_id": sprint_board.id,
            "title": "Implement drag-and-drop column transitions",
            "description": "Enable native HTML5 drag-and-drop events with drop target highlights, audio/visual cues, and instant status synchronisation.",
            "status": "in_progress",
            "priority": "urgent",
            "due_date": today + timedelta(days=1),
            "tags": "Frontend, UX",
            "subtasks": [
                ("Configure dragstart and dragover event handlers", True),
                ("Add smooth drop animation", False),
                ("Handle touch devices fallback", False)
            ]
        },
        {
            "board_id": sprint_board.id,
            "title": "Conduct security audit & input sanitization",
            "description": "Review task input fields for XSS protection, validate due dates, and ensure proper SQL injection mitigation.",
            "status": "review",
            "priority": "high",
            "due_date": today + timedelta(days=3),
            "tags": "Security, QA",
            "subtasks": [
                ("Sanitize HTML text inputs", False),
                ("Check CSRF and payload limits", False)
            ]
        },
        {
            "board_id": sprint_board.id,
            "title": "Add analytics metrics & sprint velocity dashboard",
            "description": "Display completion percentage, overdue warnings, and priority distribution bar chart for project managers.",
            "status": "todo",
            "priority": "medium",
            "due_date": today + timedelta(days=5),
            "tags": "Analytics, Product",
            "subtasks": [
                ("Compute overdue count dynamically", False),
                ("Render interactive completion progress bar", False)
            ]
        },
        {
            "board_id": sprint_board.id,
            "title": "Prepare portfolio presentation & interview talking points",
            "description": "Document architectural decisions, state management, and real-time UX for technical hiring managers.",
            "status": "todo",
            "priority": "low",
            "due_date": today + timedelta(days=7),
            "tags": "Documentation",
            "subtasks": [
                ("Record quick walk-through GIF/demo", False),
                ("Highlight Jira & Trello comparison metrics", False)
            ]
        },
        # Personal Board Tasks
        {
            "board_id": personal_board.id,
            "title": "Practice System Design: Task Manager Architecture",
            "description": "Study data structures, WebSocket syncing, database indexing, and scalability patterns for collaborative kanban boards.",
            "status": "in_progress",
            "priority": "high",
            "due_date": today + timedelta(days=2),
            "tags": "Interview, Architecture",
            "subtasks": [
                ("Study optimistic UI updates", True),
                ("Review distributed locking for collaborative boards", False)
            ]
        },
        {
            "board_id": personal_board.id,
            "title": "Complete 100 Days of Python portfolio project",
            "description": "Build high-impact web application with clean code and deploy-ready structure.",
            "status": "done",
            "priority": "urgent",
            "due_date": today,
            "tags": "Portfolio, Python",
            "subtasks": [
                ("Implement web application", True),
                ("Write comprehensive documentation", True)
            ]
        }
    ]

    for t_data in tasks_data:
        subtasks_list = cast(list, t_data.pop("subtasks", []))
        task = Task(**t_data)
        db.session.add(task)
        db.session.flush()

        for st_title, is_comp in subtasks_list:
            subtask = Subtask(task_id=task.id, title=st_title, is_completed=is_comp)
            db.session.add(subtask)

    db.session.commit()


# ---------------------------------------------------------------------------
# Web Views
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.route('/api/boards', methods=['GET', 'POST'])
def handle_boards():
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Board name is required'}), 400

        board = Board(
            name=name,
            description=data.get('description', '').strip(),
            icon=data.get('icon', 'folder'),
            color=data.get('color', '#6366f1')
        )
        db.session.add(board)
        db.session.commit()
        return jsonify(board.to_dict()), 201

    boards = Board.query.order_by(Board.created_at.asc()).all()
    return jsonify([b.to_dict() for b in boards])


@app.route('/api/boards/<int:board_id>', methods=['GET', 'PUT', 'DELETE'])
def board_detail(board_id):
    board = db.session.get(Board, board_id)
    if not board:
        return jsonify({'error': 'Board not found'}), 404

    if request.method == 'DELETE':
        db.session.delete(board)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Board deleted'})

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'name' in data and data['name'].strip():
            board.name = data['name'].strip()
        if 'description' in data:
            board.description = data['description'].strip()
        if 'color' in data:
            board.color = data['color']
        if 'icon' in data:
            board.icon = data['icon']
        db.session.commit()
        return jsonify(board.to_dict())

    return jsonify(board.to_dict())


@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        board_id = data.get('board_id')

        if not title:
            return jsonify({'error': 'Title is required'}), 400
        if not board_id:
            # Default to first board if none specified
            first_board = Board.query.first()
            if not first_board:
                return jsonify({'error': 'No board exists'}), 400
            board_id = first_board.id

        due_date_obj = None
        if data.get('due_date'):
            try:
                due_date_obj = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        tags_val = data.get('tags', '')
        if isinstance(tags_val, list):
            tags_val = ', '.join(tags_val)

        task = Task(
            board_id=board_id,
            title=title,
            description=data.get('description', '').strip(),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=due_date_obj,
            tags=tags_val,
            order_index=data.get('order_index', 0)
        )
        db.session.add(task)
        db.session.commit()

        # Handle subtasks if provided
        raw_subtasks = data.get('subtasks', [])
        for st in raw_subtasks:
            st_title = st.get('title', '').strip() if isinstance(st, dict) else str(st).strip()
            if st_title:
                is_comp = st.get('is_completed', False) if isinstance(st, dict) else False
                subtask = Subtask(task_id=task.id, title=st_title, is_completed=is_comp)
                db.session.add(subtask)

        db.session.commit()
        return jsonify(task.to_dict()), 201

    # GET filter support
    board_id = request.args.get('board_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('search', '').strip()

    query = Task.query

    if board_id:
        query = query.filter_by(board_id=board_id)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if search:
        query = query.filter(Task.title.ilike(f'%{search}%') | Task.description.ilike(f'%{search}%') | Task.tags.ilike(f'%{search}%'))

    tasks = query.order_by(Task.order_index.asc(), Task.id.desc()).all()
    return jsonify([t.to_dict() for t in tasks])


@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task deleted'})

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'title' in data and data['title'].strip():
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description'].strip()
        if 'status' in data and data['status'] in ['todo', 'in_progress', 'review', 'done']:
            task.status = data['status']
        if 'priority' in data and data['priority'] in ['low', 'medium', 'high', 'urgent']:
            task.priority = data['priority']
        if 'board_id' in data:
            task.board_id = data['board_id']
        if 'order_index' in data:
            task.order_index = data['order_index']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                except ValueError:
                    task.due_date = None
            else:
                task.due_date = None
        if 'tags' in data:
            tags_val = data['tags']
            if isinstance(tags_val, list):
                task.tags = ', '.join(tags_val)
            else:
                task.tags = tags_val

        db.session.commit()
        return jsonify(task.to_dict())

    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ['todo', 'in_progress', 'review', 'done']:
        return jsonify({'error': 'Invalid status'}), 400

    task.status = new_status
    if 'order_index' in data:
        task.order_index = data['order_index']

    db.session.commit()
    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
def add_subtask(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Subtask title is required'}), 400

    subtask = Subtask(task_id=task.id, title=title, is_completed=False)
    db.session.add(subtask)
    db.session.commit()
    return jsonify(subtask.to_dict()), 201


@app.route('/api/subtasks/<int:subtask_id>', methods=['PUT', 'DELETE'])
def manage_subtask(subtask_id):
    subtask = db.session.get(Subtask, subtask_id)
    if not subtask:
        return jsonify({'error': 'Subtask not found'}), 404

    if request.method == 'DELETE':
        db.session.delete(subtask)
        db.session.commit()
        return jsonify({'success': True})

    data = request.get_json() or {}
    if 'is_completed' in data:
        subtask.is_completed = bool(data['is_completed'])
    if 'title' in data and data['title'].strip():
        subtask.title = data['title'].strip()

    db.session.commit()
    return jsonify(subtask.to_dict())


@app.route('/api/stats', methods=['GET'])
def get_stats():
    board_id = request.args.get('board_id', type=int)
    query = Task.query
    if board_id:
        query = query.filter_by(board_id=board_id)

    all_tasks = query.all()
    total = len(all_tasks)
    done_count = sum(1 for t in all_tasks if t.status == 'done')
    in_progress_count = sum(1 for t in all_tasks if t.status == 'in_progress')
    review_count = sum(1 for t in all_tasks if t.status == 'review')
    todo_count = sum(1 for t in all_tasks if t.status == 'todo')

    today = date.today()
    overdue_count = sum(
        1 for t in all_tasks 
        if t.due_date and t.due_date < today and t.status != 'done'
    )

    priority_counts = {
        'urgent': sum(1 for t in all_tasks if t.priority == 'urgent'),
        'high': sum(1 for t in all_tasks if t.priority == 'high'),
        'medium': sum(1 for t in all_tasks if t.priority == 'medium'),
        'low': sum(1 for t in all_tasks if t.priority == 'low'),
    }

    completion_rate = round((done_count / total * 100), 1) if total > 0 else 0

    return jsonify({
        'total': total,
        'todo': todo_count,
        'in_progress': in_progress_count,
        'review': review_count,
        'done': done_count,
        'overdue': overdue_count,
        'completion_rate': completion_rate,
        'priority_counts': priority_counts
    })


@app.route('/api/reset', methods=['POST'])
def reset_database():
    """Resets database and re-seeds sample project and sprint tasks."""
    Subtask.query.delete()
    Task.query.delete()
    Board.query.delete()
    db.session.commit()
    seed_sample_data()
    return jsonify({'success': True, 'message': 'Database re-seeded with demo data'})


# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    seed_sample_data()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
