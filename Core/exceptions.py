class MagnetException(BaseException):
    '''This exception is raised when a RawMagnet model is bad created'''
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Sorry, this model seems not correct: %s" % self.reason
