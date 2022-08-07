class DataLog:
    """
    A tool for logging data.

    Args:
        headers (str): Column headers. These are the names of the data columns. For example, choose 'time' and 'angle'.
        name (str): Name of the file.
        timestamp (bool): Choose True to add the date and time to the file name. This way, your file has a unique name. Choose False to omit the timestamp.
        extension (str): File extension.
        append (bool): Choose True to reopen an existing data log file and append data to it. Choose False to clear existing data. If the file does not exist yet, an empty file will be created either way.
    """

    def __init__(self, *headers: str, name: str = 'log', timestamp: bool = True, extension: str = 'csv', append: bool = False):
        ...

    def log(self, *values):
        """
        Saves one or more values on a new line in the file.

        Args:
            values (object): One or more objects or values.
        """
        ...
