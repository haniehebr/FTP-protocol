import socket
import sys
import os
import struct

TCP_IP = "127.0.0.1" # Only a local server
TCP_PORT = 2121 # Just a random choice
BUFFER_SIZE = 1024
FORMAT = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Connection():
    print("Sending server request...")
    try:
        s.connect((TCP_IP, TCP_PORT))
        print("Connection successful\n")
        print("welcome to the FTP client :)\n")
    except:
           print("Connection unsuccessful. Make sure the server is online.")

def Help():
    try:
        val = "HELP"
        s.send(val.encode(FORMAT))
        data = s.recv(BUFFER_SIZE)
        print(data.decode(FORMAT))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return

def List_files():
    print("Requesting files...\n")
    try:
        val = "LIST"
        s.send(val.encode(FORMAT))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # First get the number of files in the directory
        number_of_files = struct.unpack("i", s.recv(4))[0]
        # Then enter into a loop to recieve details of each, one by one
        print("\t..")
        for i in range(int(number_of_files)):
            # Get the file name size first to slightly lessen amount transferred over socket
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size)
            # Also get the file size for each item in the server
            file_size = struct.unpack("i", s.recv(4))[0]
            is_dir = s.recv(BUFFER_SIZE)
            if is_dir.decode(FORMAT) == "is dir":
                print(">\t{} - {}b".format(file_name.decode(FORMAT), file_size))
            else:
                print("\t{} - {}b".format(file_name.decode(FORMAT), file_size))
            # Make sure that the client and server are syncronised
            val = "1"
            s.send(val.encode(FORMAT))
        # Get total size of directory
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print("Total directory size: {}b".format(total_directory_size))
    except:
        print("Couldn't retrieve listing")
        return
    try:
        # Final check
        val = "1"
        s.send(val.encode(FORMAT))
        return
    except:
        print("Couldn't get final server confirmation")
        return

def Pwd():
    print("Requesting path...\n")
    try:
        val = "PWD"
        s.send(val.encode(FORMAT))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return

    try:
        last_dir = s.recv(BUFFER_SIZE)
        print("\t/{}".format(last_dir.decode(FORMAT)))
    except:
        print("Couldn't retrieve path")
        return
    try:
        # Final check
        val = "1"
        s.send(val.encode(FORMAT))
        return
    except:
        print("Couldn't get final server confirmation")
        return

def Cd(dir_name):
    print("Changing dir to {}...".format(dir_name))
    try:
        val = "CD"
        s.send(val.encode(FORMAT))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        s.send(struct.pack("h", sys.getsizeof(dir_name)))
        s.send(dir_name.encode(FORMAT))
        # Get file size (if exists)
        dir_size = struct.unpack("i", s.recv(4))[0]
        if dir_size == -1:
            # If file size is -1, the file does not exist
            print("File does not exist. Make sure the name was entered correctly")
            return
    except:
        print("Error checking file")

    try:
        # Send ok to recieve file content
        val = "1"
        s.send(val.encode(FORMAT))
        path_ = s.recv(BUFFER_SIZE)
        path = path_.decode(FORMAT)
        print("\t/{}".format(dir_name))
    except:
        print("Error changing dir")
        return
    val = "1"
    s.send(val.encode(FORMAT))
    return

def Dwld(file_name):
    # Download given file
    print("Downloading file: {}".format(file_name))
    try:
        # Send server request
        val = "DWLD"
        s.send(val.encode(FORMAT))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode(FORMAT))
        # Get file size (if exists)
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            # If file size is -1, the file does not exist
            print("File does not exist. Make sure the name was entered correctly")
            return
    except:
        print("Error checking file")
    try:
        # Send ok to recieve file content
        val = "1"
        s.send(val.encode(FORMAT))
        # Enter loop to recieve file
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print("\nDownloading...")
        while bytes_recieved < file_size:
            # Again, file broken into chunks defined by the BUFFER_SIZE variable
            data1 = s.recv(BUFFER_SIZE)
            print(data1.decode(FORMAT))
            output_file.write(data1)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print("Successfully downloaded {}".format(file_name))
        # Tell the server that the client is ready to recieve the download performance details
        val = "1"
        s.send(val.encode(FORMAT))
        # Get performance details
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print("Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size))
    except:
        print("Error downloading file")
        return
    return

def Quit():
    val = "QUIT"
    s.send(val.encode(FORMAT))
    # Wait for server go-ahead
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    return

# Main

Connection()
data = s.recv(BUFFER_SIZE)
print(data.decode(FORMAT))
while True:
    # Listen for a command
    prompt = input("\nEnter a command: ")
    if prompt[:4].upper() == "HELP":
        Help()
    elif prompt[:4].upper() == "LIST":
        List_files()
    elif prompt[:3].upper() == "PWD":
        Pwd()
    elif prompt[:2].upper() == "CD":
        Cd(prompt[3:])
    elif prompt[:4].upper() == "DWLD":
        Dwld(prompt[5:])
    elif prompt[:4].upper() == "QUIT":
        Quit()
        break
    else:
        print("Command not recognised; please try again")
