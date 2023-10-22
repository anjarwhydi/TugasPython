import logging 
 
logging.basicConfig(filename=r"E:\Bootcamp\TugasPython\app\logs\log_flask.log", level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
logger = logging.getLogger('test-logger')