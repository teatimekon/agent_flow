import logging
import os.path
from datetime import datetime

# 创建一个logger
logger = logging.getLogger('Agent_Flow')
logger.setLevel(logging.INFO)

# 获取当天的日期，在logs文件夹下每天生成一个日志文件
rq = datetime.now().strftime("%Y%m%d")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_path = os.path.join(project_root, 'logs')
log_name = os.path.join(log_path, f"{rq}.log")

# 创建FileHandler，用于写入日志文件
fh = logging.FileHandler(log_name, encoding="utf-8", mode='a+')
fh.setLevel(logging.DEBUG)

# 创建StreamHandler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

# 确保其他模块不会重复输出日志
logger.propagate = False

def get_logger():
    return logger

# 日志方法
def info(msg):
    logger.info(msg)

def debug(msg):
    logger.debug(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)
