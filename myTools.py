import sys

def info(message, **kwargs):
    kwargs["file"] = sys.stderr
    print(message, **kwargs)
