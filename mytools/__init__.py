import time

import mytools.Mek_master


def get_problem_id():
    return f'{Mek_master.get_numbertime()}-{Mek_master.get_random_hax(5)}'


def get_u_token(uid):
    token = Mek_master.get_string_MD5(f'{uid}+{Mek_master.get_numbertime()[0:7]}')
    # print(token)
    return token


def get_m_token(name):
    token = Mek_master.get_string_MD5(f'{name}+{Mek_master.get_numbertime()[0:7]}')
    # print(token)
    return token
