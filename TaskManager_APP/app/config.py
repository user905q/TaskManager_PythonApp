import os
import sys
from pathlib import Path

# Определение базовой директории (папка с .exe или скриптом)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Попытка использовать папку с приложением, если нет прав - %APPDATA%
try:
    TEST_FILE = BASE_DIR / ".write_test"
    TEST_FILE.touch()
    TEST_FILE.unlink()
    DATA_DIR = BASE_DIR
except PermissionError:
    appdata = os.getenv('APPDATA')
    DATA_DIR = Path(appdata) / "TaskManager" if appdata else BASE_DIR
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# Пути
DB_PATH = DATA_DIR / "tasks.db"
STORAGE_DIR = DATA_DIR / "storage"
BACKUPS_DIR = DATA_DIR / "backups"
LOG_PATH = DATA_DIR / "error.log"
LOCK_FILE = DATA_DIR / "app.lock"

# Создание директорий
STORAGE_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

# Лимиты и константы
MAX_ATTACHMENTS = 10
MAX_COLUMNS = 10
MAX_TITLE_LEN = 255
MAX_TAG_LEN = 50
MAX_COLUMN_LEN = 50
DEADLINE_WARNING_MINUTES = 30

# Системные константы
SYSTEM_SECTION_NAME = "Задачи без раздела"
DEFAULT_COLUMNS = ["Нужно выполнить", "В процессе", "Выполнено"]
DEFAULT_TAGS = [
    "Высокий приоритет", "Средний приоритет", "Низкий приоритет",
    "Личное", "Работа", "Учеба", "Срочное"
]