import socket as PythonSocket
import packet as MyPacket
import sys
import os

def args_parse():
  if (len(sys.argv) != 5):
    print("4 required arguments.")
    sys.exit()

  try:
    emulator_name = sys.argv[1]
    ack_port = int(sys.argv[2])
    data_port = int(sys.argv[3])
    file_name = sys.argv[4]
  except:
    print("argument parsing unsuccessful")
    sys.exit()

  return emulator_name, ack_port, data_port, file_name

# Command line inputs in the order:
# 1. <hostname for the network emulator>
# 2. <UDP port number used by the link emulator to receive ACKs from the receiver>
# 3. <UDP port number used by the receiver to receive data from the emulator>
# 4. <name of the file into which the received data is written>
EMULATOR_NAME, ACK_PORT, DATA_PORT, FILE_NAME = args_parse()

SEQ_NUM_MODULO = 32

def main():
  # Clean up the log file from last execution
  try:
    os.remove('arrival.log')
    os.remove(FILE_NAME)
  except:
    pass

  data_sock, ack_sock = establish_connection()
  communicate(data_sock, ack_sock)

  ack_sock.close()
  data_sock.close()
  return


def establish_connection():
  # Data connection
  data_sock = PythonSocket.socket(PythonSocket.AF_INET, PythonSocket.SOCK_DGRAM)
  data_sock.bind(('', DATA_PORT))
  # ACK connection
  ack_sock = PythonSocket.socket(PythonSocket.AF_INET, PythonSocket.SOCK_DGRAM)
  ack_sock.bind(('', 0))

  return data_sock, ack_sock


def communicate(data_sock, ack_sock):
  exp_seq_num = 0
  while True:
    # data arrived
    udp_array, addr = data_sock.recvfrom(512)

    # parse bytes array into packet
    udp_packet = MyPacket.packet.parse_udp_data(udp_array)
    packet_type, seq_num, data = udp_packet.type, udp_packet.seq_num, udp_packet.data

    if packet_type == 1:
      log_seq_num(seq_num)
      # sequence number matches
      if exp_seq_num == seq_num:
        record_data(data)

        # send an ACK back with the same sequence number
        ack_packet = MyPacket.packet(0, seq_num, '').get_udp_data()
        ack_sock.sendmsg([ack_packet], [], 0, (EMULATOR_NAME, ACK_PORT))

        # increment and modulo expected sequence number
        exp_seq_num = (exp_seq_num + 1) % SEQ_NUM_MODULO   
      
      else:
        # send an ACK back with the sequence number equal to most recently received in-order packet
        ack_packet = MyPacket.packet(0, exp_seq_num - 1, '').get_udp_data()
        ack_sock.sendmsg([ack_packet], [], 0, (EMULATOR_NAME, ACK_PORT))

    # receive EOT, then send back EOT then exit
    if packet_type == 2:
      eot_packet = MyPacket.packet(2, exp_seq_num, '').get_udp_data()
      ack_sock.sendmsg([eot_packet], [], 0, (EMULATOR_NAME, ACK_PORT))
      return


def log_seq_num(seq_num):
  f = open("arrival.log", "a+")
  f.write(f'{seq_num}\r\n')
  f.close() 


def record_data(data):
  f = open(FILE_NAME, "a+")
  f.write(f'{data}')
  f.close() 


if __name__ == "__main__":
    main()
