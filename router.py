class Router:
    def __init__(self):
        self.routes = {}

    def register(self, route_name):
        def func_decorator(func):
            self.routes[route_name] = func
            return lambda :func
        return func_decorator

    def dispatch(self, route_name):
        return self.routes[route_name]
