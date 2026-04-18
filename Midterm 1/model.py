from mesa import Model
from mesa.space import SingleGrid
from agents import SchellingAgent
from mesa.datacollection import DataCollector

class SchellingModel(Model):
    """
    Modification:
        - Added fixed model settings that determine how tolerance is updated 
        (Tolerance is bounded between 0.2 and 0.8 and changes by 0.05 after two consecutive rounds of satisfaction or dissatisfaction)
        - Agents are initialized with tolerance values specified by user (default [0.2, 0.8])
        - The model tracks mean required similarity (average tolerence) over time
        - Added a maximum step limit (200) to stop the model from running indefinitely
    """

    ## Define initiation, requiring all needed parameter inputs
    def __init__(self, width = 30, height = 30, density = 0.7, group_one_share = 0.7, radius = 1, seed = None,  max_steps = 200,  initial_tolerance_min = 0.2, initial_tolerance_max = 0.8):
        ## Inherit seed trait from parent class and ensure seed is integer
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)
        ## Define parameter values for model instance
        self.width = width
        self.height = height
        self.density = density
        self.group_one_share = group_one_share
        self.radius = radius
        ## Create grid
        self.grid = SingleGrid(width, height, torus = True)
        ## Instantiate global happiness tracker
        self.happy = 0

        # Modification: add fixed adaptive tolerance parameters and max steps for the model
        self.tolerance_min = 0.2
        self.tolerance_max = 0.8
        self.initial_tolerance_min = min(initial_tolerance_min, initial_tolerance_max)
        self.initial_tolerance_max = max(initial_tolerance_min, initial_tolerance_max)
        self.tolerance_step = 0.05
        self.streak_threshold = 2
        self.max_steps = max_steps

        ## Define data collector, to collect happy agents and average tolerance level across all agents at a given step
        self.datacollector = DataCollector(
            model_reporters={
                "happy": "happy",
                "mean_required_similarity": lambda m: sum(a.tolerance for a in m.agents) / len(m.agents) 
                if len(m.agents) > 0 else 0,
            }
        )

        # Modification: random initial tolerance in a user-adjustable range
        # Place agents randomly around the grid
        for cont, pos in self.grid.coord_iter():
            if self.random.random() < self.density:
                agent_type = 1 if self.random.random() < self.group_one_share else 0
                tolerance = self.random.uniform(self.initial_tolerance_min, self.initial_tolerance_max)
                agent = SchellingAgent(self, agent_type, tolerance)
                self.grid.place_agent(agent, pos)

        ## Initialize datacollector
        self.datacollector.collect(self)

    ## Define a step: reset global happiness tracker, agents move in random order, collect data
    def step(self):
        self.happy = 0
        self.agents.shuffle_do("move")
        self.datacollector.collect(self)
        ## Modification: Run model until all agents are happy or the model reaches the max steps
        self.running = (self.happy < len(self.agents)) and (self.steps < self.max_steps)
