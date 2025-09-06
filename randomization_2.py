from utils import *
import time
start = time.time()

app = openSimuApp("configs/config_1.yaml")

import omni.replicator.core as rep
import asyncio
import omni
import os

class DateGenerator:
    def __init__(self, frames_required: int) -> None:
        self._current_frame = 0
        self._frames_required = frames_required
        rep.orchestrator.set_capture_on_play(False)

        camera_prim_path = "/World/camera_data"
        # self._camera = rep.get.prim_at_path(camera_prim_path)
        self._camera = rep.create.camera()
        if not self._camera:
            raise RuntimeError(f"Camera not found: {camera_prim_path}")

        # self.render_product = rep.create.render_product(camera="/World/camera_data/SG3S_ISX031C_GMSL2F_H190XA_01",
        #                                                 resolution=(1024, 1024))
        # self._render_product = rep.create.render_product(camera="/OmniverseKit_Persp", resolution=(1024, 1024))
        self._render_product = rep.create.render_product(camera=self._camera, resolution=(1024, 1024))

        self._writer = rep.writers.get("BasicWriter")
        data_save_dir = os.path.join(os.getcwd(), "data/semantic_segmentation")
        self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.attach(self._render_product)

        self.finished = False

    def __randomizeCameraPose(self):
        with self._camera:
            rep.modify.pose(
                position=rep.distribution.uniform((-5, 5, 1), (-1, 15, 3)),
                look_at="/World/Cages/CageA_1"
            )

    # def run(self):
    #     # 关键：不要 asyncio.run()；用 create_task/ensure_future 把协程挂到 Kit 的事件循环
    #     asyncio.get_event_loop().create_task(self.generate())

    def generate(self):
        for _ in range(self._frames_required):
            self.__randomizeCameraPose()
            # omni.kit.app.get_app().next_update()
            rep.orchestrator.step()

        self._writer.detach()
        self._render_product.destroy()

        rep.orchestrator.wait_until_complete()

        self.finished = True


generator = DateGenerator(2**10)
generator.generate()

# Let the simulation run until it is manually closed
while app.is_running() and not generator.finished:
    app.update()

end = time.time()
print(f"Time elapse: {end - start}")

app.close()


