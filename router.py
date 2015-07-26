class Router:
    def __init__(self):
        self.routes = {}

    def register(self, route_name):
        def func_decorator(func):
            self.routes[route_name] = func
            return lambda :func
        return func_decorator

    # TODO: Just get rid of the *args call and make it return a function
    # I don't know what's pythonic here
    def dispatch(self, route_name, *args):
        return self.routes[route_name](*args)
