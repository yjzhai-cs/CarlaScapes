import copy
from pascal_voc_writer import Writer

class XMLWriter(Writer):
    """Inherit from pascal_voc_writer.Writer to add a deepcopy method."""
    def __init__(self, path, width, height, depth=3, database='Unknown', segmented=0):
        super().__init__(path, width, height, depth, database, segmented)

        self.path = path
        self.width = width
        self.height = height
        self.depth = depth
        self.database = database
        self.segmented = segmented

    def __deepcopy__(self, memodict={}):
        copy_writer = XMLWriter(self.path, self.width, self.height, self.depth, self.database, self.segmented)
        copy_writer.template_parameters = copy.deepcopy(self.template_parameters, memodict)

        return copy_writer