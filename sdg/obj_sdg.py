from isaacsim.simulation_app import SimulationApp



class ObjSDG:
    def __init__(self, config: dict) -> None:
        self.simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": config["headless"]})
        self.environment_pool = config["environments"]
        self.obj_pool = config["objs"]

        from .randomizer_rep import Randomizer
        from .generator import Generator
        self.randomizer = Randomizer()





        
