class Memloc():
    def __init__(self, identifier):
        self.identifier = identifier
        self.using = False
        self.used_by = []
        self.future_usedby = []
        self.data_available = True
    def setusing(self, using, by=None):
        self.using = using
        if using is True:
            if by is not None:
                self.used_by = by
        elif using is False:
            self.used_by = None