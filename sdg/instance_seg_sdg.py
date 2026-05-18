from .logger import logging, logging_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging_handler)

import os, random, asyncio, sys
from tqdm import tqdm
import omni.replicator.core as rep
import carb.settings
from .writers import CocoInstanceSegWriter
from .randomizer.evnet_randomizer import CameraAndLightRandomizer, MaterialRandomizer
from .randomizer import stack_boxes_on_pallet_async
from .sample import PermuAndCombi
from .common import find_usds, load_usds, set_local_trasform

from omni.kit.async_engine import run_coroutine
from datetime import datetime
from isaacsim.core.utils import stage as stage_utils, prims as prims_utils
from omni import usd

async def prepare_loads_with_goods(prim_paths: list[str], loads_count: int, boxes_urls_and_weights: list):
    pca_list = []
    idx = 0.0
   
    with tqdm(total=len(prim_paths) * loads_count, desc="Preparation Progress",
              unit="Pallet", file=sys.stdout) as pbar:
        for prim_path in prim_paths:
            pca = PermuAndCombi([prim_path])
            pca.set_pose(translation=(0.0, 999.0 + idx, 0.0), yaw=0.0)
            pca.create_columns(columns=loads_count, direction='x', gap=0.2)

            for col in pca.column_prims:
                num_boxes = random.randint(10, 50)
                await stack_boxes_on_pallet_async(pallet_prim=col,
                                                  boxes_urls_and_weights=boxes_urls_and_weights,
                                                  num_boxes=num_boxes, overhang=0.2)
                pbar.update(1)

            pca_list.append(pca)
            idx += 3.6
    return pca_list

  
class SDG:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    def __init__(self, obj_urls_dir: str, boxes_urls_and_weights: list,
                 img_resolution: tuple[int, int], stacking_cols: int, stacking_rows: int,
                 camera_height: float, camera_orbit_radiuses: list[float],
                 pallet_with_goods_count: int,
                 save_path=None) -> None:
        self._prim_paths = load_usds(obj_urls_dir)
        self._pac = PermuAndCombi(self._prim_paths)
        self._img_resolution = img_resolution

        # Randomizer
        self._material_randomizer = MaterialRandomizer(self._pac.prim_path)
        self._camera_light_randomizer = CameraAndLightRandomizer(camera_height, camera_orbit_radiuses)

        self._render_product = rep.create.render_product(
            camera=self._camera_light_randomizer.camera, resolution=img_resolution)

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        self._writer = CocoInstanceSegWriter(output_dir=data_save_dir)
        self._writer.attach(self._render_product, trigger=self._camera_light_randomizer.camera_trigger)

        self._pallet_with_goods_count = pallet_with_goods_count

        self._counts = stacking_cols * (stacking_rows - 1)
        run_coroutine(self._pac.line_up(columns=stacking_cols, rows=stacking_rows))

        self._loads_with_goods: asyncio.Future = run_coroutine(
            prepare_loads_with_goods(self._prim_paths, pallet_with_goods_count, boxes_urls_and_weights)) # type: ignore

    async def generate(self, sample_interval: int):
        # Step 1: Prepare loads with goods
        logger.info("Preparing pallets with goods...")
        pca_list: list[PermuAndCombi] = await self._loads_with_goods

        
        this_stage = stage_utils.get_current_stage()

        # Step 2: Collect stacking pallets (without goods)
        frames_generated_total = self._camera_light_randomizer.frames_generated * (self._counts // sample_interval +
                                                                                   len(self._prim_paths) * self._pallet_with_goods_count)
        # frames_generated_total = self._camera_light_randomizer.frames_generated * (self._counts // sample_interval)
        logger.info(f"Preparation done. SDG is starting, {frames_generated_total} images will be generated.")

        with tqdm(total=frames_generated_total, desc="SDG Progress", unit=" Frames", file=sys.stdout) as pbar:
            for count in range(self._counts):
                await self._pac.run()
                if (count + 1) % sample_interval == 0:
                    for frame in range(self._camera_light_randomizer.frames_generated):
                        self._camera_light_randomizer.randomize_camera()
                        pbar.update(1)
                        if frame % 3 == 0:
                            self._material_randomizer.randomize_material()
                        if frame % 10 == 0:
                            self._camera_light_randomizer.randomize_light()

                        await rep.orchestrator.step_async(rt_subframes=8)
            this_stage.RemovePrim(self._pac.prim_path)

            # Step 3: Collect data of pallets with goods, one by one
            targe_prim_path_parent = "/World/Target"
            prims_utils.create_prim(targe_prim_path_parent)
            target_prim_path = f"{targe_prim_path_parent}/obj"
            for pca in pca_list:
                for col in pca.column_prims:
                    usd.duplicate_prim(this_stage, prim_path=str(col.GetPrimPath()), path_to=target_prim_path)
                    set_local_trasform(target_prim_path, [0.0, 0.0, 0.0])

                    for frame in range(self._camera_light_randomizer.frames_generated):
                        self._camera_light_randomizer.randomize_camera()
                        pbar.update(1)
                        # self.current_frames_generated += 1
                        if frame % 10 == 0:
                            self._camera_light_randomizer.randomize_light()
                        await rep.orchestrator.step_async(rt_subframes=8)
                    this_stage.RemovePrim(target_prim_path)

        await rep.orchestrator.wait_until_complete_async()

        self._writer.detach()
        self._render_product.destroy()   # type: ignore
