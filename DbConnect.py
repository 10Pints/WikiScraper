# DDbConnect.py
#
import pyodbc as pyodbc
def DbConnect():
    print('MnRtn 000: starting, connecting to sql server db')

    #DRIVER={SQL Server}
    '''
    'DRIVER={ODBC Driver 13 for SQL Server};'
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'DRIVER={SQL Server Native Client 10.0}'
    'DRIVER={SQL Server};'
    '''
    conn = pyodbc.connect( 'DRIVER={ODBC Driver 18 for SQL Server};'
                        'SERVER=DevI9;'
                        'DATABASE=farming_dev;'
                        'Trusted_Connection=yes;'
                        )

    conn.autocommit = True
    cursor = conn.cursor()
    print('MnRtn 010: executing sql select pathogen data cmd')
    cursor.execute('Select pathogen_id, pathogen_nm,latin_nm FROM pathogen')
    return conn

'''

cursor = conn.cursor()

#with named parameters: cursor.execute('EXEC usp_get_user_data @name = ?, @username = ?', 'tim', 'flipperpa')
conn.autocommit = True
'''