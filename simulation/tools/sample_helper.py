import os
import sys
import json
import carla
import argparse

from path import Path
from simulation.tools.base import VisualizationHelper

PROJECT_DIR = Path(__file__).parent.parent.parent.abspath()

class SampleHelper(VisualizationHelper):
    """ Sample helper class for visualizing samples on carla map. """

    def __init__(self, carla_world, dir):
        """ Constructor method. """
        super(SampleHelper, self).__init__()

        self.carla_world = carla_world
        self.dir = dir

    def visualize(self, data: dict = None):

        if os.path.isdir(self.dir) is False:
            print(f"Directory {self.dir} does not exist")
            sys.exit(1)

        for root, _, files in os.walk(self.dir):
            for file in files:
                # check whether the file is a JSON file
                if file.endswith('.json'):
                    # construct the file path
                    file_path = os.path.join(root, file)
                    # open and read the file
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                        # draw the point on carla map by using `carla_world.debug`
                        carla_world.debug.draw_point(location=carla.Location(data['x'], data['y'], data['z']),
                                                     # size=0.1,
                                                     # color=carla.Color(255, 0, 0),
                                                     life_time=100,)
                                                     # persistent_lines=True)

        while True:
            carla_world.wait_for_tick()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='CARLA Sample Helper Arguments')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--map',
        type=str,
        default='Town10HD_Opt',
        help='The map to load (default: Town15)')
    args = argparser.parse_args()

    try:

        client = carla.Client(args.host, args.port)
        client.set_timeout(50.0)

        client.load_world(args.map)
        carla_world = client.get_world()

        # Set spectator position
        transform = carla.Transform()
        spectator = carla_world.get_spectator()
        bv_transform = carla.Transform(transform.location + carla.Location(z=250, x=0),
                                       carla.Rotation(yaw=0, pitch=-90))
        spectator.set_transform(bv_transform)

        helper = SampleHelper(carla_world=carla_world, dir=PROJECT_DIR / "outputs" / args.map.split('_')[0])

        helper.visualize()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
    finally:
        print('\nDone.\n')