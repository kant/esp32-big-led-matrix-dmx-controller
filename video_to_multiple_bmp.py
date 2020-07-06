from library_bmp_to_binary import video_to_frames
from library_bmp_to_binary import frames_to_bmp


def main():
    video_file_name = input("Please enter the name of your mp4 Video? (format: video.mp4)")  # Video File Name
    video_to_frames(video_file_name)  # Extract Images from Video

    matrix_width = input("Enter the width of your Matrix?")  # Matrix Width
    matrix_height = input("Enter the height of your Matrix")  # Matrix height
    frames_to_bmp(video_file_name, matrix_width, matrix_height)  # Convert Images to Bitmaps


    # Print Done
    print("\n")
    print("The Job is Done. Thank you for using the converter.")
    print("Thank you for using the Converter!")
    print("Credits: ")
    print("Phil Meyer, 2020")


if __name__ == "__main__":
    main()