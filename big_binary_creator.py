def multiple_bmp_to_single_binary(count_frames, path):
    print("Your BMPs need to be in BMP folder. Their should be named: 'frame1', 'frame2', ...")
    input("[Press enter to Start Converting]")
    print("Converting to Binary Code Frames")
    print("...")
    count = 1
    while True:
        im = Image.open(path + "\\frame" + str(count) + ".bmp")
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
