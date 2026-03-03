class State:
    def enter(self, entity):
        """Called when entering the state"""

    def handle_input(self, entity):
        """Called every frame to handle state changes"""

    def execute(self, entity):
        """Called every frame while in this state"""

    def exit(self, entity):
        """Called when exiting the state"""
