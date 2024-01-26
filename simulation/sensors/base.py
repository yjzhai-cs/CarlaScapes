
import queue

class CarlaSensor(object):
    """ Base class for sensor provided by carla. """

    def __init__(self, name, parent_actor=None):
        """
        Constructor method.

        Input:
            name: Str of sensor name.
            parent_actor: Carla.Actor of parent actor that this sensor is attached to.
            parent_world: Carla.World of the world where this sensor is spawned.
        """
        print("Spawning {}".format(name))
        self.name = name
        self._parent = parent_actor
        self.sensor = None
        # Dict to store sensor data
        self.data = {}
        # The callback method in listen() to retrieve data used widely in official tutorials has a data race problem.
        # The callback will likely not finish before data get accessed from the main loop, causing inconsistent data.
        # Here the queue is expected to be used in listen() instead. The callback simply puts the sensor data into the queue,
        # then the data can be obtained in update() using get() which blocks and make sure synchronization.
        self._queue = queue.Queue()

    def update(self):
        """ Wait for sensor event to be put in queue and update data. """
        raise NotImplementedError()

    def destroy(self):
        """ Destroy sensor actor. """
        if self.sensor:
            print('Destroying {}'.format(self.name))
            self.sensor.destroy()
            self.sensor = None