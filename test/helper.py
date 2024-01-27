
import carla
import os
import json
from path import Path

PROJECT_DIR = Path(__file__).parent.parent.abspath()
dir = PROJECT_DIR / "outputs" / "Town10HD"

def main():
    print(dir)

    # First of all, we need to create the client that will send the requests to the simulator.
    client = carla.Client('localhost', 2000)
    client.set_timeout(50.0)
    client.load_world('Town10HD')
    carla_world = client.get_world()

    for root, _, files in os.walk(dir):
        print(files)
        for file in files:
            # check whether the file is a JSON file
            if file.endswith('.json'):
                # construct the file path
                file_path = os.path.join(root, file)

                print(file_path)

                # open and read the file
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)

                    carla_world.debug.draw_point(location=carla.Location(data['x'], data['y'], data['z']),
                                                 size=0.1,
                                                 color=carla.Color(255, 0, 0),
                                                 life_time=-1.0,
                                                 persistent_lines=True)

    while True:
        carla_world.wait_for_tick()
        # print('tick')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('Done with the script')