# test_GetAlternariaSp.py
import logging.config
import pytest   # The test framework
from GetAlternariaSp import GetAlternariaSp

logger = logging.getLogger("my_app")

def test_1():
    #pytest.set_trace()
    logger.info('GetAlternariaSp.py: starting')
    
    GetAlternariaSp()
    logger.info('GetAlternariaSp.py: leaving')
    
    
if __name__ == '__main__':
    test_1()