# -*- coding: utf-8 -*-
# ===========================================================================
# File:    DBTool_main.py
# Author:  mark
# Time:    2025/8/15 20:23
# Email:   maky_cq@163.com
# Version： V3.0
# Description: xxx
# History:
# <author>    <version>      <time>         <desc>
#  mark          V1.0        2025/8/26      构建框架
#  mark          V2.0        2025/8/27   构建start_test函数功能模块
#  mark          V3.0        2025/8/28   构建export_log函数功能模块
# ===========================================================================


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal,QObject
# from qt_material import list_themes
# import qdarkstyle
import sys  # 导入sys模块
from ParseLog import pull_DBlog,pull_logacat,parse_DB,parse_exp_main
from PyQt5.QtGui import QIcon
import subprocess
import time
import os
from pathlib import Path
from threading import Thread
from threading import Event
import shutil
from utils import zip_and_move_folder

class Ui_demo(QMainWindow):
    def __init__(self, parent=None):
        super(Ui_demo, self).__init__(parent)
        self.setupUi(self)  # 初始化窗体设置
        self.is_testing = False
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1275, 810)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setMaximumSize(QtCore.QSize(239, 31))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.verticalLayout_2.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tableWidget = QtWidgets.QTableWidget(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.tableWidget.setFont(font)
        self.tableWidget.setAutoScrollMargin(16)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        #item = QtWidgets.QTableWidgetItem()
        #self.tableWidget.setHorizontalHeaderItem(7, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(29)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_2.addWidget(self.tableWidget)
        self.verticalLayout_2.addWidget(self.frame_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1275, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # 为测试开始按钮绑定start_test槽函数
        self.pushButton.clicked.connect(self.start_test)
        # 为导出日志按钮绑定export_log槽函数
        self.pushButton_2.clicked.connect(self.export_log)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def start_test(self):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.is_testing = True
        # 获取当前设备id
        device_id = subprocess.check_output('adb devices').decode().split('\n')[1].split('\t')[0]
        # adb命令cd到log路径然后删除该路径下所有文件夹
        #adb_cmd = f"adb -s {device_id} shell rm -r /log/*"
        #subprocess.run(adb_cmd)
        #time.sleep(10)
        def run():
            # 每隔1分钟，执行一次pull_android_DBlog函数，然后调用parse_DB函数解析日志
            # ADB root和remount
            subprocess.run('adb root', check=True, shell=True)
            time.sleep(1)
            subprocess.run('adb remount', check=True, shell=True)
            time.sleep(1)

            cur_path = os.getcwd()  # 当前目录
            base_dir = Path(os.path.join(cur_path, 'DBfile'))
            parsed_files = set()  # 存储已解析的文件路径
            # print(parsed_files)
            local_base_pathA = os.path.join(cur_path, 'DBfile/android')
            remote_base_pathA = '/log/android/aee_exp/'
            local_base_pathT = os.path.join(cur_path, 'DBfile/tbox')
            remote_base_pathT = '/log/tbox/aee_exp/'
            local_base_pathC = os.path.join(cur_path, 'DBfile/cluster')
            remote_base_pathC = '/log/cluster/aee_exp/'
            count = 0
            while True:
                pull_DBlog(local_base_pathA, remote_base_pathA)
                time.sleep(2)
                pull_DBlog(local_base_pathT, remote_base_pathT)
                time.sleep(2)
                pull_DBlog(local_base_pathC, remote_base_pathC)
                time.sleep(2)
                parse_DB()    # 考虑是否放到下方try中
                # 获取所有子目录（包括嵌套子目录）
                subdirs = [d for d in base_dir.rglob('*') if d.is_dir()]
                for dir_path in subdirs:
                    main_file = dir_path / "__exp_main.txt"
                    #print(main_file)
                    if main_file.exists() and main_file not in parsed_files:
                        try:
                            #DB = DBLogPpase(str(main_file))
                            exception_info = parse_exp_main(str(main_file))
                            print(exception_info)
                            parsed_files.add(main_file)  # 记录已解析的文件
                            # 获取当前行数
                            row_position = self.tableWidget.rowCount()
                            # 插入新行
                            self.tableWidget.insertRow(row_position)
                            # 设置各列的值
                            #self.tableWidget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(row_position + 1)))
                            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(exception_info["Exception Log Time"] or ""))
                            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(exception_info["System"] or ""))
                            self.tableWidget.setItem(row_position, 2, QTableWidgetItem(exception_info["Exception Class"] or ""))
                            self.tableWidget.setItem(row_position, 3, QTableWidgetItem(exception_info["Exception Type"] or ""))
                            self.tableWidget.setItem(row_position, 4, QTableWidgetItem(exception_info["Current Executing Process"] or ""))
                            self.tableWidget.setItem(row_position, 5, QTableWidgetItem(exception_info["PID"] or ""))
                            self.tableWidget.setItem(row_position, 6, QTableWidgetItem(exception_info["Subject"] or ""))
                            # 调整列宽以适应内容
                            self.tableWidget.resizeColumnsToContents()
                            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格禁止编辑
                        except Exception as e:
                            print(f"Error parsing {main_file}: {e}")
                if not self.is_testing:
                    break
                count = count + 1
                print("=================================================================")
                print(f"第 {count} 次轮询")
                print("=================================================================")
                time.sleep(60)
        t = Thread(target=run, daemon=True)
        t.start()



    def export_log(self):
        # 停止采集的动作
        self.is_testing = False
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        # 导出DB日志和logcat日志，并弹出日志导出完成的弹窗

        #DB = DBLogPpase()
        #DB.pull_logacat()
        zip_and_move_folder("DBfile", "D:/")
        # 判断move完成
        while not os.path.exists('D:/DBfile.zip'):
            time.sleep(1)
        # 如果move完成就弹窗
        msg = QMessageBox()
        msg.setText("日志导出成功！")
        msg.exec_()
        time.sleep(1)


# 增加功能：判断adb是否存在；
# 导出日志跑进度条；


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "MTK平台DB异常采集工具"))
        self.pushButton.setText(_translate("MainWindow", "开始采集"))
        self.pushButton_2.setText(_translate("MainWindow", "导出日志"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Trigger Time"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "System"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Exception Class"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Exception Type"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "process"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PID"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Subject"))
        #item = self.tableWidget.horizontalHeaderItem(7)
        #item.setText(_translate("MainWindow", "Subject"))

# 主方法
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()  # 创建窗体对象
    ui = Ui_demo()  # 创建PyQt5设计的窗体对象
    ui.setupUi(MainWindow)  # 调用PyQt5窗体的方法对窗体对象进行初始化设置
    MainWindow.show()  # 显示窗体
    sys.exit(app.exec_())  # 程序关闭时退出进程
