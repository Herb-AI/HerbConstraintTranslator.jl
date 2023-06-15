import time

def timeit(f):
    def inner(*args, **kwargs):
        start = time.time()
        retval = f(*args, **kwargs)
        end = time.time()
        print(f"Took {end-start} seconds")
        return retval
    return inner
