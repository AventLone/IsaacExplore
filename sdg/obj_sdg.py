from isaacsim.simulation_app import SimulationApp
from isaacsim.core.utils.stage import open_stage
from .randomizer_rep import Randomizer
from .generator import Generator

class ObjSDG:
    def __init__(self, config: dict) -> None:
        # self.simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": config["headless"]})
        self.environment_pool: list[str] = config["environments"]
        self.obj_pool: list[str] = config["objs"]


    def run(self):

        for environment in self.environment_pool:
            open_stage(environment)
            for obj_path in self.obj_pool:
                randomizer = Randomizer(obj_path, 100)
                generator = Generator(randomizer)
                generator.generate()

if __name__ == "__main__":

            







        
