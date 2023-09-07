class TooMuchDebt(Exception):
    def __init__(self, message = "The given members debt is already around 500! More debt cannot be allowed, please clear the debth to rent his book."):
        self.message = message
        super().__init__(self.message)

class NoBooksFoundFrappe(Exception):
    def __init__(self, message = "Sorry, but no books were found from that search!"):
        self.message = message
        super().__init__(self.message)
