"""
NorthStar custom exceptions.
"""


class NorthStarError(Exception):
    """
    Base exception for the NorthStar platform.
    """


class ConfigurationError(NorthStarError):
    """
    Raised when configuration is invalid.
    """


class RepositoryError(NorthStarError):
    """
    Raised when repository operations fail.
    """


class ModelNotFoundError(NorthStarError):
    """
    Raised when a required model can not be located.
    """