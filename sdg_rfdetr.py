import os, random, asyncio, multiprocessing, time
from tqdm import tqdm

GENERATING_PROGRESS_QUEUE = multiprocessing.Queue()

# --- Display a bar to show the progress of the SDG ---
def display_progress(progress_queue: multiprocessing.Queue):
    """
    Listens to the queue and updates the progress bar UI.
    """   
    total_frames = progress_queue.get()
    # Initialize a tqdm progress bar with a fixed total of 100
    with tqdm(total=total_frames, desc="SDG Progress", unit=" Frames") as pbar:
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

progress_process = multiprocessing.Process(target=display_progress, args=[GENERATING_PROGRESS_QUEUE])
progress_process.start()

from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})

import omni.replicator.core as rep
import carb.settings
from sdg import writers, randomizer, sample
from omni.kit.async_engine import run_coroutine
from datetime import datetime
from isaacsim.core.utils import stage as stage_utils, prims as prims_utils
from sdg import common
from omni import usd


FORK_CAMERA_HEIGHT = 0.75
CAMERA_HEIGHT_TRAIN, CAMERA_HEIGHT_VAL = 0.75, 1.0
CAMERA_RADIUSES_TRAIN = [2.2, 3.2, 4.2]
CAMERA_RADIUSES_VAL = [3.0]
PALLET_WITH_GOODS_COLUMNS = 2


async def prepare_loads_with_goods(prim_paths: list[str], loads_count: int, boxes_urls_and_weights: list):
    pca_list = []
    idx = 0.0
    for prim_path in prim_paths:
        pca = sample.PermuAndCombi([prim_path])
        
        pca.set_pose(translation=(0.0, 999.0 + idx, 0.0), yaw=0.0)
        pca.create_columns(columns=loads_count, direction='x', gap=0.2)
        coroutines = []
        for col in pca.column_prims:
            # num_boxes = random.choice([10, 20, 30, 40, 50, 60])
            num_boxes = random.randint(10, 50)
            coroutines.append(randomizer.stack_boxes_on_pallet_async(pallet_prim=col,
                                                      boxes_urls_and_weights=boxes_urls_and_weights,
                                                      num_boxes=num_boxes, overhang=0.2))
        await asyncio.gather(*coroutines)
        pca_list.append(pca)
        idx += 3.6
    return pca_list

    

class Sampler:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    def __init__(self, prim_paths: list[str], boxes_urls_and_weights: list,
                 img_resolution=(1024, 1024), save_path=None) -> None:
        self._prim_paths = prim_paths
        self._pac = sample.PermuAndCombi(prim_paths)
        self._img_resolution = img_resolution
        # self._randomizer = randomizer.EventRandomizer(self._pac.prim_path)
        # self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)        

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        self._writer = writers.CocoInstanceSegWriter(output_dir=data_save_dir)
        # self._writer.attach(self._render_product)

        cols, rows = 4, 5
        self._counts = cols * rows
        run_coroutine(self._pac.line_up(columns=5, rows=5))

        self._loads_with_goods: asyncio.Future = run_coroutine(
            prepare_loads_with_goods(prim_paths, PALLET_WITH_GOODS_COLUMNS, boxes_urls_and_weights)) # type: ignore

    async def generate(self):
        this_stage = stage_utils.get_current_stage()
        
        # Step 1: Prepare loads with goods
        pca_list: list[sample.PermuAndCombi] = await self._loads_with_goods

        # Step 2: Collect stacking pallets (without goods)
        randomizer_temp = randomizer.EventRandomizer(self._pac.prim_path, CAMERA_HEIGHT_VAL, CAMERA_RADIUSES_VAL)
        render_product = rep.create.render_product(camera=randomizer_temp.camera, resolution=self._img_resolution)
        self._writer.attach(render_product)

        frames_generated_total = randomizer_temp.frames_generated * (self._counts // 5 + 
                                                                     len(self._prim_paths) * PALLET_WITH_GOODS_COLUMNS)
        current_frames_generated = 0
        GENERATING_PROGRESS_QUEUE.put(frames_generated_total)

        for count in range(self._counts):
            await self._pac.run()
            if count % 5 == 0:
                for frame in range(randomizer_temp.frames_generated):
                    await rep.orchestrator.step_async(rt_subframes=10)
                    randomizer_temp.randomize_camera()
                    self._writer.schedule_write()
                    current_frames_generated += 1
                    GENERATING_PROGRESS_QUEUE.put(current_frames_generated)
                    if frame % 3 == 0:
                        randomizer_temp.randomize_material()
                    if frame % 10 == 0:
                        randomizer_temp._randomize_light()
        self._writer.detach()
        render_product.destroy()   # type: ignore
        this_stage.RemovePrim(self._pac.prim_path)

        # Step 3: Collect data of pallets with goods, one by one
        targe_prim_path_parent = "/World/Target"
        prims_utils.create_prim(targe_prim_path_parent)
        target_prim_path = f"{targe_prim_path_parent}/obj"
        for pca in pca_list:
            for col in pca.column_prims:
                usd.duplicate_prim(this_stage, prim_path=str(col.GetPrimPath()), path_to=target_prim_path)
                common.set_local_trasform(target_prim_path, [0.0, 0.0, 0.0])
                randomizer_temp = randomizer.EventRandomizer(target_prim_path, CAMERA_HEIGHT_VAL, CAMERA_RADIUSES_VAL)
                render_product = rep.create.render_product(camera=randomizer_temp.camera, resolution=self._img_resolution)
                self._writer.attach(render_product)

                for frame in range(randomizer_temp.frames_generated):
                    await rep.orchestrator.step_async(rt_subframes=10)
                    randomizer_temp.randomize_camera()
                    self._writer.schedule_write()
                    current_frames_generated += 1
                    GENERATING_PROGRESS_QUEUE.put(current_frames_generated)
                    # if frame % 3 == 0:
                    #     randomizer_temp.randomize_material()
                    if frame % 10 == 0:
                        randomizer_temp._randomize_light()
                self._writer.detach()
                render_product.destroy()   # type: ignore
                this_stage.RemovePrim(target_prim_path)

        await rep.orchestrator.wait_until_complete_async()


created_stage = stage_utils.create_new_stage()
prims_utils.create_prim("/World")

environment_prim_path = "/World/Environment"
stage_utils.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
    prim_path=environment_prim_path
)
common.set_world_trasform(prim=environment_prim_path, translation=[-7.6, 4.85, 0.0], orientation=common.yaw2quat(90.0))

obj_prim_paths = common.load_usds("/home/avent/Desktop/pallets")

boxes_urls_and_weights = [
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxA_01.usd", 0.02),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01.usd", 0.06),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd", 0.12),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd", 0.80),
]

sampler = Sampler(prim_paths=obj_prim_paths, boxes_urls_and_weights=boxes_urls_and_weights,
                  img_resolution=(504, 504), save_path="/home/avent/Desktop/generated_data")

simu_app.run_coroutine(sampler.generate())
simu_app.close()

progress_process.join()
