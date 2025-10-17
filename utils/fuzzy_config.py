"""Конфигурация для модуля fuzzy matching приветствий."""

# Пороги сходства для разных типов приветствий
FORMAL_GREETING_THRESHOLD = 90  # "здравствуйте", "добрый день"
INFORMAL_GREETING_THRESHOLD = 85  # "привет", "хай"
SHORT_GREETING_THRESHOLD = 80  # "привет", "хай"
QUESTION_GREETING_THRESHOLD = 85  # "как дела", "как поживаете"
THANKS_GREETING_THRESHOLD = 85  # "спасибо", "благодарю"

# Максимальная длина текста для fuzzy сравнения
MAX_FUZZY_LENGTH = 50

# Весовые коэффициенты для алгоритма Левенштейна
INSERTION_COST = 1
DELETION_COST = 1
SUBSTITUTION_COST = 2

# Настройки для rapidfuzz
FUZZY_SCORER = (
    "ratio"  # "ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"
)

# Кэширование результатов fuzzy matching
ENABLE_FUZZY_CACHE = True
FUZZY_CACHE_SIZE = 1000

# Логирование fuzzy matching
LOG_FUZZY_MATCHES = True
LOG_FUZZY_THRESHOLD = 70  # Логировать только если сходство >= этого порога

# Типы приветствий для разных порогов
GREETING_TYPES = {
    "formal": {
        "patterns": ["здравствуйте", "добрый день", "доброе утро", "добрый вечер"],
        "threshold": FORMAL_GREETING_THRESHOLD,
    },
    "informal": {
        "patterns": ["привет", "хай", "хелло", "хей"],
        "threshold": INFORMAL_GREETING_THRESHOLD,
    },
    "short": {"patterns": ["привет", "хай"], "threshold": SHORT_GREETING_THRESHOLD},
    "question": {
        "patterns": ["как дела", "как поживаете", "как настроение"],
        "threshold": QUESTION_GREETING_THRESHOLD,
    },
    "thanks": {
        "patterns": ["спасибо", "благодарю"],
        "threshold": THANKS_GREETING_THRESHOLD,
    },
}
