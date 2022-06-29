import socket
import sys
import time
import os
import struct

print("\nWelcome to the FTP server.\n")

# Initialise socket stuff
TCP_IP = "127.0.0.1"
TCP_PORT = 2121
BUFFER_SIZE = 1024
FORMAT = "utf-8"

path = "C:/Users/Padidar/Desktop/9917663_prog1/Source/Server"
path_arr = os.getcwd().split('\\')

msg = "Call one of the following function:\n" \
      "HELP           : Show this help\n" \
      "LIST           : List files\n" \
      "PWD            : Show current dir\n" \
      "CD dir_name    : Change directory\n" \
      "DWLD file_path : Download file\n" \
      "QUIT           : Exit"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("To get started, connect a client.")
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print(f"Server listening on 0.0.0.0:{TCP_PORT}\n")
    conn, addr = s.accept()
    print(f"Connected to by address: {addr}\n")
    conn.send(msg.encode(FORMAT))

def Help():
    print("Received instruction: HELP")
    conn.send(msg.encode(FORMAT))
    print("successfully sent HELP\n")

def List_files():
    print("Received instruction: LIST")
    print("Listing files...")
    # Get list of files in directory
    listing = os.listdir(os.getcwd())
    # Send over the number of files, so the client knows what to expect (and avoid some errors)
    conn.send(struct.pack("i", len(listing)))
    total_directory_size = 0
    # Send over the file names and sizes whilst totaling the directory size
    for i in listing:
        # File name size
        conn.send(struct.pack("i", sys.getsizeof(i)))
        # File name
        conn.send(i.encode(FORMAT))
        # File content size
        conn.send(struct.pack("i", os.path.getsize(i)))
        if os.path.isdir(i) == True:
            data = "is dir"
            conn.send(data.encode(FORMAT))
        else:
            data = "is not dir"
            conn.send(data.encode(FORMAT))
        total_directory_size += os.path.getsize(i)
        # Make sure that the client and server are syncronised
        conn.recv(BUFFER_SIZE)
    # Sum of file sizes in directory
    conn.send(struct.pack("i", total_directory_size))
    # Final check
    conn.recv(BUFFER_SIZE)
    print("Successfully sent file listing")
    return

def Pwd():
    print("Received instruction: PWD")
    print("Pwd...")
    path_arr = os.getcwd().split('\\')
    size_array = len(path_arr)
    last_dir = path_arr[size_array - 1]
    print(last_dir)
    conn.send(last_dir.encode(FORMAT))
    # Final check
    conn.recv(BUFFER_SIZE)
    print("Successfully sent file listing")
    return

def Cd():
    print("Received instruction: CD")
    val = "1"
    conn.send(val.encode(FORMAT))
    dir_name_length = struct.unpack("h", conn.recv(2))[0]
    # print(dir_name_length)
    dir_name = conn.recv(dir_name_length)
    # print(dir_name.decode(FORMAT))
    print("cur dir set to:\n\tfile/{}".format(dir_name.decode(FORMAT)))
    count = 0
    listing = os.listdir(os.getcwd())
    for i in listing:
        if i == dir_name.decode(FORMAT):
            # if os.path.isfile(file_name.decode(FORMAT)):
            # Then the file exists, and send file size
            conn.send(struct.pack("i", sys.getsizeof(i)))
            break
        count = count + 1
        if count == len(listing) and dir_name.decode(FORMAT)[0] != ".":
            print(dir_name[0])
            # Then the file doesn't exist, and send error code
            print("File name not valid")
            conn.send(struct.pack("i", -1))
            return
    # Wait for ok to send file
    conn.recv(BUFFER_SIZE)
    print(dir_name.decode(FORMAT))
    if dir_name.decode(FORMAT)[0] != ".":
        os.chdir(path + "/" + dir_name.decode(FORMAT))
        path_arr.append(dir_name)
        conn.send(os.getcwd().encode(FORMAT))
    else:
        size_array = len(path_arr)
        path_ = ""
        print(size_array - dir_name_length)
        counter = (size_array - dir_name_length)
        while counter >= 0:
            path_ += "/" + path_arr[i]
            counter = counter - 1
        print(path_)
        os.chdir(path_)
        conn.send(os.getcwd().encode(FORMAT))

    conn.recv(BUFFER_SIZE)
    return

def Dwld():
    print("Received instruction: DWLD")
    val = "1"
    conn.send(val.encode(FORMAT))
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    print(file_name_length)
    file_name = conn.recv(file_name_length)
    print(file_name.decode(FORMAT))
    count = 0
    listing = os.listdir(os.getcwd())
    for i in listing:
        if i == file_name.decode(FORMAT):
            # if os.path.isfile(file_name.decode(FORMAT)):
            # Then the file exists, and send file size
            conn.send(struct.pack("i", sys.getsizeof(i)))
            break
        count = count + 1
        if count == len(listing):
            # Then the file doesn't exist, and send error code
            print("File name not valid")
            conn.send(struct.pack("i", -1))
            return
    # Wait for ok to send file
    conn.recv(BUFFER_SIZE)
    # Enter loop to send file
    start_time = time.time()
    print("Sending file...")
    content = open(file_name, "rb")
    # Again, break into chunks defined by BUFFER_SIZE
    data1 = content.read(BUFFER_SIZE)
    while data1:
        conn.send(data1)
        data1 = content.read(BUFFER_SIZE)
    content.close()
    # Get client go-ahead, then send download details
    conn.recv(BUFFER_SIZE)
    conn.send(struct.pack("f", time.time() - start_time))
    return

def Quit():
    print("Received instruction: QUIT")
    # Send quit conformation
    val = "1"
    conn.send(val.encode(FORMAT))
    # Close and restart the server
    print("Client connection ended")
    conn.close()
    s.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

while True:
    # Enter into a while loop to recieve commands from client
    print("\nWaiting for instruction\n")
    data = conn.recv(BUFFER_SIZE)
    # Check the command and respond correctly
    if data.decode(FORMAT) == "HELP":
        Help()
    elif data.decode(FORMAT) == "LIST":
        List_files()
    elif data.decode(FORMAT) == "PWD":
        Pwd()
    elif data.decode(FORMAT) == "CD":
        Cd()
    elif data.decode(FORMAT) == "DWLD":
        Dwld()
    elif data.decode(FORMAT) == "QUIT":
        Quit()
    # Reset the data to loop
    data = None
