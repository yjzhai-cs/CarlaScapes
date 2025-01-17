
import copy
import carla
import logging
from numpy import random
import time
import sys
import glob
import os

from simulation.utils.option import get_args
from simulation.world import World
from simulation.sensors import RGBCamera, GNSS, InstanceCamera, SemanticCamera, RGBBboxsCamera
from simulation.config import (WorldConfig, RGBCameraConfig, GNSSConfig, InstanceCameraConfig,
                               SemanticCameraConfig, RecorderConfig, GeneratorConfig)
from simulation.recorders import BufferRecorder
from simulation.generator import TrafficGenerator

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


def main():

    world = None
    carla_world = None
    recorder = None
    generator = None

    try:
        args = get_args()

        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        random.seed(args.seed if args.seed is not None else int(time.time()))

        # First of all, we need to create the client that will send the requests to the simulator.
        client = carla.Client(args.host, args.port)
        client.set_timeout(50.0)
        client.load_world(args.map)
        carla_world = client.get_world()
        traffic_manager = client.get_trafficmanager(args.tm_port)

        # Second, we need to create a "World" that can hold all actors including sensors and ego vehicle.
        world = World(carla_world=carla_world, traffic_manager=traffic_manager, config=WorldConfig, spawn_point=None)
        world.set_ego_autopilot(True)

        # #738  https://github.com/carla-simulator/carla/issues/738
        # 'It looks like that the bounding box is always extended to the direction where the pedestrian is moving'
        # So, We need to wait for a tick to ensure client receives the last transform of the ego vehicle we have just created
        carla_world.tick()

        generator = TrafficGenerator(generator_config=GeneratorConfig, client=client)
        generator.generate()



        world.add_carla_sensor(RGBBboxsCamera(name='rgb_camera', rgb_cam_config=RGBCameraConfig, parent_actor=world.ego_veh, world=carla_world))
        world.add_carla_sensor(GNSS(name='gnss', gnss_config=GNSSConfig, parent_actor=world.ego_veh))
        world.add_carla_sensor(InstanceCamera(name='instance_camera', in_cam_config=InstanceCameraConfig, parent_actor=world.ego_veh))
        world.add_carla_sensor(SemanticCamera(name='semantic_camera', ss_cam_config=SemanticCameraConfig, parent_actor=world.ego_veh))

        # Third, we need to create a recorder to record the data from sensors to disk.
        recorder = BufferRecorder(recorder_config=RecorderConfig, map_name=args.map)

        # Fourth, we need to start the world tick.
        while True:
            world.step_forward()

            if world.all_sensor_data['rgb_camera']['frame'] % 100 == 0:
                print(f"Frame: {world.all_sensor_data['rgb_camera']['frame']}")

                # get the bounding box of RGB camera Image
                world.carla_sensors['rgb_camera'].bounding()

                # To avoid overlapping, we need to copy the data from all_sensor_data to recorder instead of `recorder.buffering(world.all_sensor_data)`
                recorder.buffering(copy.deepcopy(world.all_sensor_data))

            world.see_ego_veh()

    finally:
        if world is not None:
            world.destroy()
        if generator is not None:
            generator.destroy()

        # for sensor in carla_world.get_actors().filter('*sensor*'):
        #     sensor.destroy()
        #
        # for pedestrian in carla_world.get_actors().filter('*pedestrian*'):
        #     pedestrian.destroy()
        #
        # for vehicle in carla_world.get_actors().filter('*vehicle*'):
        #     vehicle.destroy()

        if recorder is not None:
            recorder.flush()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')