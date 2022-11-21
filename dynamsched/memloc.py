class Memloc():
    def __init__(self, identifier):
        self.identifier = identifier
        self.using = False
        self.used_by = None
        self.future_usedby = []
    def setusing(self, using, by=None):
        self.using = using
        if using is True:
            if by is not None:
                self.used_by = by
        elif using is False:
            self.used_by = None