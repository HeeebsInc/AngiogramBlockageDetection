import numpy as np
import cv2
# from tqdm import tqdm
import os
import matplotlib.pyplot as plt

class DetectAngiogramDisease:
    def __init__(self, input_dir: str, output_dir: str):
        """
        Instantiation of the program.  This program will take an input directory that contains images, and will run each
        through a series of processes to determine if the angiogram images show cardiovascular disease.
        This program supports only angiogram xray images.

        :param input_dir: Directory path for where the original images are stored (String)
        :param output_dir: Directory path to save the output detection images (String)
        :param save_all_steps: If True, the program will save each step of the process instead of only saving the final image.  (Bool)

        """
        print('='* 125)
        print(''' ____   _       ___      __  __  _   ____   ____    ___      ___      ___  ______    ___     __  ______  ____  ___   ____  
|    \ | |     /   \    /  ]|  |/ ] /    | /    |  /  _]    |   \    /  _]|      |  /  _]   /  ]|      ||    |/   \ |    \ 
|  o  )| |    |     |  /  / |  ' / |  o  ||   __| /  [_     |    \  /  [_ |      | /  [_   /  / |      | |  ||     ||  _  |
|     || |___ |  O  | /  /  |    \ |     ||  |  ||    _]    |  D  ||    _]|_|  |_||    _] /  /  |_|  |_| |  ||  O  ||  |  |
|  O  ||     ||     |/   \_ |     \|  _  ||  |_ ||   [_     |     ||   [_   |  |  |   [_ /   \_   |  |   |  ||     ||  |  |
|     ||     ||     |\     ||  .  ||  |  ||     ||     |    |     ||     |  |  |  |     |\     |  |  |   |  ||     ||  |  |
|_____||_____| \___/  \____||__|\_||__|__||___,_||_____|    |_____||_____|  |__|  |_____| \____|  |__|  |____|\___/ |__|__|
''')
        print('='*125)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self._run()

    def _run(self):
        try:
            image_names = os.listdir(self.input_dir)
        except NotADirectoryError:
            raise Exception(f'ERROR: YOU HAVE PASSED IN A FILE ({self.input_dir}) INSTEAD OF A DIRECTORY\n')
        assert len(image_names) > 0, f'ERROR: THERE ARE NO IMAGES FOUND IN {self.input_dir}'

        for image_name in image_names:
            print(f'\033[1;31;40mRunning {image_name} through program..')
            # pbar.set_description(f'Running {image_name} through program..')
            full_image_path = f'{self.input_dir}/{image_name}'
            output_path = f'{self.output_dir}/{image_name}'
            get_user_input = self._get_user_input(image_name)
            img = cv2.imread(full_image_path)
            if get_user_input == 'y':
                #this will call the drawing function so that we can extract the
                #ROI  (xmin, ymin, xmax, ymax)
                coord = self._draw_on_image(img, full_image_path)
                if len(coord) == 0:
                    x_new = int(img.shape[1] * .1)
                    y_new = int(img.shape[0] * .1)
                    cropped_img = img[y_new:img.shape[0] - y_new, x_new: img.shape[1] - x_new]
                else:
                    xmin, ymin, xmax, ymax = coord
                    #crop the image using the ROI region
                    cropped_img = img[ymin:ymax, xmin: xmax]
                    #resize the image to a flat dim so that it will perform well
                    cropped_img = cv2.resize(cropped_img, (500,500), cv2.INTER_LINEAR)
                self.run_segmentation(cropped_img, output_path)

            else:
                # this will crop the image borders to exclude the black portion taht is often found in x-ray images
                x_new = int(img.shape[1] * .1)
                y_new = int(img.shape[0] * .1)
                img = img[y_new:img.shape[0] - y_new, x_new: img.shape[1] - x_new]
                self.run_segmentation(img, output_path)

            print('~'*100)
        # pbar.close()

    def run_segmentation(self, img: np.array, output_path: str) -> np.array:
        """
        This function will perform segmentation on an image.  If there is blockage detected, it will
        mark a circle around that area.  Once the segmentation is finsihed, the program will save
        the image or all the steps performed in the output path provided
        :param img: The image which you want to perform the segmentation
        :param output_path: The output path of the image
        :return: Output image with the regions marked
        """
        img_dict = {}

        #convert the image to gray then apply brightness correction
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = self._automatic_brightness_and_contrast(gray)

        #blur the image to remove noise.  By doing this we get better contours during segmentation
        blurred = cv2.medianBlur(gray, 5)
        img_dict['blurred'] = blurred
        img_dict['brightness corrected'] = gray

        #this creates a 12 blocks to perform the adaptive thresholding.  Because x-rays are not consistent in where things are
        #present in the image, using 12 blocks will often include all necessary pixel distributions for the thresholding
        block_size = int(blurred.shape[0] / 12)
        block_size = block_size + 1 if block_size % 2 == 0 else block_size

        #perform adaptive thresholding using the block size.  This will use dynamic thrshold and turn every pixel above this number to 255
        edged_adap = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size,
                                           10)

        #determine the min contour area.  Having a higher number will reduce contours over noise but can also pose the problem
        #of missing the vessel
        min_contour_area = 50

        #perform thresholding using Ellipse and a kernel of 3x3.
        #Then apply contours to find the edges within the thresholded image
        #these contours will be used to perform more thresholding later on
        thresh = cv2.morphologyEx(edged_adap, cv2.MORPH_ELLIPSE, np.ones((3, 3), np.uint8))
        #find contours using the external boundaries found in the image.
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = [i for i in contours if cv2.contourArea(i) > min_contour_area]
        edged_contour = img.copy()

        for idx1, c1 in enumerate(contours):
            cv2.drawContours(edged_contour, [c1], -1, (0, 0, 0), -1)


        edged_contour = cv2.cvtColor(edged_contour, cv2.COLOR_BGR2GRAY)
        #perform another round of thresholding where it will turn every pixel above 0 to 255
        threshed = cv2.threshold(edged_contour, 0, 255, cv2.THRESH_BINARY_INV)[1]
        #dilate the image to make the gaps get a bit closer to each other.
        dilated = cv2.dilate(threshed, None, iterations=2)
        img_dict['edged contour'] = edged_contour
        img_dict['threshed edged contour'] = threshed
        img_dict['dilated'] = dilated

        min_contour_area = 1250
        output_image = img.copy()
        #perform another contour operation to get the outline of the dilated image
        thresh = cv2.morphologyEx(dilated, cv2.MORPH_ELLIPSE, np.ones((3, 3), np.uint8))
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = [i for i in contours if cv2.contourArea(i) > min_contour_area]
        detections = 0
        for idx1, c1 in enumerate(contours):
            for idx2, c2 in enumerate(contours):
                if idx2 == idx1:
                    continue
                #determine if the contour is close to another contour.  If it is within the minimum specified below (10),
                #then that is an area where there could be blockage in the blood vessel
                point = self._find_if_close(c1, c2, 10)
                if point:
                    detections += 1
                    center = tuple(contours[idx1][point].squeeze())
                    cv2.circle(output_image, center, 25, (0, 0, 255), 2)

        #display the image and write output determinations
        message = f'Possible Blockage' if detections > 0 else 'No Blockage Detected'
        color = (0, 0, 255) if detections > 0 else (0, 255, 0)
        output_image = cv2.putText(output_image, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        img_dict['output image'] = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        fig, ax = plt.subplots(1, 6, figsize=(20, 10))
        for idx2, (name, im) in enumerate(img_dict.items()):
            if len(im.shape) == 2:
                ax[idx2].imshow(im, cmap='gray')
                ax[idx2].set_title(f'Step {idx2+1 } | {name}')
                continue
            ax[idx2].imshow(im)
            ax[idx2].set_title(name)
        plt.show()
        if '.jpeg' in output_path or '.jpg' in output_path or '.png' in output_path:
            output_path = output_path
            reversed_output_path = output_path[::-1]
            reversed_output_path = reversed_output_path[reversed_output_path.find('.')+1:]
            figure_path = f'{reversed_output_path[::-1]}_steps.jpg'
        else:
            reversed_output_path = output_path[::-1]
            reversed_output_path = reversed_output_path[reversed_output_path.find('.')+1:][::-1]
            output_path = f'{reversed_output_path}.jpg'
            figure_path = f'{reversed_output_path}_steps.jpg'
        fig.savefig(figure_path)
        cv2.imwrite(output_path, output_image)


        #this will display the output image
        cv2.imshow('Output Image | Press q to exit', output_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(f'FINISHED SAVING {output_path} IMAGE')
        return img

    def _draw_callback(self, event, x, y, flags, param):
        """
        This function is used as a callback feature for drawing a bounding box on an image.  This
        function is called when the user specifies that they want to draw the region of interest of the program
        :param event:
        :param x:
        :param y:
        :param flags:
        :param param:
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix = x
            self.iy = y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                img2 = cv2.imread(self.img_path)
                self.bboxes.append((self.ix, self.iy, x, y))
                cv2.rectangle(img2, pt1=(self.ix, self.iy), pt2=(x, y), color=(0, 0, 255), thickness=10)
                self.img = img2

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            img2 = cv2.imread(self.img_path)
            cv2.rectangle(img2, pt1=(self.ix, self.iy), pt2=(x, y), color=(0, 0, 255), thickness=10)
            self.bboxes.append((self.ix, self.iy, x, y))
            self.img = img2

    def _draw_on_image(self, img: np.array, img_path: str) -> tuple:
        """
        This function will initialize the drawing function when the user specifies they want to add a
        region of interest for the segmentation process.  It will return the coordinates of the box so that
        we can crop the image to just that area
        :param img: image array (np.array)
        :param img_path: the path of the original image
        :return: tuple containing the bbox coordinates (xmin, ymin, xmax, ymax)
        """
        self.ix, self.iy = -1, -1
        self.img = img
        self.drawing = False
        self.img_path = img_path
        self.bboxes = []
        cv2.namedWindow('Original Image | When the you are finished, press q key')
        cv2.setMouseCallback('Original Image | When the you are finished, press q key', self._draw_callback)
        while True:
            cv2.imshow('Original Image | When the you are finished, press q key', self.img)
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        if len(self.bboxes) == 0:
            return ()
        x = np.array([i[0] for i in self.bboxes] + [i[2] for i in self.bboxes])
        y = np.array([i[1] for i in self.bboxes] + [i[3] for i in self.bboxes])
        return (x.min(), y.min(), x.max(), y.max())

    def _automatic_brightness_and_contrast(self, image: np.array, clip_hist_percent: int = 1) -> np.array:
        """
        This function will perform a dynamic calculation for normalizing the brightness in the image.

        Using histograms, it will balance the brightness across the image so that there is no one area that
        is a lot brighter/darker than the rest of the image
        :param image: image array (np.array)
        :param clip_hist_percent: the percentage in which the histogram will clip the pixel values
        :return: The output image (np.array).  This image will have the new brightness adjustments
        """
        # Calculate grayscale histogram
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_size = len(hist)

        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index - 1] + float(hist[index]))

        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum / 100.0)
        clip_hist_percent /= 2.0

        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1

        # Locate right cut
        maximum_gray = hist_size - 1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1

        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha

        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return auto_result

    def _find_if_close(self, cnt1: list, cnt2: list, min_dist: int=10):
        """
        This function will perform a euclidean distance between two contours to find the distance of the closest points
        If the distance is below the min_dist parameter, it will return the idx of that contour where that occurs, otherwise it
        will return False
        :param cnt1: List containing points for the first contour
        :param cnt2: List containing points for the second contour
        :param min_dist: The minimum distance in which a contour can be to the other contour. Default is 10 pixels
        :return: The index if it is within that distance, otherwise False (no points are within the distance)
        """
        row1, row2 = cnt1.shape[0], cnt2.shape[0]
        for i in range(row1):
            for j in range(row2):
                dist = np.linalg.norm(cnt1[i] - cnt2[j])
                if abs(dist) < min_dist:
                    return i
                elif i == row1 - 1 and j == row2 - 1:
                    return False

    def _get_user_input(self, image_name: str) -> str:
        """
        This function will determine if the user wants to add a cropping method to have an ROi instead
        of the entire image fed through the segmentation process
        :param image_name: The name of the image that is being fed
        :return: The user's answer (either y or n)
        """
        while True:
            user_input = input(f'\033[1;33;40mWould you like to specify the area within the image {image_name}?\t'
                               'Y for yes | N for no\n'
                               'By entering Y, a pop will open with the image where you can draw a bounding box to specify the target area\n'
                               'By entering N, you will let the program run through the entire image without a bbox specification\n'
                               'ENTER HERE ->  ')
            if user_input.lower() not in ['n', 'y']:
                continue
            else:
                return user_input.lower()



if __name__ == '__main__':
    # import array_to_latex as a2l
    # s_list = [cv2.MORPH_ELLIPSE, cv2.MORPH_CROSS, cv2.MORPH_RECT]
    # for s in s_list:
    #     array_ex = cv2.getStructuringElement(s, (5,5))
    #     print(a2l.to_ltx(array_ex, arraytype = 'bmatrix'))
    # assert False
    param_dict = {
        'input_dir': 'sample-images',
        'output_dir': 'output-images',
    }
    da = DetectAngiogramDisease(**param_dict)
