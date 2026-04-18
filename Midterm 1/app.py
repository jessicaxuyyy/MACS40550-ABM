import solara
from model import SchellingModel
from mesa.visualization import (  
    SolaraViz,
    make_space_component,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

## Define agent portrayal: color, shape, and size
def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color = "blue" if agent.type == 1 else "red",
        marker= "s",
        size= 75,
    )

#  Modification: removed desired_share_alike from the GUI because tolerance is now agent-specific and fixed by the model rules
#  Modification: added initial_tolerance_min and initial_tolerance_max so users can set the initial tolerance range in the UI
## Enumerate variable parameters in model: seed, grid dimensions, population density, agent preferences, vision, and relative size of groups
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": {
        "type": "SliderInt",
        "value": 30,
        "label": "Width",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 30,
        "label": "Height",
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "density": {
        "type": "SliderFloat",
        "value": 0.7,
        "label": "Population Density",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "group_one_share": {
        "type": "SliderFloat",
        "value": 0.7,
        "label": "Share Type 1 Agents",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "radius": {
        "type": "SliderInt",
        "value": 1,
        "label": "Vision Radius",
        "min": 1,
        "max": 5,
        "step": 1,
    },
     "initial_tolerance_min": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Initial Tolerance Min",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
    "initial_tolerance_max": {
        "type": "SliderFloat",
        "value": 0.8,
        "label": "Initial Tolerance Max",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
}

## Instantiate model
schelling_model = SchellingModel()

# Modification: updated the visualization to show both happy agents and average required similarity over time
# higher mean_required_similarity = agents require more same-type neighbors
happy_chart = make_plot_component("happy")
mean_required_similarity_chart = make_plot_component("mean_required_similarity")
space_component = make_space_component(agent_portrayal)

## Instantiate page inclusing all components
page = SolaraViz(
    schelling_model,
    components=[happy_chart, mean_required_similarity_chart, space_component],
    model_params=model_params,
    name="Schelling Segregation Model",
)
## Return page
page
    
