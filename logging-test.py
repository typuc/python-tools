import logging
import logging.config
from logging import handlers
logging.config.fileConfig('logging.config')
logger = logging.getLogger("rotatingFileLogger")
logger.info("test")
logger.info("111")
logger.info("11")
logger.warning("1111")

####
# import logging
# import logging.config
# import time
# from logging import handlers
# time_rota_handler = handlers.TimedRotatingFileHandler(filename='time_ctr.log',
#                                                       when='s',              # 时间单位，周：w；天:d；时: h；分：m；秒: s
#                                                       interval=1,            # 间隔多久切一个
#                                                       backupCount=5,         # 备份日志保留个数，多余自动删除
#                                                       encoding='utf-8')
# time_rota_handler.setFormatter(
#     logging.Formatter(
#         fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s[%(lineno)d]:  %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     ))
#
# logger_01 = logging.Logger(name='千行BUG率', level=logging.INFO,)
# logger_01.addHandler(time_rota_handler)
# while True:
#     time.sleep(1)
#     logger_01.info('debug message')


