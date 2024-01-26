
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
from simulation.sensors import RGBCamera, GNSS, InstanceCamera, SemanticCamera
from simulation.config import WorldConfig, RGBCameraConfig, GNSSConfig, InstanceCameraConfig, SemanticCameraConfig, RecorderConfig
from simulation.recorders import BufferRecorder

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


def main():

    world = None
    recorder = None

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

        world.add_carla_sensor(RGBCamera(name='rgb_camera', rgb_cam_config=RGBCameraConfig, parent_actor=world.ego_veh, world=carla_world))
        world.add_carla_sensor(GNSS(name='gnss', gnss_config=GNSSConfig, parent_actor=world.ego_veh))
        world.add_carla_sensor(InstanceCamera(name='instance_camera', in_cam_config=InstanceCameraConfig, parent_actor=world.ego_veh))
        world.add_carla_sensor(SemanticCamera(name='semantic_camera', ss_cam_config=SemanticCameraConfig, parent_actor=world.ego_veh))

        world.set_ego_autopilot(True)

        # Third, we need to create a recorder to record the data from sensors to disk.
        recorder = BufferRecorder(recorder_config=RecorderConfig, map_name=args.map)

        # Fourth, we need to start the world tick.

        while True:

            world.step_forward()

            world.see_ego_veh()

            if world.all_sensor_data['rgb_camera']['frame'] % 100 == 0:
                print(f"Frame: {world.all_sensor_data['rgb_camera']['frame']}")
                recorder.buffering(copy.deepcopy(world.all_sensor_data))

    finally:
        if world is not None:
            world.destroy()

        if recorder is not None:
            recorder.flush()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')