from gevent import monkey
from gevent.pywsgi import WSGIServer

import mytools.Mek_master

monkey.patch_all()

import datetime
import os
from multiprocessing import cpu_count
from multiprocessing import Process
from app import app


def run(MULTI_PROCESS):
    if MULTI_PROCESS == False:
        WSGIServer(('0.0.0.0', 8080), app).serve_forever()
    else:
        mulserver = WSGIServer(('0.0.0.0', 8080), app)
        mulserver.start()

        def server_forever():
            mulserver.start_accepting()
            mulserver._stop_event.wait()

        for i in range(cpu_count()):
            p = Process(target=server_forever)
            p.start()


if __name__ == "__main__":
    # 单进程 + 协程
    mytools.Mek_master.logo_Slabt()
    run(False)
    # 多进程 + 协程
    # run(True)
