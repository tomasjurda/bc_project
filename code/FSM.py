class FSM:
    def __init__(self, entity):
        self.entity = entity
        self.current_state = None


    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit(self.entity)
        self.current_state = new_state
        self.current_state.enter(self.entity)


    def update(self):
        if self.current_state:
            self.current_state.handle_input(self.entity)
            self.current_state.execute(self.entity)