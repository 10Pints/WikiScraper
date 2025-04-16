# DDbConnect.py
# mod from wikiscraper 2
# mod from wikiscraper 1
import pyodbc as pyodbc
import logging.config
logger = logging.getLogger("my_app")

def DbConnect():
    logger.info('DbConnect 000: starting, connecting to sql server DevI9 farming_dev')

    conn = pyodbc.connect( 'DRIVER={ODBC Driver 18 for SQL Server};'
                        'SERVER=DevI9;'
                        'DATABASE=farming_dev;'
                        'Trusted_Connection=yes;'
                        )

    conn.autocommit = True
    logger.info('DbConnect 999: connected')
    return conn #cursor.fetchall()
