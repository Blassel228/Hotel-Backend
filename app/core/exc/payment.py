class InsufficientFundsException(Exception):
    def __init__(self, detail: str = "Insufficient funds for this payment", balance: float = None):
        super().__init__(detail)
        self.balance = balance

class PaymentProviderException(Exception):
    def __init__(self, detail: str = "Payment provider error occurred", code: int = None):
        super().__init__(detail)
        self.code = code

class PaymentVerificationFailed(Exception):
    def __init__(self, detail: str = "Payment was not verified", code: int = 402):
        super().__init__(detail)
        self.code = code
