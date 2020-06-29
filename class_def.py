import pickle

with open('./data/state_num.pkl', 'rb') as f:
    state_num = pickle.load(f)

all_states = []

class Transition:
    def __init__(self, prev_state_id, label, next_state_id, category='', sub_category=''):
        self.prev_state_id = prev_state_id
        self.label = label
        self.next_state_id = next_state_id
        self.transition_probability = 0
        self.category = category
        self.sub_category = sub_category

class State:
    def __init__(self, out_tr, state_type, prompt, category, sub_category, id=None):
        with open('state_num.pkl', 'rb') as f:
            state_num = pickle.load(f)
        if id == None:
            self.id = state_num
        else:
            self.id = id
        state_num += 1
        with open('state_num.pkl', 'wb') as f:
            pickle.dump(state_num, f)
        self.out_tr = out_tr                # list of Transition class objects
        self.state_type = state_type        # normal, expand, word
        self.prompt = prompt
        self.category = category
        self.sub_category = sub_category
    
    def add_transition(self,out_tr):
        for transition in self.out_tr:
            if transition.prev_state_id == out_tr.prev_state_id and transition.label == out_tr.label and transition.next_state_id == out_tr.next_state_id:
                return
        self.out_tr.append(out_tr)
    
    def clear_transitions_to_state_id(self,next_state_id):
        new_out_tr = []
        for transition in self.out_tr:
            if transition.next_state_id != next_state_id:
                new_out_tr.append(transition)
        self.out_tr = new_out_tr


def find_state(state_type,prompt,category,sub_category):
    for state in all_states:
        if state.state_type == state_type and state.prompt == prompt and state.category == category and state.sub_category == sub_category:
            return state.id
    return None
