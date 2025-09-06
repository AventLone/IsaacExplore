import yaml
from isaacsim import SimulationApp

def loadConfig(yaml_file_path: str):
    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def openSimuApp(config_file_path: str):
    simulate_config = loadConfig(config_file_path)["simulation_app"]
    simulation_app = SimulationApp(simulate_config["config"])
    from isaacsim.core.utils.stage import open_stage
    open_stage(simulate_config["stage_file_path"])
    simulation_app.update()

    return simulation_app
