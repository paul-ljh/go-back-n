import socket as PythonSocket
import packet as MyPacket
import sys
import threading
import time
import os

def args_parse():
  if (len(sys.argv) != 5):
    print("4 required arguments.")
    sys.exit()

  try:
    emulator_name = sys.argv[1]
    data_port = int(sys.argv[2])
    ack_port = int(sys.argv[3])
    file_name = sys.argv[4]
  except:
    print("argument parsing unsuccessful")
    sys.exit()

  return emulator_name, data_port, ack_port, file_name

# Command line inputs in the order:
# 1. <hostname for the network emulator>
# 2. <UDP port number used by the emulator to receive data from the sender>
# 3. <UDP port number used by the sender to receive ACKs from the emulator>
# 4. <name of the file to be transferred>
EMULATOR_NAME, DATA_PORT, ACK_PORT, FILE_NAME = args_parse()

WINDOW_SIZE = 10
SEQ_NUM_MODULO = 32
MAX_DATA_LENGTH = 500

base = 0
next_seq_num = 0

pkt_array = [None] * SEQ_NUM_MODULO # array for packets
file_last_position = 0 # the last-read file position
timer = False
lock = threading.Lock()
receieved_all_acks = False
finished_reading = False

def main():
  global timer
  try:
    # Clean up the log file from last execution
    os.remove('seqnum.log')
    os.remove('ack.log')
  except:
    pass

  data_sock, ack_sock = establish_connection()

  pkt_sender_thread = PacketSenderThread(data_sock)
  ack_receiver_thead = AckReceiverThread(data_sock, ack_sock)

  pkt_sender_thread.start()
  ack_receiver_thead.start()


class PacketSenderThread(threading.Thread):
  def __init__(self, data_sock):
    threading.Thread.__init__(self)
    self.data_sock = data_sock

  def is_it_in_window(self):
    maximum_num = (base + WINDOW_SIZE - 1) % SEQ_NUM_MODULO
    if base > SEQ_NUM_MODULO - WINDOW_SIZE:
      return (next_seq_num >= base) or (next_seq_num <= maximum_num)
    else:
      return (next_seq_num >= base) and (next_seq_num <= maximum_num)

  def is_timed_out(self):
    return current_milli_time() - timer >= 100

  def log_seqence(self, num):
    f = open("seqnum.log","a+")
    f.write(f'{num}\n')
    f.close()

  def send_packet(self, index):
    if pkt_array[index] != 'EOT':
      self.log_seqence(index)
      self.data_sock.sendto(pkt_array[index], (EMULATOR_NAME, DATA_PORT))

  def resend_packets(self):
    if base > next_seq_num:
      for seq_num in range(base, SEQ_NUM_MODULO):
        self.send_packet(seq_num)
      for seq_num in range(0, next_seq_num):
        self.send_packet(seq_num)
    else:
      for seq_num in range(base, next_seq_num):
        self.send_packet(seq_num)

  def packet_handler(self):
    global file_last_position, finished_reading, pkt_array
    # restore last read position, read, then update last read position
    f = open(FILE_NAME, "r")
    f.seek(file_last_position)
    data = f.read(MAX_DATA_LENGTH)
    file_last_position = f.tell()
    f.close()

    # have read entire file
    if data == "":
      pkt_array[next_seq_num] = "EOT"
      finished_reading = True

    else:
      pkt_array[next_seq_num] = MyPacket.packet(1, next_seq_num, data).get_udp_data()
      self.send_packet(next_seq_num)

  def run(self):
    global next_seq_num, timer

    while True:
      lock.acquire()

      # Exit sender
      if receieved_all_acks:
        lock.release()
        break
      
      # have data to send
      if finished_reading == False and self.is_it_in_window():
        self.packet_handler()
        # start timer if it was stopped
        if timer == False:
          timer = current_milli_time()
        # advance next sequence number
        next_seq_num = (next_seq_num + 1) % SEQ_NUM_MODULO

      if timer and self.is_timed_out():
        timer = current_milli_time()
        self.resend_packets()
      
      lock.release()


class AckReceiverThread(threading.Thread):
  def __init__(self, data_sock, ack_sock):
    threading.Thread.__init__(self)
    self.data_sock = data_sock
    self.ack_sock = ack_sock

  def log_ack(self, seq_num):
    f = open("ack.log", "a+")
    f.write(f'{seq_num}\n')
    f.close()

  def run(self):
    global base, next_seq_num, timer, pkt_array, receieved_all_acks

    while True:
      # parse UDP bytes array into UDP packet
      udp_array = self.ack_sock.recv(12)
      udp_packet = MyPacket.packet.parse_udp_data(udp_array)
      packet_type, seq_num, data = udp_packet.type, udp_packet.seq_num, udp_packet.data

      lock.acquire()
      # EOT
      if packet_type == 2:
        self.ack_sock.close()
        lock.release()
        break

      # ACK
      if packet_type == 0:
        self.log_ack(seq_num)
        # if seq_num is bigger or equal to than the expected one
        if seq_num >= base:
          base = (seq_num + 1) % SEQ_NUM_MODULO

          # last ACK to receive
          if pkt_array[base] == "EOT":
            receieved_all_acks = True
            pkt = MyPacket.packet(2, base, "").get_udp_data()
            self.data_sock.sendto(pkt, (EMULATOR_NAME, DATA_PORT))
            # EOT won't be lost, therfore close data socket
            self.data_sock.close()

          # more ACKs to receive
          else:
            if base == next_seq_num:
              # no outstanding packets, stop timer
              timer = False
            else:
              # oustanding packets, restart timer
              timer = current_milli_time()
        lock.release()


def current_milli_time():
  return int(round(time.time() * 1000))

def establish_connection():
  ack_sock = PythonSocket.socket(PythonSocket.AF_INET, PythonSocket.SOCK_DGRAM)
  ack_sock.bind(('', ACK_PORT))
  data_sock = PythonSocket.socket(PythonSocket.AF_INET, PythonSocket.SOCK_DGRAM)

  return data_sock, ack_sock

if __name__ == "__main__":
    main()
