#database related information
mysqlUsr = ""
mysqlPass = ""
host = ""
database = ""

#test server ip address
#serverIP = '127.0.0.1'          #localhost test
#serverIP = '192.168.0.14'       #lan test
serverIP = '35.226.148.30'       #google szerver

#linux specific launch information
#terminal = '' #'sudo gnome-terminal -- '
terminal = 'sudo xterm -hold -e ' #+ '/bin/bash -c '
master = '/dev/ttyACM0'


#windows specific launch information (at home test)
'''
terminal = 'start cmd /c '
master = 'COM6'
'''
