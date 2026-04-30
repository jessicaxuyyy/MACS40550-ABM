from mesa import Model
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from agents import AxelrodAgent


# Define neighborhood boundry 4, 8, 12 neighboors
neightbor_boundry = {
    4: [(0, 1), (1, 0), (0, -1), (-1, 0),],
    8: [(0, 1), (1, 0), (0, -1), (-1, 0),(1, 1), (1, -1), (-1, 1), (-1, -1), ],
    12: [(0, 1), (1, 0), (0, -1), (-1, 0),(1, 1), (1, -1), (-1, 1), (-1, -1),(0, 2), (2, 0), (0, -2), (-2, 0),],
}


# Helper function to calculate cultural similarity between two agents (proportion of shared cultural features)
#  0 means the two agents share no traits; 1 means the two agents have identical cultures
def cultural_similarity(agent_a, agent_b, num_feature):
    
    shared = sum(a == b for a, b in zip(agent_a.culture, agent_b.culture)) # Count features with the same trait value

    return shared / num_feature


# Helper function to collect each neighboring pair once, used for mean similarity and stopping rules
# checks every agent and its neighbors to avoid counting the same neighboring relationship twice
def get_neighbor_pairs(model):

    seen = set() # Store counted pairs
    pairs = [] # Store unique neighboring pairs

    for agent in model.agents:
        for neighbor in model.get_neighbors(agent.pos):

            pair = tuple(sorted([agent.pos, neighbor.pos]))

            if pair not in seen: # Add the pair only once
                seen.add(pair)
                pairs.append((agent, neighbor))

    return pairs # Return unique neighbor pairs


# Helper function to count cultural regions
# A region is defined by connected set of neighboring sites with identical culture
def count_regions(model):

    visited = set()     # Store positions that have already been assigned to a region
    regions = 0 # total cultural regions

    for agent in model.agents:
        if agent.pos in visited:
            continue

        regions += 1

        queue = [agent] # Use queue to keep track of same-culture neighbors that still needed to be checked

        # Expand the region through same-culture neighbors
        while queue:
            current = queue.pop()
            if current.pos in visited:
                continue

            visited.add(current.pos)

            for neighbor in model.get_neighbors(current.pos): # Add neighboring agents with same culture
                if neighbor.pos not in visited and neighbor.culture == current.culture:
                    queue.append(neighbor)

    return regions  # the number of connected same culture regions


# Helper function to count the number of distinct culture vectors (does not have to be spatially connected)
def count_unique_culture(model):

    unique_culture = set()

    # Add each culture as a tuple because lists cannot be stored in a set
    for agent in model.agents:
        unique_culture.add(tuple(agent.culture))

    # Return the number of unique cultures
    return len(unique_culture)


# Helper function to calculate mean neighbor similarity; average across the grid
# collects every neighboring pair once; cal cultural similarity for each pair; tracks whether neighboring sites become more similar over time
def mean_neighbor_similarity(model):

    pairs = get_neighbor_pairs(model)

    # Return 0 if no neighboring pairs
    if not pairs:
        return 0

    # Calculate sum cultural similarity across all neighboring pairs
    total = sum(
        cultural_similarity(a, b, model.num_feature)
        for a, b in pairs
    )

    return total / len(pairs) # Return average similarity between neighbors


# Helper function to count neighboring pairs that can still produce change
# 0 = cannot interact; 1 = already identical; If no active links remain, no neighboring pair can produce further change
def count_active_links(model):

    active = 0

    # Check all unique neighboring pairs
    for agent, neighbor in get_neighbor_pairs(model):
        similarity = cultural_similarity(agent, neighbor, model.num_feature)

        if 0 < similarity < 1: # Active links (0,1)
            active += 1

    return active

# Axelrod cultural dissemination model
class AxelrodModel(Model):

    """
    The model places one agent at every fixed grid site
    Each agent has a culture vector with F features; each feature has one trait value from 0 to num_traits - 1
    Initial cultures are assigned independently and uniformly at random

    One Mesa step equals to N Axelrod events; N = number of sites in the grid
    In each event, one active site and one neighbor are selected
    The active site interacts with probability equal to cultural similarity
    If interaction occurs, the active site copies one differing trait from the neighbor

    The model stops when no neighboring pair can change or stops if the maximum number of Mesa steps is reached
    """

    # Define initiation
    def __init__(
        self,
        grid_size=10,
        num_feature=5,
        num_trait=10,
        neighborhood_type=4,
        max_steps=500,
        seed=42,
    ):
        # Convert seed from GUI input into an integer
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)

        # Instantiate model parameters
        self.current_step = 0
        self.event_count = 0 # Count total Axelrod events
        self.running = True
        self.grid_size = int(grid_size)
        self.width = self.grid_size
        self.height = self.grid_size
        self.num_feature = int(num_feature)
        self.num_trait = int(num_trait)
        self.max_steps = int(max_steps)
        self.neighborhood_type = int(neighborhood_type)

        # Create a fixed bounded grid with no wraparound
        self.grid = SingleGrid(self.width, self.height, torus=False)

        # Define datacollector for model level outputs
        self.datacollector = DataCollector(
            model_reporters={
                "num_regions": count_regions,
                "num_unique_culture": count_unique_culture,
                "mean_similarity": mean_neighbor_similarity,
                "event_count": lambda m: m.event_count,
            }
        )

        for _, pos in self.grid.coord_iter(): # Place one agent at every grid site

            # Assign each cultural feature independently and uniformly
            culture = [
                self.random.randrange(self.num_trait)
                for _ in range(self.num_feature)
            ]

            # Create one Axelrod agent with this culture
            agent = AxelrodAgent(self, culture)

            # Place the agent at the fixed grid position
            self.grid.place_agent(agent, pos)

        # Initialize datacollector
        self.datacollector.collect(self)

    # Define neighborhood based on the selected 4, 8, or 12-site neighborhood; grid is bounded and not wrap around
    # 4-neighbor: north, east, south, and west; 8-neighbor: 4 + diagonal neighbors; 12-neighbor: 8 + cells two units away in cardinal directions
    def get_neighbors(self, pos):

        boundry = neightbor_boundry[self.neighborhood_type] # Get boundry list

        x, y = pos

        neighbors = [] # to store valid neighbors

        for dx, dy in boundry:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height: # Keep only cells inside the bounded grid
                cell_agents = self.grid.get_cell_list_contents([(nx, ny)])

                if cell_agents:  # Add the agent in that cell if one exists
                    neighbors.append(cell_agents[0])

        # Return all valid neighbors
        return neighbors

    # Define model step; one Mesa step is defined as N Axelrod events; N is the number of sites in the grid
    # Stopping rule: the model stops when stable or when max_steps is reached
    def step(self):

        # Stop immediately if the model has already stopped
        if not self.running:
            return

        # Stop if maximum steps has been reached
        if self.current_step >= self.max_steps:
            self.running = False
            return

        num_sites = self.width * self.height

        # Run N random activation events
        for _ in range(num_sites):
            agent = self.random.choice(list(self.agents))
            agent.interact()
            self.event_count += 1 # Count this Axelrod event

        self.current_step += 1

        self.datacollector.collect(self) # Collect outputs

        stable = count_active_links(self) == 0 # Check whether no neighboring pair can still change

        reached_max_steps = self.current_step >= self.max_steps # Check whether maximum steps has been reached

        self.running = not (stable or reached_max_steps) # Stop model if stable or max steps reached