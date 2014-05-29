"""
Generic runnable object that takes a function and arguments then runs it.
"""

# It's a class with an init and one function, hooray!

class Runner(object):

    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.function(*self.args, **self.kwargs)
