from PIL import Image
import cv2
import os
import shutil
import socket
import struct
import time
from time import sleep
import keyboard


def single_bmp_to_binary(bmp_file_name, bin_file_name):
    print("Converting to Binary Code")
    print("...")
    im = Image.open("BMP\\" + bmp_file_name)
    bin_file = open(bin_file_name, 'w+b')
    led_number = 0
    matrix_height = im.size[1]
    y = matrix_height - 1
    while y >= 0:
        led_number = iterate_line_from_left_to_right(bin_file, im, led_number, y)
        y = y - 1
        if y >= 0:
            led_number = iterate_line_from_right_to_left(bin_file, im, led_number, y)
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


def get_current_ntp_time_ms():
    current_unix_time_s = time.time()
    current_ntp_time_s = current_unix_time_s + 2208988800
    current_ntp_time_ms = current_ntp_time_s * 1000
    return current_ntp_time_ms


def lt1_video(video_file_name):
    # Setup all that video stuff
    vidcap = cv2.VideoCapture(video_file_name)  # Open the Video
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1  # Get Video length
    count = 0

    # Setup all that time stuff
    print("sending frame sequence to ESPs")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    last_send_frame_packet_time = get_current_ntp_time_ms()
    frame_packet_has_been_sent = False
    time_offset = 200
    time_to_present_frame = last_send_frame_packet_time + time_offset

    print("  present first frame at NTP time (in ms) {0}".format(time_to_present_frame))

    while True:
        p1 = bytearray()  # Create / Clear byte arrays
        p2 = bytearray()  # Create / Clear byte arrays
        p3 = bytearray()  # Create / Clear byte arrays
        p4 = bytearray()  # Create / Clear byte arrays

        success, image = vidcap.read()  # Read the Video Frame
        if not success:
            break
        size = (50, 28)
        image = cv2.resize(image, size)  # Resize
        # Some debug shit
        # cv2.imwrite("frame" + str(count) + ".png", image)  # Saving Image to Debug
        # p1_bin_file = open("p1_frame" + str(count) + ".bin", 'w+b')

        # Prepare packages
        p1 = fill_bytearray_p1(p1, image, time_to_present_frame)
        p2 = fill_bytearray_p2(p2, image, time_to_present_frame)
        p3 = fill_bytearray_p3(p3, image, time_to_present_frame)
        p4 = fill_bytearray_p4(p4, image, time_to_present_frame)

        # WAITING FOR PERMISSION TO LIFT OF
        if frame_packet_has_been_sent:
            # wait until approx. 40 ms elapsed from last packet has been sent
            wait_time_ms = 40.0 - (get_current_ntp_time_ms() - last_send_frame_packet_time)
            if wait_time_ms > 0:
                sleep(wait_time_ms / 1000.0)

        # SEND
        send_to_esp(opened_socket, p1, p2, p3, p4)

        # Set time values
        frame_packet_has_been_sent = True
        last_send_frame_packet_time = get_current_ntp_time_ms()
        time_to_present_frame = last_send_frame_packet_time + time_offset + 40

        # p1_bin_file.close()

        # If the stop key is pressed, stop the thing
        if wait_for_keyboard_input():
            break

        # Loop things and begin again with the next frame.
        count = count + 1
        if count > (video_length-1):
            vidcap.release()  # Relase the Video / End
            break


def lt2_video(video_file_name):
    # Setup all that video stuff
    vidcap = cv2.VideoCapture(video_file_name)  # Open the Video
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1  # Get Video length
    count = 0

    # Setup all that time stuff
    print("sending frame sequence to ESPs")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    last_send_frame_packet_time = get_current_ntp_time_ms()
    frame_packet_has_been_sent = False
    time_offset = 200
    time_to_present_frame = last_send_frame_packet_time + time_offset

    print("  present first frame at NTP time (in ms) {0}".format(time_to_present_frame))

    while True:
        p1 = bytearray()  # Create / Clear byte arrays
        p2 = bytearray()  # Create / Clear byte arrays
        p3 = bytearray()  # Create / Clear byte arrays
        p4 = bytearray()  # Create / Clear byte arrays

        success, image = vidcap.read()  # Read the Video Frame
        if not success:
            break
        size = (50, 14)
        image = cv2.resize(image, size)  # Resize
        # Some debug shit
        # cv2.imwrite("frame" + str(count) + ".png", image)  # Saving Image to Debug
        # p1_bin_file = open("p1_frame" + str(count) + ".bin", 'w+b')

        # Prepare packages
        p1 = fill_bytearray_p1(p1, image, time_to_present_frame)
        p2 = fill_bytearray_p2(p2, image, time_to_present_frame)

        # WAITING FOR PERMISSION TO LIFT OF
        if frame_packet_has_been_sent:
            # wait until approx. 40 ms elapsed from last packet has been sent
            wait_time_ms = 40.0 - (get_current_ntp_time_ms() - last_send_frame_packet_time)
            if wait_time_ms > 0:
                sleep(wait_time_ms / 1000.0)

        # SEND
        send_to_esp(opened_socket, p1, p2, p3, p4)

        # Set time values
        frame_packet_has_been_sent = True
        last_send_frame_packet_time = get_current_ntp_time_ms()
        time_to_present_frame = last_send_frame_packet_time + time_offset + 40

        # p1_bin_file.close()

        # If the stop key is pressed, stop the thing
        if wait_for_keyboard_input():
            break

        # Loop things and begin again with the next frame.
        count = count + 1
        if count > (video_length - 1):
            vidcap.release()  # Relase the Video / End
            break


def lt3_video(video_file_name):
    # Setup all that video stuff
    vidcap = cv2.VideoCapture(video_file_name)  # Open the Video
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1  # Get Video length
    count = 0

    # Setup all that time stuff
    print("sending frame sequence to ESPs")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    last_send_frame_packet_time = get_current_ntp_time_ms()
    frame_packet_has_been_sent = False
    time_offset = 200
    time_to_present_frame = last_send_frame_packet_time + time_offset

    print("  present first frame at NTP time (in ms) {0}".format(time_to_present_frame))

    while True:
        p1 = bytearray()  # Create / Clear byte arrays
        p2 = bytearray()  # Create / Clear byte arrays
        p3 = bytearray()  # Create / Clear byte arrays
        p4 = bytearray()  # Create / Clear byte arrays

        success, image = vidcap.read()  # Read the Video Frame
        if not success:
            break
        size = (25, 28)
        image = cv2.resize(image, size)  # Resize
        # Some debug shit
        # cv2.imwrite("frame" + str(count) + ".png", image)  # Saving Image to Debug
        # p1_bin_file = open("p1_frame" + str(count) + ".bin", 'w+b')

        # Prepare packages
        p1 = fill_bytearray_p1(p1, image, time_to_present_frame)
        p3 = fill_bytearray_p3(p3, image, time_to_present_frame)

        # WAITING FOR PERMISSION TO LIFT OF
        if frame_packet_has_been_sent:
            # wait until approx. 40 ms elapsed from last packet has been sent
            wait_time_ms = 40.0 - (get_current_ntp_time_ms() - last_send_frame_packet_time)
            if wait_time_ms > 0:
                sleep(wait_time_ms / 1000.0)

        # SEND
        send_to_esp(opened_socket, p1, p2, p3, p4)

        # Set time values
        frame_packet_has_been_sent = True
        last_send_frame_packet_time = get_current_ntp_time_ms()
        time_to_present_frame = last_send_frame_packet_time + time_offset + 40

        # p1_bin_file.close()

        # If the stop key is pressed, stop the thing
        if wait_for_keyboard_input():
            break

        # Loop things and begin again with the next frame.
        count = count + 1
        if count > (video_length - 1):
            vidcap.release()  # Relase the Video / End
            break


def send_to_esp(opened_socket, package1, package2, package3, package4):
    opened_socket.sendto(package1, ("ESP-158", 50000))  # Send data to P1
    opened_socket.sendto(package2, ("192.168.2.160", 50000))  # Send data to P2
    opened_socket.sendto(package3, ("ESP-157", 50000))  # Send data to P3
    opened_socket.sendto(package4, ("192.168.2.161", 50000))  # Send data to P4


def fill_bytearray_p1(package, image, time_to_present_frame):
    package += struct.pack('<Q', round(time_to_present_frame))  # TimeStamp
    # LED Values
    for x in range(0, 14, 2):
        for y in range(0, 25, 1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)
            # pixel__arr = [r, g, b]
            # binary_format = bytearray(pixel__arr)
            # p1_bin_file.write(binary_format)

        x = x + 1
        for y in range(24, -1, -1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)
            # pixel__arr = [r, g, b]
            # binary_format = bytearray(pixel__arr)
            # p1_bin_file.write(binary_format)

    return package


def fill_bytearray_p2(package, image, time_to_present_frame):
    package += struct.pack('<Q', round(time_to_present_frame))  # TimeStamp
    # LED Values
    for x in range(0, 14, 2):
        for y in range(25, 50, 1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

        x = x + 1
        for y in range(49, 24, -1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

    return package


def fill_bytearray_p3(package, image, time_to_present_frame):
    package += struct.pack('<Q', round(time_to_present_frame))  # TimeStamp
    # LED Values
    for x in range(14, 28, 2):
        for y in range(0, 25, 1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

        x = x + 1
        for y in range(24, -1, -1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

    return package


def fill_bytearray_p4(package, image, time_to_present_frame):
    package += struct.pack('<Q', round(time_to_present_frame))  # TimeStamp
    # LED Values
    for x in range(14, 28, 2):
        for y in range(25, 50, 1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

        x = x + 1
        for y in range(49, 24, -1):
            b, g, r = (image[x, y])
            package.append(r)
            package.append(g)
            package.append(b)

    return package


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


def wait_for_keyboard_input():
    if keyboard.is_pressed('f6'):
        return True




