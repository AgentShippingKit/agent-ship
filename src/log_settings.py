import logging
import sys
import os
import colorlog
from pythonjsonlogger import jsonlogger

class Config:
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "INFO"
    LOG_FILE_PATH = "app.log"

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    LOG_FILE_PATH = "dev_app.log"

class ProductionConfig(Config):
    LOG_LEVEL = "ERROR"
    LOG_FILE_PATH = "/var/log/app/app.log"

class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = "DEBUG"
    LOG_FILE_PATH = "test_app.log"

def get_config():
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
    

config = get_config()

# Respect explicit LOG_LEVEL env var across all environments
_env_log_level = os.getenv("LOG_LEVEL")
if _env_log_level:
    config.LOG_LEVEL = _env_log_level.upper()

# Define the formatters
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

file_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(module)s %(message)s')

# Define the logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        },
        "standard": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(module)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": config.LOG_LEVEL,
            "formatter": "color" if config.DEBUG or config.TESTING else "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": config.LOG_LEVEL,
            "formatter": "json" if os.getenv("FASTAPI_ENV") == "production" else "standard",
            "filename": config.LOG_FILE_PATH,
        },
    },
    "root": {
        "level": config.LOG_LEVEL,
        "handlers": ["console", "file"],
    },
    "loggers": {
        "uvicorn": {
            "level": config.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # Common noisy libraries; align them to configured level
        "litellm": {
            "level": config.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # Suppress LiteLLM LoggingWorker event loop errors (non-critical)
        "litellm.litellm_core_utils.logging_worker": {
            "level": "ERROR",  # Only show errors, suppress warnings about event loops
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "base_events": {
            "level": "ERROR",  # Suppress "Task exception was never retrieved" warnings from LiteLLM
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "httpx": {
            "level": config.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "app": {
            "level": config.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

def configure_logging():
    # On Heroku, only use console logging (no file writing allowed)
    if os.getenv('DYNO'):
        # Heroku environment - only console logging
        heroku_config = LOGGING_CONFIG.copy()
        heroku_config['handlers'] = {'console': heroku_config['handlers']['console']}
        heroku_config['root']['handlers'] = ['console']
        for logger_name in heroku_config['loggers']:
            heroku_config['loggers'][logger_name]['handlers'] = ['console']
        logging.config.dictConfig(heroku_config)
    else:
        # Local environment - try to use both console and file, fallback to console-only if file fails
        log_file_path = config.LOG_FILE_PATH
        
        # Check if we can create the log file
        can_use_file = True
        try:
            # Ensure log file directory exists for absolute paths
            if os.path.isabs(log_file_path):
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
            
            # Try to open the file to see if we can write to it
            # Use 'a' mode to append (won't fail if file exists) and ensure we close it
            with open(log_file_path, 'a'):
                pass
        except (OSError, PermissionError, IOError) as e:
            # Can't create/write to log file, skip file handler
            can_use_file = False
            import warnings
            warnings.warn(f"Unable to create log file '{log_file_path}': {e}. Using console-only logging.", UserWarning)
        
        if can_use_file:
            # Use both console and file logging
            logging.config.dictConfig(LOGGING_CONFIG)
        else:
            # Fallback to console-only logging
            fallback_config = LOGGING_CONFIG.copy()
            fallback_config['handlers'] = {'console': fallback_config['handlers']['console']}
            fallback_config['root']['handlers'] = ['console']
            for logger_name in fallback_config['loggers']:
                fallback_config['loggers'][logger_name]['handlers'] = ['console']
            logging.config.dictConfig(fallback_config)