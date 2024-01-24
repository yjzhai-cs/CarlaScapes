
import carla
import logging
from numpy import random
import time
import sys
import glob
import os

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

from src.option import get_args
from src.collector import DataCollector
from src.generator import TrafficGenerator

def main():

    datacollector: DataCollector = None
    generator: TrafficGenerator = None
    try:
        args = get_args()

        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        random.seed(args.seed if args.seed is not None else int(time.time()))

        client = carla.Client(args.host, args.port)
        client.set_timeout(20.0)
        client.load_world(args.map)
        world = client.get_world()

        generator = TrafficGenerator(client, args)
        generator.generate()

        if args.asynch or not generator.synchronous_master:
            world.wait_for_tick()
        else:
            world.tick()

        datacollector = DataCollector(
            client=client,
            map=args.map,
            is_spectator=args.spectator,
            img_width=args.width,
            img_height=args.height
        )

        while True:
            if not args.asynch and generator.synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

            datacollector.collect()

    finally:
        datacollector.destroy()
        generator.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
