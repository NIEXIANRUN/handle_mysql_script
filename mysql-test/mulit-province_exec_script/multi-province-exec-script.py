from mysql_connection import DBConnection
import time
from concurrent.futures import ThreadPoolExecutor
pool = ThreadPoolExecutor(5)


def get_sql_list(file):
    with open(file, 'r', encoding='utf-8') as f:
        sql_data = ''
        for line in f.readlines():
            if len(line) == 0:
                continue
            elif line.startswith('--'):
                continue
            else:
                sql_data += line
        sql_list = sql_data.split(';')[:-1]
        sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
        return sql_list


def get_db_info_list(config_file):
    with open(config_file, 'r') as f:
        db_info_list = []
        for line in f.readlines():
            host, port, database = line.strip(',')
            db_info = dict(user='inception', password='123456')
            db_info['host'] = host.strip()
            db_info['port'] = int(port.strip())
            db_info['database'] = database.strip()
            db_info_list.append(db_info)
        return db_info_list


def sync_run_script(db_info):
    sql_list = get_sql_list(sql_script_file)
    with DBConnection.DBConnectionManager(**db_info) as db_client:
        for sql in sql_list:
            res = db_client.exe(sql)
            format_str = '{0} {1} 执行脚本 {2}'.format(db_info['host'], db_info['port'], sql)
            print(format_str)


if __name__ == '__main__':
    sql_script_file = 'insert.txt'
    config_file = 'config.txt'

    db_info_list = get_db_info_list(config_file)
    with pool as executor:
        results = executor.map(sync_run_script, db_info_list)
    print(list(results))
