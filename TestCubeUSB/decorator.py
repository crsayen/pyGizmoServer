from functools import lru_cache

def decorator(func):
    def inner(*args, **kwargs):
        print("before")
        func(*args, **kwargs)
        print("after")
    return inner

@decorator
def decorated(s):
    print(s)

decorated('s')

@lru_cache
decorated('ajsdkl;fjadjfalkd')