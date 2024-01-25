import carla
import os
import json
from typing import Dict

from queue import Queue
from queue import Empty

from .config import OUTPUT_PATH
from .base import Base
from .bounding import Bounding

def sensor_callback(save_path, sensor_data, sensor_queue, sensor_name, map_name):
    file_name = '%s_%06d_%06d' % (map_name, sensor_data.timestamp, sensor_data.frame)

    if sensor_data.frame % 100 == 0:
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

    sensor_queue.put((sensor_data.timestamp, sensor_data.frame, sensor_name))


class DataCollector(Base):
    def __init__(self,
                 client: carla.Client,
                 map:str = 'Town01',
                 is_spectator: bool = True,
                 img_width: int = 2048,
                 img_height: int = 1024,
                 sensor_trick: float = 1.5,
                 ):

        super().__init__(client=client)

        self.map_name = map
        self.is_spectator = is_spectator
        self.img_width = img_width
        self.img_height = img_height
        self.sensor_trick = sensor_trick

        self.save_path = OUTPUT_PATH / f'{map}'
        if os.path.isdir(self.save_path) is False:
            os.makedirs(self.save_path)

        # create sensor queue
        self.sensor_queue = Queue()
        self.sensor_list = []

        self.actor_list = self.world.get_actors()

        self.ego_vehicle = None
        for actor in self.actor_list:
            if 'role_name' in actor.attributes and actor.attributes['role_name'] == 'hero':
                self.ego_vehicle = actor
                break

        self.build_sensor()

        self.bounding_tool = Bounding(camera=self.camera, camera_bp=self.rgb_camera_bp, world=self.world, ego_vehicle=self.ego_vehicle)

    def build_rgb_sensor(self):
        """Build the rgb camera for the ego vehicle."""

        self.rgb_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        self.rgb_camera_bp.set_attribute('image_size_x', f'{self.img_width}')
        self.rgb_camera_bp.set_attribute('image_size_y', f'{self.img_height}')
        self.rgb_camera_bp.set_attribute('fov', '70')
        # self.rgb_camera_bp.set_attribute('sensor_tick', f'{self.sensor_trick}')

        # camera relative position related to the vehicle
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(self.rgb_camera_bp, camera_transform, attach_to=self.ego_vehicle)
        # set the callback function
        self.camera.listen(lambda image: sensor_callback(self.save_path, image, self.sensor_queue, "camera", self.map_name))
        self.sensor_list.append(self.camera)

    def build_gnss_sensor(self):
        """Build the gnss sensor for the ego vehicle."""
        gnss_bp = self.blueprint_library.find('sensor.other.gnss')
        # gnss_bp.set_attribute('sensor_tick', f'{self.sensor_trick}')

        gnss_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.gnss = self.world.spawn_actor(gnss_bp, gnss_transform, attach_to=self.ego_vehicle)
        self.gnss.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "gnss", self.map_name))
        self.sensor_list.append(self.gnss)

    def build_sem_seg_sensor(self):
        """Build the semantic segmentation camera for the ego vehicle."""
        sem_seg_bp = self.blueprint_library.find('sensor.camera.semantic_segmentation')
        sem_seg_bp.set_attribute('image_size_x', f'{self.img_width}')
        sem_seg_bp.set_attribute('image_size_y', f'{self.img_height}')
        sem_seg_bp.set_attribute('fov', '70')
        # sem_seg_bp.set_attribute('sensor_tick', f'{self.sensor_trick}')

        sem_seg_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.sem_seg_camera = self.world.spawn_actor(sem_seg_bp, sem_seg_transform, attach_to=self.ego_vehicle)
        self.sem_seg_camera.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "semantic_segmentation", self.map_name))
        self.sensor_list.append(self.sem_seg_camera)

    def build_ins_seg_sensor(self):
        """Build the instance segmentation camera for the ego vehicle."""
        ins_seg_bp = self.blueprint_library.find('sensor.camera.instance_segmentation')
        ins_seg_bp.set_attribute('image_size_x', f'{self.img_width}')
        ins_seg_bp.set_attribute('image_size_y', f'{self.img_height}')
        ins_seg_bp.set_attribute('fov', '70')
        # ins_seg_bp.set_attribute('sensor_tick', f'{self.sensor_trick}')

        ins_seg_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.ins_seg_camera = self.world.spawn_actor(ins_seg_bp, ins_seg_transform, attach_to=self.ego_vehicle)
        self.ins_seg_camera.listen(lambda data: sensor_callback(self.save_path, data, self.sensor_queue, "instance_segmentation", self.map_name))
        self.sensor_list.append(self.ins_seg_camera)

    def build_sensor(self):
        self.build_rgb_sensor()
        self.build_gnss_sensor()
        self.build_sem_seg_sensor()
        self.build_ins_seg_sensor()

    def destroy(self):
        """Destroy the actors and sensors. Recovers the settings."""
        print(f'destroying {len(self.sensor_list)} sensors.')

        for sensor in self.world.get_actors().filter('*sensor*'):
            sensor.destroy()

    def collect(self):
        """Collect the data from the sensors."""
        if self.is_spectator:
            # set the sectator to follow the ego vehicle
            self.world.get_spectator().set_transform(self.sensor_list[0].get_transform())

        # As the queue is blocking, we will wait in the queue.get() methods
        # until all the information is processed and we continue with the next frame.
        try:
            for i in range(0, len(self.sensor_list)):
                timestamp, frame, sensor_name = self.sensor_queue.get(True, 1.0)
                print("    Frame: %d   Sensor: %s" % (frame, sensor_name))

                if sensor_name == 'camera' and frame % 100 == 0:
                    self.bounding_tool.bounding(os.path.join(self.save_path, '%s_%06d_%06d' % (self.map_name, timestamp, frame)))

        except Empty:
            pass
            # print("   Some of the sensor information is missed")