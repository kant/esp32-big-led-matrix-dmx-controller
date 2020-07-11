from PIL import Image
import cv2
import os
import shutil


def single_bmp_to_binary(bmp_file_name, bin_file_name):
    print("Converting to Binary Code")
    print("...")
    im = Image.open("BMP\\" + bmp_file_name)
    bin_file = open(bin_file_name, 'w+b')
    led_number = 0
    matrix_height = im.size[1]
    y = matrix_height - 1
    while y >= 0:
        led_number = iterate_line_from_right_to_left(bin_file, im, led_number, y)
        y = y - 1
        if y >= 0:
            led_number = iterate_line_from_left_to_right(bin_file, im, led_number, y)
            y = y - 1

    bin_file.close()
    print("Done converting to Binary File.")


def multiple_bmp_to_multiple_binary(count_frames, path):
    print("Your BMPs need to be in BMP folder. Their should be named: 'frame1', 'frame2', ...")
    input("[Press enter to Start Converting]")
    print("Converting to Binary Code Frames")
    print("...")
    count = 1
    while True:
        im = Image.open(path + "\\frame" + str(count) + ".bmp")
        bin_file = open("frame" + str(count) + ".bin", 'w+b')
        led_number = 0
        matrix_height = im.size[1]
        y = matrix_height - 1
        while y >= 0:
            led_number = iterate_line_from_right_to_left(bin_file, im, led_number, y)
            y = y - 1
            if y >= 0:
                led_number = iterate_line_from_left_to_right(bin_file, im, led_number, y)
                y = y - 1

        bin_file.close()

        count = count + 1
        if int(count) > (int(count_frames) - 1):
            break

    print("Done converting to Binary Frames.")


def multiple_bmp_to_single_binary(frames_count, path, led_count):
    bin_file = open("animation.bin", 'w+b')
    frames = [0, 0, 0, 10]
    binary = bytearray(frames)
    bin_file.write(binary)
    leds = [0, 0, 0, 49]
    binary = bytearray(leds)
    bin_file.write(binary)

    count = 0
    while True:
        im = Image.open(path + "\\frame" + str(count) + ".bmp")
        led_number = 0
        matrix_height = im.size[1]
        y = matrix_height - 1
        while y >= 0:
            led_number = iterate_line_from_right_to_left(bin_file, im, led_number, y)
            y = y - 1
            if y >= 0:
                led_number = iterate_line_from_left_to_right(bin_file, im, led_number, y)
                y = y - 1


        count = count + 1
        if int(count) > (int(frames_count) - 1):
            break

    bin_file.close()
    print("Done converting to Binary Frames.")




def video_to_frames(video_file_name):
    isFile1 = os.path.isdir("OUTPUT_FRAMES_TEMP")  # Check for Temp Folder
    if not isFile1:
        os.mkdir("OUTPUT_FRAMES_TEMP")  # Create Temp Folder for full sized frames
    vidcap = cv2.VideoCapture(video_file_name)
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("Extracting Frames...")
    count = 0
    while True:
        success, image = vidcap.read()  # Read the Video Frame
        cv2.imwrite("OUTPUT_FRAMES_TEMP" + "\\full_size_frame" + str(count) + ".jpg", image)  # Save the Frame
        count = count + 1
        if count > (video_length-1):
            vidcap.release()  # Relase the Video / End
            print("Done extracting Frames.\n%d frames extracted" % count)
            break


def frames_to_bmp(video_file_name, matrix_width, matrix_height):
    vidcap = cv2.VideoCapture(video_file_name) # Gets Video
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1  # Gets Video Length
    print("Converting Frames to BMPs...")
    count = 0
    while True:
        im = Image.open("OUTPUT_FRAMES_TEMP" + "\\full_size_frame" + str(count) + ".jpg")  # Read a full size Image
        im_resized = im.resize((int(matrix_width), int(matrix_height)), resample=3, box=None)  # Convert
        im_resized.save("OUTPUT_FRAMES" + "\\frame" + str(count) + ".bmp")  # Save Bitmap
        count = count + 1
        if count > (video_length-1):
            vidcap.release()  # Release the Video / End
            shutil.rmtree("OUTPUT_FRAMES_TEMP")  # Delete Temporary Frames Folder
            print("Done converting Frames.\n%d frames converted." % count)
            print("\n")
            break



def print_pixel(bin_file, im, led_number, x, y):
    r, g, b = im.getpixel((x, y))
    pixel__arr = [r, g, b]
    binary_format = bytearray(pixel__arr)
    bin_file.write(binary_format)


def iterate_line_from_left_to_right(bin_file, im, led_number, y):
    matrix_width = im.size[0]
    for x in range(matrix_width):
        print_pixel(bin_file, im, led_number, x, y)
        led_number = led_number + 1
    return led_number


def iterate_line_from_right_to_left(bin_file, im, led_number, y):
    matrix_width = im.size[0]
    for x in range(matrix_width - 1, -1, -1):
        print_pixel(bin_file, im, led_number, x, y)
        led_number = led_number + 1
    return led_number






