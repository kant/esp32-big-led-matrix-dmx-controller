from library_bmp_to_binary import multiple_bmp_to_multiple_binary


def main():
    print("Welcome to the Multiple BMP Frames to Multiple Binary Frames Converter!")
    frames = int(input("How many frames do you have in the Folder?"))
    #Start process:

    multiple_bmp_to_multiple_binary(frames)


    print("Thank you for using the Converter!")
    print("Credits: ")
    print("Phil Meyer, 2020")


if __name__ == "__main__":
    main()