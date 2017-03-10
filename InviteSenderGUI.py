# -*- coding: cp1250 -*-
# Import libraries for GUI
import PyQt4.uic
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QThread

# Import os for managing directories
import os
import sys

# Import library to validate email
from email_validator import validate_email, EmailNotValidError

# Import pdf-gen
import createPDF
import random

# import mailsend2gmail
from send2mail import sendMail

# Import json for reading config
import json

import base64


# Main program
class InviterGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(InviterGui, self).__init__(parent)
        # Read config
        try:
            with open('config', 'r') as f:
                self.config = json.load(f)
            f.close()
        except Exception as e:
            # QtGui.QMessageBox.information("Sporocilo","Missing config, edit Account settings.")
            self.config = {'aserver': "smtp.gmail.com",
                           'aport': 587,
                           'auser': base64.b64encode('your.mail@gmail.com'),
                           'apassword': '',
                           'bcount': 0,
                           'cevent':'RandomEvent Title vol. 1',
                           'cdate':'10.05.2016',
                           'clogo': "logo.jpg",
                           'clocation':'Random Club / Random Location',
                           'dseries': "TEST",
                           'llocation': "Select the path"
                           }
            # self.dlg.leStatus.setText(str(e)+" Making new config file...")

            self.save()

        # Make a worker instance
        self.work = Work()

        # Count sent files
        self.count = self.config['bcount']
        self.count_th = 0
        self.unsent = 0

        # Load GUI file
        self.dlg = PyQt4.uic.loadUi("guiv3.ui")
        # Connect buttons
        QObject.connect(self.dlg.btSend, SIGNAL("clicked()"), self.get_one_mail)
        QObject.connect(self.dlg.btSave, SIGNAL("clicked()"), self.save_conf)
        QObject.connect(self.dlg.btSavePDF, SIGNAL("clicked()"), self.save_pdf_content)
        QObject.connect(self.dlg.btPath, SIGNAL("clicked()"), self.set_path)
        QObject.connect(self.work, SIGNAL("threadDone(QString)"), self.update_status)
        QObject.connect(self.work, SIGNAL("count"), self.count_thr)
        # Set text from config
        # Set text for Settings tab
        self.dlg.leLogin.setText(self.config['auser'])
        self.dlg.leServer.setText(self.config['aserver'])
        self.dlg.lePort.setText(str(self.config['aport']))
        self.dlg.lePath.setText(self.config['llocation'])
        # Set text for PDF content tab
        self.dlg.leEvent.setText(self.config['cevent'])
        self.dlg.leDate.setText(self.config['cdate'])
        self.dlg.leLocation.setText(self.config['clocation'])

        self.dlg.leCount.display(self.count)

        # Show GUI
        self.dlg.show()

    # Update progress bar
    def update_status(self, text):
        # Set text
        self.dlg.leStatus.setText(text)
        # Apply changes to GUI
        QtGui.QApplication.processEvents()

    # Set Unique code generator log file
    def set_path(self):
        self.config['llocation'] = str(QtGui.QFileDialog.getSaveFileName(self, 'Save File', '', "Text (*.txt)"))
        try:
            self.save()
            l = open(self.config['llocation'], "w")
            l.close()
            self.dlg.lePath.setText(self.config['llocation'])
        except:
            self.update_status("!You haven't set the path !")

    # Count events
    def count_thr(self):
        self.count_th += 1
        QtGui.QApplication.processEvents()

    # Get mails, generate pdf for each and send it
    def get_one_mail(self):
        self.dlg.progressBar.setValue(0)
        if os.path.exists(self.config['llocation']):
            mails_str = str(self.dlg.leEmails.toPlainText())
            mails_str = mails_str.replace(" ", "")
            mails = mails_str.split(",")
            self.dlg.progressBar.setMaximum(len(mails) * 3)
            self.count = 0
            for mail in mails:
                try:
                    v = validate_email(mail)  # validate and get info
                    mail = v["email"]  # replace with normalized form
                    self.update_status(mail)
                    # self.config['server'], self.config['port'],
                    #                   self.config['user'], self.config['password']

                    w = self.work.send(self.config['aserver'],
                                       self.config['aport'],
                                       self.config['auser'],
                                       base64.b64decode(self.config['apassword']),
                                       mail,
                                       str(self.dlg.leSubject.text()),
                                       str(self.dlg.leBody.toPlainText()),
                                       self.config['clogo'],
                                       self.config['cevent'],
                                       self.config['cdate'],
                                       self.config['clocation'],
                                       self.config['dseries'],
                                       self.config['llocation'])
                    if "Error" in w:
                        self.unsent += 1
                        self.count_th += 1
                    else:
                        self.count += 1

                except EmailNotValidError as e:
                    self.unsent += 1
                    self.count_th += 3
                    # email is not valid, exception message is human-readable
                    self.update_status((str(e)) + mail)

                self.dlg.leCount.display(self.count)
                self.dlg.progressBar.setValue(self.count_th)
                #int(self.count) + int(self.unsent)
                QtGui.QApplication.processEvents()
            self.config['bcount'] = int(self.count) + int(self.config['bcount']) - int(self.unsent)
            self.save()
        else:
            self.update_status("Invalid path to store UNIQE CODES, check Settings...")

    # Save settings from PDF content tab
    def save_pdf_content(self):
        self.config['cevent'] = str(self.dlg.leEvent.text())
        self.config['cdate'] = str(self.dlg.leDate.text())
        self.config['clocation'] = str(self.dlg.leLocation.text())
        self.save()

    # Save data from Settings tab
    def save_conf(self):
        self.config['auser'] = str(self.dlg.leLogin.text())
        self.config['aserver'] = str(self.dlg.leServer.text())
        self.config['aport'] = int(self.dlg.lePort.text())
        if self.config['apassword'] != base64.b64encode(str(self.dlg.lePasswd.text())):
            self.config['apassword'] = base64.b64encode(str(self.dlg.lePasswd.text()))
        self.config['llocation'] = str(self.dlg.lePath.text())
        self.save()

    # Save config
    def save(self):
        with open('config', 'w') as f:
            json.dump(self.config, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()


# Threading class
class Work(QThread):  # multithread
    def __init__(self, parent=None):
        super(Work, self).__init__(parent)
        self.pathname, self.scriptname = os.path.split(sys.argv[0])
        with open('config', 'r') as f:
            self.config = json.load(f)

    def generate_number(self):
        # returning edited string number
        return str(random.random())[2:8]

    def send(self, server, port, user, passwd, send_to, subject, body, logo, event, date, location, series, logFile):
        # self.dlg.progressBar.setValue(100)
        unumber = self.generate_number()
        f = open(logFile, 'r')
        line = str(series + "-" + unumber[:2] + "-" + unumber[2:4] + "-" + unumber[4:])
        if line not in f:
            fa = open(logFile, 'a')
            fa.write(series + "-" + unumber[:2] + "-" + unumber[2:4] + "-" + unumber[4:] + "\n")
            if not os.path.exists(os.path.join(os.getcwd(), series)):
                os.makedirs(os.path.join(os.getcwd(), series))
            file = os.path.join(series, "Invitation_" + event + "_" + series + "_" + str(unumber) + ".pdf")
            self.emit(SIGNAL("threadDone(QString)"), "Creating PDF")
            self.emit(SIGNAL("count"))
            createPDF.createPDF(logo, event, date, location, series, unumber, file)
            self.emit(SIGNAL("threadDone(QString)"), "Sending to mail "+send_to)
            self.emit(SIGNAL("count"))
            p = sendMail(server, port, user, passwd,
                         send_to, subject, str(body),
                         file)
            self.emit(SIGNAL("threadDone(QString)"), p)
            self.emit(SIGNAL("count"))
            return p
        f.close()

app = QtGui.QApplication(sys.argv)
top = InviterGui()
app.exec_()
