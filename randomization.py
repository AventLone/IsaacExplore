from utils import *


import omni.replicator.core as rep
import asyncio
# import omni
import os

class DateGenerator:
    def __init__(self, frames_required: int) -> None:
        self._current_frame = 0
        self._frames_required = frames_required
        rep.orchestrator.set_capture_on_play(False)

        camera_prim_path = "World/Camera"
        self._camera = rep.get.prim_at_path(camera_prim_path)
        if not self._camera:
            raise RuntimeError(f"Camera not found: {camera_prim_path}")

        self.render_product = rep.create.render_product(camera="/World/Camera/SG3S_ISX031C_GMSL2F_H190XA_01", 
                                                        resolution=(1024, 1024))

        self._writer = rep.writers.get("BasicWriter")
        data_save_dir = os.path.join(os.getcwd(), "data/semantic_segmentation")
        self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.attach(self.render_product)

    def __randomizeCameraPose(self):
        with self._camera:
            rep.modify.pose(
                position=rep.distribution.uniform((-5, 5, 1), (-1, 15, 5)),
                look_at="/World/Cages/CageA"
            )

    def run(self):
        asyncio.run(self.tasks())

    async def generate(self):
        for _ in range(self._frames_required):
            # timeline = omni.timeline.get_timeline_interface()

            # if self.control_timeline and not timeline.is_playing():
            #     timeline.play()
            #     timeline.commit()
            # await omni.kit.app.get_app().next_update_async()
            # await rep.orchestrator.step_async()
            self.__randomizeCameraPose()
            await rep.orchestrator.step_async()


    async def tasks(self):
        await asyncio.gather(self.generate())


# import omni.replicator.core as rep

# CAM_PATH = "/World/Camera"

# cam = rep.get.prims(path_pattern=CAM_PATH)
# if not cam:
#     raise RuntimeError(f"Camera not found: {CAM_PATH}")

# # from rep.randomizer import randomizer as rd

# def jitter_cam():
#     with cam:
#         rep.modify.pose(
#             rotation=rep.distribution.uniform((-5, -30, -5), (5, 30, 5)),
#             # rotation=rep.distribution.uniform((-5, -30, -5), (5, 30, 5))
#             lookat="/World/Cages/CageA"
#         )

# # 在每一帧触发（跑 200 帧为例）
# with rep.trigger.on_frame(num_frames=200):
#     jitter_cam()


