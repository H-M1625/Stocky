# exceptions.py

class NotEnoughQuantityException(Exception):
    def __init__(self):
        super().__init__("Insufficient quantity in stock. Please adjust your order.")
