from library_bmp_to_binary import multiple_bmp_to_single_binary


def main():
    print("Welcome to the Multiple BMP Frames to Single Binary File Converter!")
    path = input("In witch folder are the Bitmaps? standard:'BMP' or 'OUTPUT_FRAMES'")
    frames = int(input("How many frames do you have in the Folder?"))
    #Start process:
    led_count = 49   # Not used in moment
    multiple_bmp_to_single_binary(frames, path, led_count)

    # Print Done
    print("\n")
    print("The Job is Done. Thank you for using the converter.")
    print("Thank you for using the Converter!")
    print("Credits: ")
    print("Phil Meyer, 2020")


if __name__ == "__main__":
    main()