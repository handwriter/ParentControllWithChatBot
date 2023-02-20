import sys
import os
import signal
import psutil
import subprocess
import win32gui
import requests
import win32process
import threading
import wmi
from scapy.all import *
import socket
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify
import tkinter as tk
# from PyQt5.QtCore import *
# from PyQt5.QtGui import QMouseEvent, QCursor
# from PyQt5.QtWidgets import *
import webbrowser
import json
# from PyQt5.QtWebEngineWidgets import *
from pathlib import Path
from multiprocessing import Process, Queue
import sys


class Config:
    data = {} # type: dict
    def __init__(self, fp, filename):
        self.filepath = os.path.join(fp, filename)
        if not Path(self.filepath).exists():
            with open(self.filepath, 'w') as doc:
                doc.write("{}")
        else:
            try:
                with open(self.filepath, 'r') as doc:
                    self.data = json.load(doc)
            except:
                with open(self.filepath, 'w') as doc:
                    doc.write("{}")

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        return None

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save_data()

    def __contains__(self, key):
        return key in self.data

    def save_data(self):
        with open(self.filepath, 'w') as doc:
            json.dump(self.data, doc)

def process_banned_hostnames(hosts):
    return [socket.gethostbyname(i) for i in hosts]


CONFIG_FILEPATH = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents', "Control Settings\\")

if not Path(CONFIG_FILEPATH).exists():
    os.mkdir(CONFIG_FILEPATH)
CONFIG = Config(CONFIG_FILEPATH, "config.json")


c = wmi.WMI()
SERVER_ADDRESS = "http://194.87.253.133:689/"
BANNED_APPS = {}
if "banned_apps" in CONFIG:
    for i in CONFIG["banned_apps"]:
        BANNED_APPS[i] = 0

BANNED_HOSTNAMES = []

if "banned_sites" in CONFIG:
    BANNED_HOSTNAMES = CONFIG["banned_sites"]

if "screen_access" not in CONFIG:
    CONFIG["screen_access"] = False

if "statistics_access" not in CONFIG:
    CONFIG["statistics_access"] = False


BANNED_IP = process_banned_hostnames(BANNED_HOSTNAMES)
print(BANNED_IP)
IP_BAN_HISTORY = {}




def server_url(page: str):
    return SERVER_ADDRESS + page

def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe


def get_app_id(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return int(pid)
    except:
        return None

# class CustomQWebView(QWebEngineView):
#     def mousePressEvent(self, a0: QMouseEvent) -> None:
#         print(a0.button())

# class MainWindow(QMainWindow):
#
#     # constructor
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#         # creating a QWebEngineView
#         self.browser = CustomQWebView()
#
#         # setting default browser url as google
#         self.browser.setUrl(QUrl("http://127.0.0.1:5000"))
#
#         # adding action when url get changed
#
#         # adding action when loading is finished
#         self.browser.loadFinished.connect(self.update_title)
#
#         # set this browser as central widget or main window
#         self.setCentralWidget(self.browser)
#         self.setFixedSize(1200, 800)
#
#     def update_title(self):
#         self.show()

def center_window(root, width=300, height=200, x=500, y=500):
    # get screen width and height
    # screen_width = root.winfo_screenwidth()
    # screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    # x = (screen_width/2) - (width/2)
    # y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def check_ip(cap: Packet):
    global BANNED_IP
    if CONFIG["banned_sites"] is None: return
    if len(BANNED_IP) != len(CONFIG["banned_sites"]):
        BANNED_IP = process_banned_hostnames(CONFIG["banned_sites"])
    dst = cap.sprintf("{IP:%IP.dst%}")
    if dst in BANNED_IP:
        if dst not in IP_BAN_HISTORY:
            IP_BAN_HISTORY[dst] = 0
        if datetime.now().timestamp() - IP_BAN_HISTORY[dst] > 3600:
            IP_BAN_HISTORY[dst] = datetime.now().timestamp()
            requests.get(server_url("banned_site_report"), params={"chat_id": CONFIG["chat_id"], "name": BANNED_HOSTNAMES[BANNED_IP.index(dst)]})
            print(f"BANNNED - {BANNED_HOSTNAMES[BANNED_IP.index(dst)]}")


def winEnumHandler(hwnd, win_list):
    title = win32gui.GetWindowText(hwnd)

    if win32gui.IsWindowVisible(hwnd) and title != "":
        win_list.append((hwnd, title))

def controlBannedApps():
    while True:
        windows = []
        win32gui.EnumWindows(winEnumHandler, windows)
        # if config_ref.isMoveWindow:
        #     cur = QCursor()
        #     config_ref.qmainwindow.setGeometry(config_ref.startWindowX + (cur.pos().x() - config_ref.startMouseX),
        #                                        config_ref.startWindowY + (cur.pos().y() - config_ref.startMouseY))
        for i in windows:
            app_id = get_app_id(i[0])
            file = get_app_name(i[0])
            if app_id < 0: continue
            # try:
            #     print("DD")
            #     # item_pid = psutil.Process(app_id)
            # except:
            #     print("ERROR")
            #     pass
            # if file == None: continue
            for j in BANNED_APPS:
                if j in i[1] or file != None and  j in file:
                    res = datetime.now().timestamp() - BANNED_APPS[j]
                    if res > 3600:
                        rect = win32gui.GetWindowRect(i[0])
                        x = rect[0]
                        y = rect[1]
                        w = rect[2] - x
                        h = rect[3] - y
                        requests.get(server_url("banned_app_report"), params={"chat_id": CONFIG["chat_id"], "name": j})
                        root = tk.Tk()
                        root.attributes('-alpha', 0.0)  # For icon
                        # root.lower()
                        root.iconify()
                        window = tk.Toplevel(root)
                        center_window(window, w, h, x, y)

                        window.overrideredirect(1)  # Remove border
                        # window.attributes('-topmost', 1)
                        # Whatever buttons, etc
                        close = tk.Button(window, text="Close Window", command=lambda: destroy_ban_app(window, i[0]))
                        close.pack(fill=tk.BOTH, expand=1)
                        window.attributes('-topmost',True)
                        window.mainloop()
                        print("BANNED APP WORKING - " + i[1])
                        BANNED_APPS[j] = datetime.now().timestamp()


def destroy_ban_app(tk_window, ban_app_hwnd):
    tk_window.destroy()
    win32gui.CloseWindow(ban_app_hwnd)


threading.Thread(target=sniff, kwargs={"filter": "ip", "prn": lambda x:check_ip(x)}).start()
threading.Thread(target=controlBannedApps).start()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict()
        r = requests.get(server_url("login"), params={"id": data["account-id"]}).json()

        if not r["status"]:
            return render_template("login.html", error="Аккаунт не найден")

        CONFIG["chat_id"] = data["account-id"]
        return redirect("/settings")
    return render_template("login.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    global BANNED_HOSTNAMES
    if request.method == "POST":
        print(request.form.to_dict())
        if "banned_apps" in request.form:
            for i in request.form["banned_apps"].split(", "):
                if i not in BANNED_APPS:
                    BANNED_APPS[i] = 0
            CONFIG["banned_apps"] = list(BANNED_APPS.keys())
        if "banned_hostnames" in request.form:
            BANNED_HOSTNAMES = request.form["banned_hostnames"].split(", ")
            CONFIG["banned_sites"] = BANNED_HOSTNAMES
        CONFIG["screen_access"] = "scrn_acc" in request.form
        CONFIG["statistics_access"] = "stat_acc" in request.form
    return render_template("settings.html", banned_apps=", ".join(BANNED_APPS.keys()), banned_sites=", ".join(BANNED_HOSTNAMES), stat_acc=CONFIG["statistics_access"], scrn_acc=CONFIG["screen_access"])
webbrowser.open("http://127.0.0.1:5000/", new=0, autoraise=True)
app.run()

# if __name__ == '__main__':
#     Process(target=controlBannedApps, args=[QUEUE]).start()
#     qapp = QApplication(sys.argv)
#     CONFIG.qapp = qapp
#     # # setting name to the application
#     qapp.setApplicationName("Chrome Web Browser")
#     #
#     # # creating a main window object
#     window = MainWindow()
#     CONFIG.qmainwindow = window
#     window.setWindowFlag(Qt.FramelessWindowHint)
#     # window.setWindowFlags(Qt.CustomizeWindowHint)
#     qapp.exec()