from mesa import Agent

class SchellingAgent(Agent):

    """
    Modification:
        - Each agent starts with its own randomly assigned tolerance
        - Tolerance updates over time based on repeated satisfaction or dissatisfaction
    """

    ## Initiate agent instance, inherit model trait from parent class
    def __init__(self, model, agent_type, tolerance):
        super().__init__(model)
        ## Set agent type
        self.type = agent_type

        # Modification: each agent has its own tolerance and adaptation record/history

        # Agent-specific tolerance threshold; the agent is satisfied when share_alike >= self.tolerance
        self.tolerance = tolerance

        # Track consecutive rounds of satisfaction and dissatisfaction
        self.satisfied_streak = 0
        self.dissatisfied_streak = 0
        
    ## Define decision rule
    def move(self):
        ## Get list of neighbors within range of sight
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore = True, radius = self.model.radius, include_center = False)
        
        ## Count neighbors of same type as self
        similar_neighbors = len([n for n in neighbors if n.type == self.type])
        share_alike = similar_neighbors / len(neighbors) if len(neighbors) > 0 else 0

        # Modification: compare to the agent's own tolerance
        if share_alike < self.tolerance:
            self.dissatisfied_streak += 1
            self.satisfied_streak = 0
            self.model.grid.move_to_empty(self)

            # Modification: after 2 consecutive dissatisfied rounds, increase tolerance by 0.05, bounded above by 0.8
            if self.dissatisfied_streak >= self.model.streak_threshold:
                self.tolerance = min(
                    self.model.tolerance_max,
                    self.tolerance + self.model.tolerance_step,
                )
                self.dissatisfied_streak = 0
        else:
            self.model.happy += 1 #  Otherwise add one to model count of happy agents.
            self.satisfied_streak += 1
            self.dissatisfied_streak = 0

            # Modification: after 2 consecutive satisfied rounds, decrease tolerance by 0.05, bounded below by 0.2
            if self.satisfied_streak >= self.model.streak_threshold:
                self.tolerance = max(
                    self.model.tolerance_min,
                    self.tolerance - self.model.tolerance_step,
                )
                self.satisfied_streak = 0
