# from isaacsim.simulation_app import SimulationApp
# simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

# import random, pathlib
# from sdg.sample import PermuAndCombi
# from isaacsim.core.utils import stage, prims
# from sdg.randomizer import stack_boxes_on_pallet_async
# from sdg import common
# from omni.kit.async_engine import run_coroutine

# created_stage = stage.create_new_stage()
# prims.create_prim("/World")

# # environment_prim_path = "/World/Environment"
# # stage.add_reference_to_stage(
# #     usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
# #     prim_path=environment_prim_path
# # )
# # common.set_world_trasform(prim=environment_prim_path, translation=[-6.7, 5.5, 0.0], orientation=common.yaw2quat(180.0))

# def find_usds(dir: str) -> list[str]:
#     folder = pathlib.Path(dir)
#     usd_files = []
#     for usd_file in folder.rglob("*.usd"):
#         usd_files.append(str(usd_file))
#     return usd_files

# def load_usds(dir: str | list[str], objs_prim_path="/World/Objs") -> list[str]:
#     """
#     Load USDs from a folder into the stage
#     """
#     prims.create_prim(objs_prim_path)
#     usd_file_paths = find_usds(dir) if type(dir) is str else dir
#     obj_prim_paths = []
#     idx = 0
#     for file_path in usd_file_paths:
#         idx += 1
#         obj_prim_path = f"{objs_prim_path}/obj{idx}"
#         obj_prim_paths.append(obj_prim_path)
#         stage.add_reference_to_stage(usd_path=file_path, prim_path=obj_prim_path)
#     return obj_prim_paths




# # objs_prim_path = "/World/Obj"
# # stage.add_reference_to_stage(
# #     usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Props/pallet_eu.usd",
# #     # usd_path="/home/avent/Desktop/IsaacAssets/Props/KKP.usd",
# #     prim_path=objs_prim_path
# # )

# obj_prim_paths = load_usds(dir="/home/avent/Desktop/pallets")

# boxes_urls_and_weights = [
#     ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxA_01.usd", 0.02),
#     ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01.usd", 0.06),
#     ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd", 0.12),
#     ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd", 0.80),
# ]
# # simu_app.run_coroutine(pca.run(colomns=6, rows=6))
# # simu_app.run_coroutine(pca.run_stack_boxes(colomns=6, boxes_urls_and_weights=boxes_urls_and_weights))
# pca = PermuAndCombi(obj_prim_paths)
# simu_app.run_coroutine(pca.line_up(columns=6, rows=6, gap=0, direction='x'))

# # for col in pca.colomn_prims:
# #     num_boxes = random.randint(10, 70)
# #     run_coroutine(stack_boxes_on_pallet_async(pallet_prim=col,
# #                                               boxes_urls_and_weights=boxes_urls_and_weights,
# #                                               num_boxes=num_boxes, overhang=0.1))

# # environment_url = "/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd"
# # simu_app.run_coroutine(example())

# while simu_app.is_running():
#     simu_app.update()

# simu_app.close()


import multiprocessing
import time
from tqdm import tqdm

# --- PROCESS 1: THE PRODUCER / WORKER ---
def worker_process(progress_queue: multiprocessing.Queue, finish_event):
    """Simulates a heavy workload, updating the range from 1 to 100."""
    print("Process 1: Starting heavy computations...")
    time.sleep(2.0)
    prgress_total = 60
    progress_queue.put(prgress_total)
    for i in range(1, prgress_total + 1):
        # Simulate an actual calculation or Isaac Sim physics step
        time.sleep(0.05) 
        
        # Send the current progress value to Process 2
        progress_queue.put(i)
        
    # Signal Process 2 that we are completely finished
    finish_event.set()
    # print("Process 1: Done with all tasks.")

# Standard ANSI Escape Codes for text coloring
PINK = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"  # Crucial to prevent leaking color to the rest of the terminal

# --- PROCESS 2: THE CONSUMER / PROGRESS BAR ---
def UI_process(progress_queue: multiprocessing.Queue):
    """
    Listens to the queue and updates the progress bar UI.
    """   
    total_frames = progress_queue.get()
    # Initialize a tqdm progress bar with a fixed total of 100
    desc_text = f"{GREEN}SDG Progress{RESET}"
    with tqdm(total=total_frames, desc=desc_text, unit=" Frames") as pbar:
        curren_frames = 0
        # Loop until Process 1 sets the finish event AND the queue is completely drained
        # while not finish_event.is_set() or not progress_queue.empty():
        while curren_frames < total_frames:
            if not progress_queue.empty():
                new_val = progress_queue.get()
                
                # Calculate how much the counter advanced and update the bar
                step = new_val - curren_frames
                pbar.update(step)
                curren_frames = new_val
            else:
                time.sleep(0.01)   # Prevent CPU pinning (100% core usage) while waiting for the next update


# --- MAIN ORCHESTRATION ---
if __name__ == "__main__":
    # 1. Initialize our communication channels
    progress_queue = multiprocessing.Queue()
    finish_event = multiprocessing.Event()

    # 2. Spawn both processes
    p1 = multiprocessing.Process(target=worker_process, args=(progress_queue, finish_event))
    p2 = multiprocessing.Process(target=UI_process, args=[progress_queue])

    # 3. Start execution
    p2.start()  # Start the UI listener first so it captures the very first update
    p1.start()

    # 4. Wait for both to gracefully exit
    p1.join()
    p2.join()

    # print("Main: System finished execution successfully.")

    # for i in tqdm(range(100)):
    #     time.sleep(0.05)  # Fake work

    # with tqdm(total=100, desc="Generation Progress", unit=" Frames") as pbar:
    #     for i in range(1, 101):
    #         pbar.update(1)
    #         time.sleep(0.05)