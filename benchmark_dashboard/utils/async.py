
from threading import Thread

def run_async(method):
    """this method should be overwritten
    """
    Thread(target=method, args=[]).start()
