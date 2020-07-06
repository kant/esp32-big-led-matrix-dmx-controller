from PIL import Image

#This comment is new!!
def single_bmp_to_binary(bmp_file_name, bin_file_name):
    print("Converting to Binary Code")
    print("...")
    im = Image.open(bmp_file_name)
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


def multiple_bmp_to_multiple_binary(count_frames):
    print("Your BMPs need to be named: 'frame1', 'frame2', ...")
    input("[Press enter to Start Converting]")
    print("Converting to Binary Code Frames")
    print("...")
    count = 1
    while True:
        im = Image.open("frame" + str(count) + ".bmp")
        bin_file = open("frame" + str(count) + ".bmp", 'w+b')
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






