import socket
import time
import struct
from time import sleep


def get_current_time_ms():
    return time.time() * 1000


def build_master_time_packet(master_time_ms):
    master_time_packet = bytearray()
    # 8 bytes represent the master time
    # round time (float), pack it with little-Endian as unsigned long long (uint64_t in C/C++)
    master_time_packet += struct.pack('<Q', round(master_time_ms))
    return master_time_packet


def build_frame_packet(time_to_present_frame, color):
    frame_packet = bytearray()
    # first 8 bytes represent the master time at which the frame shall be presented
    # round time (float), pack it with little-Endian as unsigned long long (uint64_t in C/C++)
    frame_packet += struct.pack('<Q', round(time_to_present_frame))
    # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
    for led in range(350):
        frame_packet.append(color[0])
        frame_packet.append(color[1])
        frame_packet.append(color[2])
    return frame_packet


def main():
    print("sending frame sequence to ESPs")

    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    opened_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    opened_socket.settimeout(5)

    color_red = 0
    color_green = 0
    color_blue = 0

    color_to_vary = 0

    master_time_ms = get_current_time_ms()
    print("send master time ({0} ms) broadcast".format(master_time_ms))
    master_time_packet = build_master_time_packet(master_time_ms)
    opened_socket.sendto(master_time_packet, ("<broadcast>", 50000))

    last_send_time_packet_time = master_time_ms

    last_send_frame_packet_time = master_time_ms
    frame_packet_has_been_sent = False

    time_offset = 200

    time_to_present_frame = master_time_ms + time_offset
    print("send first frame presented at time ({0} ms) broadcast".format(time_to_present_frame))

    while True:
        # prepare frame packet
        if color_to_vary == 0:
            color_red += 10
            if color_red > 255:
                color_red = 0
                color_to_vary += 1
        elif color_to_vary == 1:
            color_green += 10
            if color_green > 255:
                color_green = 0
                color_to_vary += 1
        else:
            color_blue += 10
            if color_blue > 255:
                color_blue = 0
                color_to_vary += 1

        if color_to_vary > 2:
            color_to_vary = 0

        color = [color_red, color_green, color_blue]

        frame_packet = build_frame_packet(time_to_present_frame, color)

        if frame_packet_has_been_sent:
            # wait until approx. 40 ms elapsed from last packet has been sent
            wait_time_ms = 40.0 - (get_current_time_ms() - last_send_frame_packet_time)
            if wait_time_ms > 0:
                sleep(wait_time_ms / 1000.0)

        master_time_ms = get_current_time_ms()

        opened_socket.sendto(frame_packet, ("192.168.2.162", 50000))
        opened_socket.sendto(frame_packet, ("192.168.2.164", 50000))
        opened_socket.sendto(frame_packet, ("192.168.2.165", 50000))
        opened_socket.sendto(frame_packet, ("192.168.2.166", 50000))

        frame_packet_has_been_sent = True
        time_to_present_frame = last_send_frame_packet_time + time_offset + 40
        last_send_frame_packet_time = master_time_ms

        if (last_send_frame_packet_time - last_send_time_packet_time) > 2000:
            # send updated master time every approx. 2000ms
            last_send_time_packet_time = last_send_frame_packet_time
            master_time_packet = build_master_time_packet(last_send_time_packet_time)
            opened_socket.sendto(master_time_packet, ("<broadcast>", 50000))


    opened_socket.close()

    print("done")


if __name__ == '__main__':
    main()
