import socket
import time
import struct


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
    print("sending frame to ESPs")

    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    opened_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    opened_socket.settimeout(5)

    master_time_ms = get_current_time_ms()
    print("send master time ({0} ms) broadcast".format(master_time_ms))
    master_time_packet = build_master_time_packet(master_time_ms)
    opened_socket.sendto(master_time_packet, ("<broadcast>", 50000))

    time_to_present_frame = master_time_ms + 200
    print("send frame presented at time ({0} ms) broadcast".format(time_to_present_frame))
    color = [0, 0, 0] # all LEDs black
    # color = [255, 255, 255] # all LEDs white
    frame_packet = build_frame_packet(time_to_present_frame, color)
    opened_socket.sendto(frame_packet, ("192.168.2.162", 50000))
    opened_socket.sendto(frame_packet, ("192.168.2.164", 50000))
    opened_socket.sendto(frame_packet, ("192.168.2.165", 50000))
    opened_socket.sendto(frame_packet, ("192.168.2.166", 50000))

    opened_socket.close()

    print("done")


if __name__ == '__main__':
    main()
