import cv2


def cartoon_effect1(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.medianBlur(gray_img, 5)
    edges_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)
    homogen_colors_img = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon_img = cv2.bitwise_and(homogen_colors_img, homogen_colors_img, mask=edges_img)
    return cartoon_img


def cartoon_effect2(img):
    numDownSamples = 2  # number of downscaling steps
    numBilateralFilters = 7  # number of bilateral filtering steps
    img_color = img
    for i in range(numDownSamples):
        img_color = cv2.pyrDown(img_color)
    for i in range(numBilateralFilters):
        img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
    for i in range(numDownSamples):
        img_color = cv2.pyrUp(img_color)
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                     cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    return cv2.bitwise_and(img_color, img_edge)


def main():
    print("cartoon effect with OpenCV...")

    filename = "phil.png"
    filename = "chris.png"
    filename = "family.png"
    filename = "beer.png"

    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    if img is not None:
        cartoon1_img = cartoon_effect1(img)
        cartoon2_img = cartoon_effect2(img)
        down_scaled_image = cv2.resize(img, (50, 28), interpolation=cv2.INTER_AREA)
        down_scaled_cartoon1_image = cv2.resize(cartoon1_img, (50, 28), interpolation=cv2.INTER_AREA)
        down_scaled_cartoon2_image = cv2.resize(cartoon2_img, (50, 28), interpolation=cv2.INTER_AREA)

        cv2.imshow("Original", img)
        cv2.imshow("Cartoon 1", cartoon1_img)
        cv2.imshow("Cartoon 2", cartoon1_img)
        cv2.imshow("Down scaled", down_scaled_image)
        cv2.imshow("Down scaled cartoon 1", down_scaled_cartoon1_image)
        cv2.imshow("Down scaled cartoon 2", down_scaled_cartoon2_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("done")


if __name__ == '__main__':
    main()
