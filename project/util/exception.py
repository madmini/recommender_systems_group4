class MovieNotFoundException(Exception):
    """ MovieID does not exist. """
    pass


class UserNotFoundException(Exception):
    """ UserID does not exist. """
    pass


class MethodNotFoundException(Exception):
    """ Method does not exist. """
    pass


class MissingDataException(Exception):
    """ Data for evaluation is missing. """
    pass
