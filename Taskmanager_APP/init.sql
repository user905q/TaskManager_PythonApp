PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#4a90e2',
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    section_id INTEGER,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    deadline DATETIME,
    color TEXT DEFAULT '#ffffff',
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#cccccc',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS time_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    column_id INTEGER,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    duration_sec INTEGER,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (column_id) REFERENCES board_columns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS board_columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    color TEXT DEFAULT '#e0e0e0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_columns (
    task_id INTEGER NOT NULL,
    column_id INTEGER NOT NULL,
    moved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, column_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (column_id) REFERENCES board_columns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    channel TEXT DEFAULT 'tray',
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO tags (name, color) VALUES
    ('Высокий приоритет', '#e74c3c'),
    ('Средний приоритет', '#f39c12'),
    ('Низкий приоритет', '#27ae60'),
    ('Личное', '#9b59b6'),
    ('Работа', '#3498db'),
    ('Учеба', '#1abc9c'),
    ('Срочное', '#e67e22');

INSERT OR IGNORE INTO board_columns (id, name, position, color) VALUES
    (1, 'Нужно выполнить', 1, '#e74c3c'),
    (2, 'В процессе', 2, '#f39c12'),
    (3, 'Выполнено', 3, '#27ae60');