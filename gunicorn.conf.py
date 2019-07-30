import multiprocessing

bind = "127.0.0.1:6001"
workers = multiprocessing.cpu_count() * 2 + 1
