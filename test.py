import cv2
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
from sklearn.utils import shuffle

class VesselSegmentation:
    def __init__(self):
        self.image_dir = 'sample-images'
        self.image_names = os.listdir(self.image_dir)
        self.image_names = shuffle(self.image_names)

        self.segment()

    def normal_segment(self, gray_img, original_image):

        blurred = cv2.GaussianBlur(gray_img, (9, 9), 0)
        block_size = int(1 / 8 * gray_img.shape[0] / 2 * 2 + 1)
        block_size = block_size + 1 if block_size % 2 == 0 else block_size
        edged_adap = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size,
                                           10)
        low_color = 0
        high_color = 255
        thresh = cv2.inRange(edged_adap, low_color, high_color)
        thresh = cv2.morphologyEx(edged_adap, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        edged_contour = original_image.copy()
        for c in contours:
            area = cv2.contourArea(c)
            if area < 100:
                continue
            cv2.drawContours(edged_contour, [c], -1, (0, 0, 0), -1)
        edged_contour = cv2.cvtColor(edged_contour, cv2.COLOR_BGR2GRAY)

        return edged_adap, edged_contour

    def segment(self):
        for image_name in self.image_names:
            full_path = f'{self.image_dir}/{image_name}'
            original_image = cv2.imread(full_path)
            x_new = int(original_image.shape[1] * .1)
            y_new = int(original_image.shape[0] * .1)
            original_image = original_image[y_new:original_image.shape[0] - y_new, x_new: original_image.shape[1] - x_new]
            gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            edge_adap, edge_contour = self.normal_segment(gray, original_image)
            stacked = np.hstack([gray, edge_adap, edge_contour])
            fig, ax = plt.subplots(2, figsize = (15, 10))
            ax[0].imshow(stacked, cmap = 'gray')
            ax[0].set_title('Normal Segmentation')

            plt.show()



if __name__ == '__main__':
    segment = VesselSegmentation()
