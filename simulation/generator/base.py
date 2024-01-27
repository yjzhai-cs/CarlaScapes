

import carla

class Generator(object):
    def __init__(self, generator_config: dict, client: carla.Client):
        """
        Constructor method.

        Input:
            generator_config: Dict of generator configuration.
            map_name: Str of map name.
        """
        self.generator_config = generator_config
        self.client = client

    def generate(self):
        """
        Generate data.

        Input:
            data: Dict of data to be generated.
        """
        raise NotImplementedError()

