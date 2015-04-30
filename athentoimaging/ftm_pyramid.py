import cv2 as cv
import numpy as np
import argparse
import os
import img_utils as iu

"""
This script performs a fast template matching algorithm using the OpenCV
function matchTemplate plus an approximation through pyramid construction to
improve it's performance on large images.
"""


def build_pyramid(input_file, max_level):

    image = iu.get_image(input_file)

    results = [image]
    aux = image.copy()

    for i in range(0, max_level):
        aux = cv.pyrDown(aux, (aux.shape[1]/2, aux.shape[0]/2))
        results = [aux] + results

    return results


def temp_match(input_file, template, max_level):

    results = []

    source_pyr = build_pyramid(input_file, max_level)
    template_pyr = build_pyramid(template, max_level)

    for lvl in range(0, int(max_level), 1):

        curr_image = source_pyr[lvl]
        curr_template = template_pyr[lvl]

        shapeX = curr_image.shape[1] - curr_template.shape[1] + 1
        shapeY = curr_image.shape[0] - curr_template.shape[1] + 1

        result = np.zeros([shapeX, shapeY])


        #On the first level performs regular template matching.
        if lvl == 0:
            result = cv.matchTemplate(curr_image, curr_template,
                                      cv.TM_CCORR_NORMED)

        #On every other level, perform pyramid transformation and template
        #matching on the predefined ROI areas, obtained using the result of the
        #previous level.
        else:
            mask = cv.pyrUp(r)
            mask8u = np.uint8(mask)
            contours = cv.findContours(mask8u, cv.RETR_EXTERNAL,
                                       cv.CHAIN_APPROX_NONE)

            #Uses contours to define the region of interest and perform TM on
            #the areas.

            for cnt in contours[0]:
                x, y, w, h = cv.boundingRect(cnt)
                dx = x + w + curr_template.shape[1] - 1
                dy = y + h + curr_template.shape[0] - 1

                result[y:h, x:w] = cv.matchTemplate(
                    curr_image[y:dy, x:dx],
                    curr_template,
                    cv.TM_CCORR_NORMED)

        if result.all() != 0:
            T, r = cv.threshold(result, 0.94, 1., cv.THRESH_TOZERO)
            results.append(r)

            cv.imshow("R", r)
            cv.waitKey()
            cv.destroyAllWindows()

    return results


def ftm_pyramid(input_file, template_file, max_level=5):

    image = iu.get_image(input_file, 0)
    template = iu.get_image(template_file, 0)

    tm_results = temp_match(image, template, max_level)

    for r in tm_results:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(r)
        if max_val > 0.9:
            cv.rectangle(image,
                         max_loc,
                         (max_loc[0] + template.shape[1],
                          max_loc[1] + template.shape[0]),
                         (0, 0, 255), 2)

    cv.imshow("Result", image)
    cv.waitKey()
    return 0


if __name__ == '__main__':
    #CLI arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required="True",
                    help="Path to the input image.")
    ap.add_argument("-t", "--template", required="True",
                    help="Path to the template image.")
    ap.add_argument("-l", "--levels", help="Number of levels of the pyramid.")
    args = vars(ap.parse_args())

    #Loading values
    input_file = args["input"]
    template = args["template"]
    max_lvl = args["levels"]

    if max_lvl is None:
        max_lvl = 5

    ftm_pyramid(input_file, template, int(max_lvl))