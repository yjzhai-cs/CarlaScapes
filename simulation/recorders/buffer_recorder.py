
import os
import cv2
import json
from .base import Recorder

class BufferRecorder(Recorder):
    """BufferRecorder class to record data to disk.
    Don't save data to disk from buffer until buffer is full.
    """
    def __init__(self, recorder_config: dict, map_name: str):
        """
        Constructor method.

        Input:
            recoder_config: Dict of recorders configuration.
        """

        super().__init__(recorder_config, map_name)
        self.map_name = map_name
        self.buffer = None
        self.capacity = recorder_config['capacity']

        self.init()

    def init(self):
        """ Initialize buffer. """
        self.buffer = {
            'rgb_camera': [],
            'gnss': [],
            'instance_camera': [],
            'semantic_camera': []
        }

    def clean(self):
        self.buffer.clear()

    def get_size(self):
        """
        Get current size of buffer.

        Output:
            size: Int of current size of buffer.
        """
        size = 0
        for _, data_buffers in self.buffer.items():
            size = len(data_buffers)
            break

        return size

    def buffering(self, source: dict):
        """
        Save data to buffer. If buffer is full, flush data to disk.
        Record sequential data from source at the current time step.

        Input:
            data: Dict of data to be saved.
        """

        if self.get_size() >= self.capacity:
            self.flush()

        # Iterate over groups
        for group, _ in self.buffer.items():
            self.buffer[group].append(source[group])

    def flush(self):
        """
        Flush data to disk from buffer.
        """
        if self.get_size() == 0:
            return

        # Save the RGB Image to disk
        for i in range(len(self.buffer['rgb_camera'])):
            timestamp = self.buffer['rgb_camera'][i]['timestamp']
            frame = self.buffer['rgb_camera'][i]['frame']
            cv2.imwrite(os.path.join(self.save_path, '%s_%06d_%06d_img.png' % (self.map_name, timestamp, frame)),
                        self.buffer['rgb_camera'][i]['rgb_image'])

            if 'bboxs' in self.buffer['rgb_camera'][i] and self.buffer['rgb_camera'][i]['bboxs'] is not None:
                self.buffer['rgb_camera'][i]['bboxs'].save(os.path.join(self.save_path, '%s_%06d_%06d_bounding_box.xml' % (self.map_name, timestamp, frame)))


        # Save the Semantic Segmentation Image to disk
        for i in range(len(self.buffer['semantic_camera'])):
            timestamp = self.buffer['semantic_camera'][i]['timestamp']
            frame = self.buffer['semantic_camera'][i]['frame']
            cv2.imwrite(os.path.join(self.save_path, '%s_%06d_%06d_color.png' % (self.map_name, timestamp, frame)),
                        self.buffer['semantic_camera'][i]['ss_image'])

            cv2.imwrite(os.path.join(self.save_path, '%s_%06d_%06d_labelIds.png' % (self.map_name, timestamp, frame)),
                        self.buffer['semantic_camera'][i]['labelIds_image'])

        # Save the Instance Segmentation Image to disk
        for i in range(len(self.buffer['instance_camera'])):
            timestamp = self.buffer['instance_camera'][i]['timestamp']
            frame = self.buffer['instance_camera'][i]['frame']
            cv2.imwrite(os.path.join(self.save_path, '%s_%06d_%06d_instance.png' % (self.map_name, timestamp, frame)),
                        self.buffer['instance_camera'][i]['in_image'])

        # Save the GNSS data to disk
        for i in range(len(self.buffer['gnss'])):
            timestamp = self.buffer['gnss'][i]['timestamp']
            frame = self.buffer['gnss'][i]['frame']
            with open(os.path.join(self.save_path, '%s_%06d_%06d_gnss.json' % (self.map_name, timestamp, frame)), 'w') as f:
                json.dump(self.buffer['gnss'][i], f)

        # Clean the buffer and re-initialize it
        self.clean()
        self.init()

    def save(self, data: dict):
        pass