import logging
from logging.handlers import RotatingFileHandler
import os

# 日志文件路径
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "app.log")

# 创建 RotatingFileHandler，限制日志文件大小为5MB，最多保留3个文件
file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.ERROR)

# 创建控制台日志输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 获取 FastAPI logger 实例
logger = logging.getLogger("fastapi")
logger.setLevel(logging.INFO)

# 添加处理器到 logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 禁止重复日志
logger.propagate = False
