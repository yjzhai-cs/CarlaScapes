import carla
import os
import json
from typing import Dict

from queue import Queue
from queue import Empty

from .config import OUTPUT_PATH
from .env_base import EnvBase


def sensor_callback(save_path, sensor_data, sensor_queue, sensor_name, map_name):
    file_name = '%s_%06d_%06d' % (map_name, sensor_data.timestamp, sensor_data.frame)
    if 'gnss' == sensor_name:
        with open(os.path.join(save_path, f'{file_name}_gnss.json'), 'w', encoding='utf-8') as file:
            data = {
                'latitude': sensor_data.latitude,
                'longitude': sensor_data.longitude,
                'altitude': sensor_data.altitude,
            }
            json.dump(data, file)
    if 'camera' == sensor_name:
        sensor_data.save_to_disk(os.path.join(save_path, f'{file_name}_img.png'))
    if 'semantic_segmentation' == sensor_name:
        sensor_data.save_to_disk(os.path.join(save_path, f'{file_name}_color.png'), carla.ColorConverter.CityScapesPalette)
    if 'instance_segmentation' == sensor_name:
        sensor_data.save_to_disk(os.path.join(save_path, f'{file_name}_instance.png'))

    sensor_queue.put((sensor_data.frame, sensor_name))


class DataCollector(EnvBase):
    def __init__(self, ip: str = "localhost",
                 port: int = 2000,
                 map_name: str = "Town02",
                 is_large_map: bool = False,
                 weather_config: Dict[str, float] = None,
                 is_sync_mode: bool = True,
                 is_spectator: bool = True,
                 img_width: int = 2048,
                 img_height: int = 1024,):

        super().__init__(ip=ip,
                       port=port,
                       map_name=map_name,
                       is_large_map=is_large_map,
                       weather_config=weather_config,
                       is_sync_mode=is_sync_mode)

        self.is_spectator = is_spectator
        self.img_width = img_width
        self.img_height = img_height
        self.save_path = OUTPUT_PATH / f'{map_name}'

        if os.path.isdir(self.save_path) is False:
            os.makedirs(self.save_path)

        # create sensor queue
        self.sensor_queue = Queue()

        try:
            self.build_env()
            self.build_sensor()
            self.collect()
        finally:
            self.destroy()
            print(' - Exited.')

    def build_rgb_sensor(self):
        """Build the rgb camera for the ego vehicle."""

        rgb_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        rgb_camera_bp.set_attribute('image_size_x', f'{self.img_width}')
        rgb_camera_bp.set_attribute('image_size_y', f'{self.img_height}')
        rgb_camera_bp.set_attribute('fov', '70')

        # camera relative position related to the vehicle
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = self.world.spawn_actor(rgb_camera_bp, camera_transform, attach_to=self.ego_vehicle)
        # set the callback function
        camera.listen(lambda image: sensor_callback(self.save_path, image, self.sensor_queue, "camera", self.map_name))
        self.sensor_list.append(camera)

    def build_gnss_sensor(self):
        """Build the gnss sensor for the ego vehicle."""
        gnss_bp = self.blueprint_library.find('sensor.other.gnss')
        gnss_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        gnss = self.world.spawn_actor(gnss_bp, gnss_transform, attach_to=self.ego_vehicle)
        gnss.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "gnss", self.map_name))
        self.sensor_list.append(gnss)

    def build_sem_seg_sensor(self):
        """Build the semantic segmentation camera for the ego vehicle."""
        sem_seg_bp = self.blueprint_library.find('sensor.camera.semantic_segmentation')
        sem_seg_bp.set_attribute('image_size_x', f'{self.img_width}')
        sem_seg_bp.set_attribute('image_size_y', f'{self.img_height}')
        sem_seg_bp.set_attribute('fov', '70')

        sem_seg_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        sem_seg_camera = self.world.spawn_actor(sem_seg_bp, sem_seg_transform, attach_to=self.ego_vehicle)
        sem_seg_camera.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "semantic_segmentation", self.map_name))
        self.sensor_list.append(sem_seg_camera)

    def build_ins_seg_sensor(self):
        """Build the instance segmentation camera for the ego vehicle."""
        ins_seg_bp = self.blueprint_library.find('sensor.camera.instance_segmentation')
        ins_seg_bp.set_attribute('image_size_x', f'{self.img_width}')
        ins_seg_bp.set_attribute('image_size_y', f'{self.img_height}')
        ins_seg_bp.set_attribute('fov', '70')

        ins_seg_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        ins_seg_camera = self.world.spawn_actor(ins_seg_bp, ins_seg_transform, attach_to=self.ego_vehicle)
        ins_seg_camera.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "instance_segmentation", self.map_name))
        self.sensor_list.append(ins_seg_camera)

    def build_sensor(self):
        self.build_rgb_sensor()
        self.build_gnss_sensor()
        self.build_sem_seg_sensor()
        self.build_ins_seg_sensor()

    def collect(self):
        while True:
            if self.is_sync_mode:
                self.world.tick()

            if self.is_spectator:
                # set the sectator to follow the ego vehicle
                spectator = self.world.get_spectator()
                transform = self.ego_vehicle.get_transform()
                spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
                                                        carla.Rotation(pitch=-90)))

            # As the queue is blocking, we will wait in the queue.get() methods
            # until all the information is processed and we continue with the next frame.
            try:
                for i in range(0, len(self.sensor_list)):
                    s_frame = self.sensor_queue.get(True, 1.0)
                    print("    Frame: %d   Sensor: %s" % (s_frame[0], s_frame[1]))

            except Empty:
                print("   Some of the sensor information is missed")