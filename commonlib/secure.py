#database related information
mysqlUsr = ""
mysqlPass = ""
host = ""
database = ""

#test server ip address
#serverIP = '127.0.0.1'        #localhost test
#serverIP = '192.168.0.14'     #lan test
serverIP = '35.226.148.30'     #google szerver test

#linux specific launch information
#terminal = 'gnome-terminal -- '
terminal = '/usr/bin/python3 '  #background process doesn't need terminal, but needs full python path
mavproxypath = ''               #add full path of mavproxy.py after the last space with / at the end
master = 'ttyACM0'

#windows specific launch information
'''
terminal = 'start cmd /c '
master = 'COM6'
'''