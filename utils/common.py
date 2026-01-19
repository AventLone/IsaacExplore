import yaml
from isaacsim.simulation_app import SimulationApp

def load_config(yaml_file_path: str):
    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def open_simu_app(config_file_path: str):
    simulate_config = load_config(config_file_path)["simulation_app"]
    simulation_app = SimulationApp(simulate_config["config"])
    from isaacsim.core.utils.stage import open_stage
    open_stage(simulate_config["stage_file_path"])
    simulation_app.update()

    return simulation_app
