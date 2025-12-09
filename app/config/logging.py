import logging
import os
from logging.handlers import RotatingFileHandler

# 日志目录
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 清除默认处理器
root_logger.handlers.clear()

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# 所有日志文件处理器
all_log_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,  # 保留5个备份
    encoding="utf-8"
)
all_log_handler.setLevel(logging.INFO)
all_log_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
all_log_handler.setFormatter(all_log_formatter)
root_logger.addHandler(all_log_handler)

# 错误日志文件处理器
error_log_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "error.log"),
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3,  # 保留3个备份
    encoding="utf-8"
)
error_log_handler.setLevel(logging.ERROR)
error_log_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
error_log_handler.setFormatter(error_log_formatter)
root_logger.addHandler(error_log_handler)

# 调试日志文件处理器
debug_log_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "debug.log"),
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3,  # 保留3个备份
    encoding="utf-8"
)
debug_log_handler.setLevel(logging.DEBUG)
debug_log_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
debug_log_handler.setFormatter(debug_log_formatter)
root_logger.addHandler(debug_log_handler)

# 配置模块日志记录器
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("slowapi").setLevel(logging.WARNING)
logging.getLogger("redis").setLevel(logging.WARNING)

# 导出日志记录器
logger = root_logger
