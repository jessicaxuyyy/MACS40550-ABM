import colorsys
import solara
from model import AxelrodModel
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle


# Create agent portrayal based on the culture vector
def agent_portrayal(agent):
    """
    Color of each agent = its culture vector; Agents with the same full culture receive the same color
    Note: The color is only a visual represetnation for the full culture vector but does not represent one specific feature or one specific trait
    """

    hue = (hash(tuple(agent.culture)) % 1000) / 1000 # Convert the full culture vector into a tuple

    r, g, b = colorsys.hls_to_rgb(hue, 0.5, 0.8)  # Convert hue into RGB color

    # Format RGB values as a hex color
    color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    # Draw each agent as a square on the grid
    return AgentPortrayalStyle(color=color, marker="s", size=75)


# Define variable model parameters shown in the GUI
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "grid_size": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid Side Length",
        "min": 5,
        "max": 50,
        "step": 1,
    },
    "num_feature": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of Features",
        "min": 1,
        "max": 20,
        "step": 1,
    },
    "num_trait": {
        "type": "SliderInt",
        "value": 10,
        "label": "Traits per Feature",
        "min": 1,
        "max": 50,
    },
    "neighborhood_type": {
        "type": "SliderInt",
        "value": 4,
        "label": "Neighborhood Type",
        "min": 4,
        "max": 12,
        "step": 4,
    },
    "max_steps": {
        "type": "SliderInt",
        "value": 500,
        "label": "Maximum Step",
        "min": 500,
        "max": 5000,
        "step": 100,
    },
}

# Define text information shown in the GUI
def model_information(model):
    return solara.Markdown(
        f"""
        **Step:** {model.current_step}  
        **Events:** {model.event_count}  
        **Maximum Step:** {model.max_steps}
        """
    )

model = AxelrodModel()

# Define model space component
space_component = make_space_component(agent_portrayal)

# Define plot for number of cultural regions over time
regions_chart = make_plot_component("num_regions")

# Define plot for number of unique culture over time
unique_cultures_chart = make_plot_component("num_unique_culture")

# Define plot for mean cultural similarity between neighbors over time
mean_similarity_chart = make_plot_component("mean_similarity")

# Define other aspects of Solara
page = SolaraViz(
    model,
    components=[space_component, regions_chart, unique_cultures_chart, mean_similarity_chart, model_information,],
    model_params=model_params,
    name="Axelrod Cultural Dissemination Model",
)

# Return page
page
