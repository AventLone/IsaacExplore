import omni.replicator.core as rep
import os, carb.settings
from datetime import datetime
from .randomizer_rep import Randomizer

import omni.replicator.core as rep
import os
from omni.replicator.core import CocoWriter

import os
from pathlib import Path
import numpy as np

from omni.replicator.core import AnnotatorRegistry
from pycocotools import mask as mask_utils


class CocoInstanceSegWriter(CocoWriter):
    def __init__(self, output_dir: str, semantic_types: rep.List[str] = None, 
                 coco_categories: dict = None, s3_bucket: str = None, s3_region: str = None, 
                 s3_endpoint: str = None, dataset_id: str = None, frame_padding: int = 4, 
                 image_output_format: str = "png", coco_license_info: rep.List[dict] = None, **kwargs):
        super().__init__(output_dir, semantic_types, coco_categories, s3_bucket, s3_region,
                         s3_endpoint, dataset_id, frame_padding, image_output_format, coco_license_info, **kwargs)
        self.annotators.append(AnnotatorRegistry.get_annotator(
            "instance_segmentation", init_params={"semanticTypes": self.semantic_types}))
        self.label_dict = {
            'unlabelled': {'name': 'unlabelled', 'id': 0, 'supercategory': 'unlabelled', 'color': (0, 0, 0), 'isthing': 0},
            'pallet': {'name': 'pallet', 'id': 1, 'supercategory': 'loads', 'color': (220, 20, 60), 'isthing': 1},
            'goods': {'name': 'goods', 'id': 2, 'supercategory': 'loads', 'color': (119, 11, 32), 'isthing': 1}
        }
        
    def write(self, data: dict):
        """Write function called from the OgnWriter node on every frame to process annotator output.

        Args:
            data: A dictionary containing the annotator data for the current frame.
        """
        # Check for on_time triggers
        # For each on_time trigger, prefix the output frame number with the trigger counts
        sequence_id = ""
        for trigger_name, call_count in data["trigger_outputs"].items():
            if "on_time" in trigger_name:
                sequence_id = f"{call_count}_{sequence_id}_"
        if sequence_id != self._sequence_id:
            self._frame_id = 0
            self._sequence_id = sequence_id

        # Loop through all annotators and render products
        for render_product_name, rp_data_dict in data["renderProducts"].items():

            camera_name = rp_data_dict["camera"][1:].replace("Replicator/", "").replace("/", "-").replace("_", "-")
            rgb_path = self._write_rgb(render_product_name, camera_name, rp_data_dict["rgb"])
            image_id = len(self.coco_annotation_dict["images"])
            image_dict = {
                "file_name": Path(rgb_path).as_posix(),
                "id": image_id,
                "height": int(rp_data_dict["resolution"][1]),
                "width": int(rp_data_dict["resolution"][0]),
                "license": 0,
                "date_captured": self._date.isoformat(),
                "flicker_url": "",
            }
            self.coco_annotation_dict["images"].append(image_dict)
            self._write_instance_annotation_segment(rp_data_dict["instance_segmentation"], image_id)

        self._frame_id += 1
        if self._frame_id % 25 == 0:
            # periodically write the annotation file to avoid data loss
            self._write_coco_annotation_file()

    def _write_instance_annotation_segment(self, annotator_dict, image_id):
        instance_map = annotator_dict["data"]
        id_to_semantics = annotator_dict["idToSemantics"]

        image_annotations = []

        for instance_id in np.unique(instance_map):
            instance_id = int(instance_id)
            if instance_id == 0:
                continue

            mask = (instance_map == instance_id).astype(np.uint8)
            area = int(mask.sum())
            if area == 0:
                continue

            ys, xs = np.where(mask > 0)
            x_min = int(xs.min())
            x_max = int(xs.max())
            y_min = int(ys.min())
            y_max = int(ys.max())

            bbox = [x_min, y_min, x_max - x_min + 1, y_max - y_min + 1]

            semantic_dict = id_to_semantics.get(str(instance_id), {})
            category_id = None
            for label in semantic_dict.values():
                if label in self.label_dict:
                    category_id = self.label_dict[label]["id"]
                    self._used_categories.setdefault(label, self.label_dict[label])

            if category_id is None:
                continue
            #     category_id = self.label_dict["unlabelled"]["id"]
            #     self._used_categories.setdefault("unlabelled", self.label_dict["unlabelled"])

            rle = mask_utils.encode(np.asfortranarray(mask))
            rle["counts"] = rle["counts"].decode("utf-8")

            annotation_entry = {
                "id": self._num_annotations,
                "image_id": image_id,
                "bbox": bbox,
                "area": float(area),
                "bbox_mode": 1,
                "category_id": int(category_id),
                "iscrowd": 0,
                "segmentation": rle,
            }

            image_annotations.append(annotation_entry)
            self._num_annotations += 1

        self.coco_annotation_dict["annotations"] += image_annotations


class Generator:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    # carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)   # DLAA

    def __init__(self, randomizer: Randomizer, annotation_typ: dict, img_resolution=(1024, 1024), save_path=None) -> None:
        self._randomizer = randomizer
        self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)        

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        self._writer = CocoInstanceSegWriter(output_dir=data_save_dir)
        # self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        # self._writer.initialize(output_dir=data_save_dir, rgb=True, **annotation_typ)
        # self._writer.initialize(output_dir=data_save_dir,
        #                         rgb=True,
        #                         bounding_box_2d_tight=True,
        #                         instance_segmentation=True, 
        #                         semantic_segmentation=True)
        self._writer.attach(self._render_product, trigger=self._randomizer.camera_trigger)

    def generate(self):
        self._randomizer.trigger_obj_pose()
        self._randomizer.trigger_obj_apperance()
        self._randomizer.trigger_camera()
        self._randomizer.trigger_light()

        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()

        self._writer.detach()
        self._render_product.destroy()    # type: ignore


