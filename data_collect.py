from utils import *
simulate_app = openSimuApp("./configs/config_1.yaml")

from modules import ObjBasedDateGenerator

data_collect_config = loadConfig("./configs/config_1.yaml")["obj_data_collect"]

generator = ObjBasedDateGenerator(data_collect_config)
generator.generate()

while simulate_app.is_running() and not generator.is_finished:
    simulate_app.update()

simulate_app.close()