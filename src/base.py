import carla

class Base(object):
    def __init__(self, client: carla.Client):

        self.client = client

        self.world = self.client.get_world()

        self.blueprint_library = self.world.get_blueprint_library()


    def destroy(self):
        """Destroy the actors."""
        pass

