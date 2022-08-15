import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from ping3 import ping

from SSHLibrary import SSHLibrary
from functools import partial

class MainWindow(qtw.QWidget):
    def __init__(self):
        """
        Main Window Constructor
        """
        super().__init__()
        self.pi = [
            '192.168.64.4',
            '192.168.10.101',
            '192.168.10.102',
            '192.168.10.103'
        ]


        # robotframework ssh library
        self.ssh = SSHLibrary()
        
        self.username = 'sage'
        self.password = 'wilder'
        # username = 'ubuntu'
        # password = 'raspberry'

        self.number_of_pi = len(self.pi)

        # setup rows of the UI
        self.setup_ip_labels()
        self.setup_alive_labels()
        self.setup_poweroff_buttons()
        self.setup_mavproxy_buttons()

        title_line = qtw.QLabel('<h3>ANT Colony Rasperry Pi Utility</h3>')

        window = qtw.QWidget(self)
        window.setWindowFlags(qtc.Qt.Sheet | qtc.Qt.Popup)

        
        # setting layout
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(title_line)

        grid_layout = qtw.QGridLayout()
        grid_layout.setSpacing(10)
        
        # columns
        ip_column = qtw.QLabel('<b><font color="red">| IP </font></b>')
        ping_column = qtw.QLabel('<b><font color="red">| WiFi </font></b>')
        shutdown_column = qtw.QLabel('<b><font color="red">| Shutdown </font></b>')
        mavproxy_column = qtw.QLabel('<b><font color="red">| Mavproxy </font></b>')
        
        grid_layout.addWidget(ip_column, 0, 0)
        grid_layout.addWidget(ping_column, 0, 1)
        grid_layout.addWidget(shutdown_column, 0, 2)
        grid_layout.addWidget(mavproxy_column, 0, 3)

        layout.addLayout(grid_layout)


        # bottom buttons
        self.refresh_button = qtw.QPushButton('Refresh Status', self)
        self.refresh_button.clicked.connect(self.update_alive_labels)
        self.shutdown_all_button = qtw.QPushButton('Shutdown All', self)
        ## shutdown_all button to be implemented later

        refresh_button_layout = qtw.QHBoxLayout()
        refresh_button_layout.addWidget(self.refresh_button)
        refresh_button_layout.addWidget(self.shutdown_all_button)

        layout.addLayout(refresh_button_layout)



        for id in range(self.number_of_pi):
            grid_layout.addWidget(self.ip_labels[id], id+1, 0)
            self.ip_labels[id].setStyleSheet("background-color: white; inset grey;")
            self.ip_labels[id].setFrameShape(qtw.QFrame.Panel)


        for id in range(self.number_of_pi):
            grid_layout.addWidget(self.alive_labels[id], id+1, 1)

        for id in range(self.number_of_pi):
            grid_layout.addWidget(self.poweroff_buttons[id], id+1, 2)

        for id in range(self.number_of_pi):
            grid_layout.addWidget(self.mavproxy_buttons[id], id+1, 3)
        

        self.show()

    def setup_ip_labels(self):
        self.ip_labels = ['L_IP_'+str(idx) for idx in range(self.number_of_pi)]

        for id in range(self.number_of_pi):
            self.ip_labels[id] = qtw.QLabel(self)
            self.ip_labels[id].setText(self.pi[id])
    
    def setup_alive_labels(self):
        self.alive_labels = ['L_ALIVE_'+str(idx) for idx in range(self.number_of_pi)]

        for id in range(self.number_of_pi):
            self.alive_labels[id] = qtw.QLabel(self)
            self.alive_labels[id].setText("=")

    
    def update_alive_labels(self):
        for id, label in enumerate(self.alive_labels):
            label.setText(self.alive(self.pi[id]))

    def alive(self, ip):
        if (ping(ip)):
            return '✅'
        else:
            return '❌'

    def sudo_shutdown(self, ip):
        print('sudo shutdown accessed ...........')
        print(ip)

        self.ssh.open_connection(ip)
        self.ssh.login(self.username, self.password)
        self.ssh.start_command('sudo touch hello.txt', sudo=True, sudo_password=password)
        # ssh.start_command('sudo poweroff', sudo=True, sudo_password=password)
        self.ssh.close_connection()

        print('connection closed')

    def check_mavproxy_service(self, ip, id):
        print('mavproxy service checker function accessed.. IP: ', ip)
        self.ssh.open_connection(ip)
        self.ssh.login(self.username, self.password)
        string = self.ssh.execute_command("systemctl status sshd")
        if ("running" in string):
            print("mavproxy is running")
            self.mavproxy_buttons[id].setText('Check ✅')
        else:
            print("mavproxy is not running")
            self.mavproxy_buttons[id].setText('Check ❌')

        self.ssh.close_connection()



    def setup_mavproxy_buttons(self):
        self.mavproxy_buttons = ['Mav_'+str(idx) for idx in range(self.number_of_pi)]

        for id in range(self.number_of_pi):
            self.mavproxy_buttons[id] = qtw.QPushButton('Check', self)
            remote_ip = self.pi[id]
            self.mavproxy_buttons[id].clicked.connect(partial(self.check_mavproxy_service, remote_ip, id))

    def setup_poweroff_buttons(self):
        self.poweroff_buttons = ['P_Button_'+str(idx) for idx in range(self.number_of_pi)]

        for id in range(self.number_of_pi):
            self.poweroff_buttons[id] = qtw.QPushButton('Shutdown', self)
            remote_ip = self.pi[id]
            self.poweroff_buttons[id].clicked.connect(partial(self.sudo_shutdown, remote_ip))
            



if __name__=='__main__':
    app = qtw.QApplication(sys.argv)

    mw = MainWindow()

    sys.exit(app.exec())
