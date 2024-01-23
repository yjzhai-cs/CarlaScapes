
import argparse

def get_args():
    argparser = argparse.ArgumentParser(
        description='CARLA Data Collector Arguments')
    argparser.add_argument(
        '--ip',
        type=str,
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '--port',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--map',
        type=str,
        default='Town01',
        help='The map to load (default: Town02)')
    argparser.add_argument(
        '--large_map',
        action='store_true',
        help='Whether to load the large map')
    argparser.set_defaults(large_map=False)
    argparser.add_argument(
        '--width',
        type=int,
        default='2048',
        help='image resolution (default: 2048x1024)')
    argparser.add_argument(
        '--height',
        type=int,
        default='1024',
        help='image resolution (default: 2048x1024)')
    argparser.add_argument(
        '--sync',
        action='store_true',
        help='Synchronous mode execution')
    argparser.set_defaults(sync=True)
    argparser.add_argument(
        '--spectator',
        action='store_true',
        help='Whether to use the spectator')
    argparser.set_defaults(spectator=True)
    argparser.add_argument(
        '--weather',
        action='store_true',
        help='The weather preset to use (default: None)')
    argparser.set_defaults(weather=False)

    args = argparser.parse_args()
    return args