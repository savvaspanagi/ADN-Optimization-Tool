def addTime(self, timeframe, time_interval):
    """
    Adds a timeframe and time_interval to the manager object.

    Parameters:
        manager (Manager): The Manager object to update.
        timeframe (str): The total timeframe (e.g., '24hours').
        time_interval (str): The interval of time (e.g., '30minutes').

    Returns:
        None
    """
    self.timeframe = timeframe
    self.time_interval = time_interval
    self.delta = time_interval/60

