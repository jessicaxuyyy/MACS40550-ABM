from mesa import Agent

class AxelrodAgent(Agent):

    """
    Each agent occupies one grid site and has a culture vector with n features
    each feature has one trait from 0 to n - 1
    In each event, the active agent chooses one neighbor at random
    The agent calculates cultural similarity with that neighbor; similarity is the share of features with the same trait
    The agent interacts with probability equal to similarity
    If interaction occurs, the active agent copies one differing trait from the neighbor
    And only the active agent changes, and the neighbor does not change
    """

    # Initiate agent and model
    def __init__(self, model, culture):
        super().__init__(model)

        self.culture = culture # culture is a list of integers

    # One Axelrod event for selected active agent
    def interact(self):
        """
        The active agent first gets its possible neighbors, and one neighbor is randomly selected from neighborhood
        The probability of interaction = cultural similarity
        If the two agents share no features, no interaction resulted
        If the two agents are identical, the event occurs but no feature changes
        If interaction occurs, one differing feature is randomly selected, and the active agent changes that feature to match that of the neighbor
        """

        neighbors = self.model.get_neighbors(self.pos) # Get neighbors based on neighborhood rule

        # Stop this event if the agent has no neighbors
        if not neighbors:
            return
        
        neighbor = self.random.choice(neighbors) # Pick one neighbor at random

        # Cultural similarity = proportion of shared features
        shared = sum(a == b for a, b in zip(self.culture, neighbor.culture))
        similarity = shared / self.model.num_feature

        # If similarity = 0, interaction probability = 0; if similarity = 1, the event is allowed but no trait changes 
        # event_count increases by 1 regardless of what interact() returns
        if similarity == 0 or similarity == 1:
            return

        # Interact with probability equal to cultural similarity
        if self.random.random() < similarity:

            # Find features where the active agent and neighbor differ
            differing = [i for i in range(self.model.num_feature) if self.culture[i] != neighbor.culture[i]]

            feature = self.random.choice(differing) # Randomly pick one different feature

            self.culture[feature] = neighbor.culture[feature] # Update the active agent trait to match the neighbor
