
import cv2

image_path = '../outputs/Town10HD/Town10HD_000075_458800_color.png'
labelIds_path = '../outputs/Town10HD/Town10HD_000075_458800_labelIds.png'

image = cv2.imread(image_path)
print(image)
labelIds = cv2.imread(labelIds_path)
print(labelIds)