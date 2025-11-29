class InvalidFileTypeError(Exception):
    """
    Exception raised for invalid file types.
    """
    pass

class BitrateTooLowError(Exception):
    """
    Exception raised when the calculated bitrate is too low.
    """
    pass

class TooManyAttemptsError(Exception):
    """
    Exception raised when maximum compression attempts are exceeded.
    """
    pass