class Failure:

    def __init__(self, exception, request=None, response=None, func_name=""):
        self.exception = exception
        self.request = request
        self.response = response
        self.func_name = func_name

    def check(self, exception_type):
        """
        Checks if the exception type is valid.
        """
        if isinstance(self.exception, exception_type):
            return True
        return False
