import os

class Recorder(object):
    def __init__(self, recorder_config: dict, map_name: str):
        """
        Constructor method.

        Input:
            recoder_config: Dict of recorders configuration.
        """

        self.save_path = os.path.join(recorder_config['save_path'], map_name)
        if os.path.isdir(self.save_path) is False:
            os.makedirs(self.save_path)

    def save(self, data: dict):
        """
        Save data to disk.

        Input:
            data: Dict of data to be saved.
        """

        raise NotImplementedError()