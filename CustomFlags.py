from GameLogic import Flag

class Immediately_Playable(Flag):
    def __init__(self, data = None):
        super().__init__("IP", data)

class Chop(Flag):
    def __init__(self, data = None):
        super().__init__("CH", data)

class Chop_Moved(Flag):
    def __init__(self, data = None):
        super().__init__("CM", data)
