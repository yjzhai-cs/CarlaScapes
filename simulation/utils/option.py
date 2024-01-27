
import argparse

def get_args():
    argparser = argparse.ArgumentParser(
        description='CARLA Data Collector Arguments')

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
        default='Town10HD',
        help='The map to load (default: Town15)')

    args = argparser.parse_args()
    return args