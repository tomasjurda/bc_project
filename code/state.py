class State:
    def enter(self, entity):
        """Called when entering the state"""
        pass

    def handle_input(self, entity):
        """Called every frame to handle state changes"""
        pass

    def execute(self, entity):
        """Called every frame while in this state"""
        pass

    def exit(self, entity):
        """Called when exiting the state"""
        pass
