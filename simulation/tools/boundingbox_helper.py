import os
import sys
import cv2
import xml.etree.ElementTree as ET

from path import Path
from simulation.tools.base import VisualizationHelper

PROJECT_DIR = Path(__file__).parent.parent.parent.abspath()

class BoundingBoxHelper(VisualizationHelper):
    def __init__(self):
        super(BoundingBoxHelper, self).__init__()

    def parse_voc_xml(self, xml_file):
        """Parse voc xml file to get bounding boxes"""

        if os.path.isfile(xml_file) is False:
            print(f"XML File {xml_file} does not exist")
            sys.exit(1)

        tree = ET.parse(xml_file)
        root = tree.getroot()

        boxes = []
        for object in root.findall('object'):
            name = object.find('name').text
            bndbox = object.find('bndbox')
            xmin = int(round(float(bndbox.find('xmin').text)))
            ymin = int(round(float(bndbox.find('ymin').text)))
            xmax = int(round(float(bndbox.find('xmax').text)))
            ymax = int(round(float(bndbox.find('ymax').text)))
            boxes.append((name, (xmin, ymin, xmax, ymax)))

        return boxes

    def draw_boxes(self, image_path, boxes):
        """Draw bounding boxes on image"""

        if os.path.isfile(image_path) is False:
            print(f"Image File {image_path} does not exist")
            sys.exit(1)

        # Read image
        image = cv2.imread(image_path)

        # Draw bounding boxes and class names on image
        for box in boxes:
            name, (xmin, ymin, xmax, ymax) = box
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 1)
            cv2.putText(image, name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 1)

        # Show image
        cv2.imshow('Image with Bounding Boxes', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def visualize(self, data: dict = None):
        """
        Visualize data.

        Input:
            data: Dict of data to be visualized.
        """
        pass

if __name__ == '__main__':
    xml_file = PROJECT_DIR / 'outputs' / 'Town10HD' / 'Town10HD_000013_5025800_bounding_box.xml'  # PASCAL VOC format XML file path
    image_path = PROJECT_DIR / 'outputs' / 'Town10HD' / ('Town10HD_000013_5025800_color.png') # Corresponding image file path)

    helper = BoundingBoxHelper()
    boxes = helper.parse_voc_xml(xml_file=xml_file)
    helper.draw_boxes(image_path=image_path, boxes=boxes)

