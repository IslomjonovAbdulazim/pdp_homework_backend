# Line limit options for homework
LINE_LIMIT_OPTIONS = [300, 600, 900, 1200]

# Supported file extensions
FILE_EXTENSION_OPTIONS = [
    ".py", ".dart", ".java", ".cpp", ".c", ".js",
    ".ts", ".go", ".rs", ".kt", ".swift"
]

# System limits
MAX_FILES_PER_HOMEWORK = 5
MAX_LINES_PER_FILE = 500
MAX_SESSIONS_PER_USER = 3

# Grading rubrics
GRADING_RUBRICS = [
    "task_completeness",
    "code_quality",
    "correctness"
]

# JWT settings
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 7  # 1 week
ALGORITHM = "HS256"