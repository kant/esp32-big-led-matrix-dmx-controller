from multiprocessing import Process
from library_bmp_to_binary import wait_for_keyboard_input
from library_bmp_to_binary import lt1_video
from library_bmp_to_binary import lt2_video
from library_bmp_to_binary import lt3_video


def main():
    # video_file_name = "nyancat.mp4"       # Test Video 1
    # video_file_name = "simpsons.mp4"      # Test Video 2
    # video_file_name = "red_rectangle.mp4" # Test Video 3
    video_file_name = "neverplaythis.mp4"   # Test Video 4

    p1 = Process(target=wait_for_keyboard_input())      # Start listener for stop key (F6 for testing reasons)
    p1.start()
    # p2 = Process(target=lt1_video(video_file_name))   # Layout type 1
    # p2 = Process(target=lt2_video(video_file_name))   # Layout type 2
    p2 = Process(target=lt3_video(video_file_name))     # Layout type 3
    p2.start()

    p1.join()   # Join processes
    p2.join()   # Join processes



if __name__ == '__main__':
    main()


