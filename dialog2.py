# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!
import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
import pandas as pd
import h5py
import scipy.interpolate
import matplotlib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSplitter, QHBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sys
from queue import Queue
import time
from queue import Queue
import datetime

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        for loc, spine in self.axes.spines.items():
            # use ax.spines.items() in Python 3
            spine.set_linewidth(0)

        # FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        # FigureCanvas.updateGeometry(self)


class plot_D(QtCore.QObject):
    def __init__(self, d1,powerlist, parent=None):
        super(plot_D, self).__init__(parent)
        self.dll = d1
        self.powerlist =powerlist
        self.ax = self.dll.axes

    def aaaa(self):
        while True:
            # print('plot_ani', self.fft_plot_queue.qsize())
            if self.powerlist.empty():
                # QtCore.QThread.sleep(1)
                pass
                time.sleep(0.5)
            else:
                powerlist = self.powerlist.get()
                xy_center = [2, 2]
                N = 500
                radius = 2
                df = pd.read_csv('channel2.txt')
                ch_names = df.name.to_list()
                pos = df[['x', 'y']].values
                pos1 = pos * 2 + 2
                poslist = pos1.tolist()
                x = []
                y = []
                for zz in poslist:
                    x.append(zz[0])
                    y.append(zz[1])

                x.extend([0, 0, 4, 4])
                y.extend([4, 0, 0, 4])

                z = powerlist
                xi = np.linspace(-1, 6, N)
                yi = np.linspace(-1, 6, N)
                zi = scipy.interpolate.griddata((x, y), z, (xi[None, :], yi[:, None]), method='cubic')

                dr = xi[1] - xi[0]
                for i in range(N):
                    for j in range(N):
                        r = np.sqrt((xi[i] - xy_center[0]) ** 2 + (yi[j] - xy_center[1]) ** 2)
                        if (r - dr / 2) > radius - 0.03:
                            zi[j, i] = "nan"

                # make figure

                # set aspect = 1 to make it a circle
                # self.dll.add_subplot(111)

                self.ax.clear()
                # self.ax = self.ax2.add_subplot(111, aspect=1)

                # use different number of levels for the fill and the lines
                CS = self.ax.contourf(xi, yi, zi, 30, cmap=plt.cm.jet, zorder=2)
                self.ax.contour(xi, yi, zi, 30, colors="grey", zorder=2)
                # make a color bar
                # cbar = self.ax.colorbar(CS, ax=self.ax)
                # add the data points
                # I guess there are no data points outside the head...
                self.ax.scatter(x[:16], y[:16], marker='o', c='k', s=5, zorder=3)
                # draw a circle
                # change the linewidth to hide the
                circle = matplotlib.patches.Circle(xy=xy_center, radius=radius, edgecolor="k", facecolor="none")
                self.ax.add_patch(circle)
                # make the axis invisible
                for loc, spine in self.ax.spines.items():
                    # use ax.spines.items() in Python 3
                    spine.set_linewidth(0)
                # remove the ticks
                self.ax.set_xticks([])
                self.ax.set_yticks([])

                # Add some body parts. Hide unwanted parts by setting the zorder low
                # add two ears
                # xy = [[1.5, 3], [2, 6], [2.5, 3]]
                # polygon = matplotlib.patches.Polygon(xy=xy, facecolor="w", zorder=0)
                # ax.add_patch(polygon)
                circle = matplotlib.patches.Ellipse(xy=[0, 2], width=0.5, height=1.0, angle=0, edgecolor="k",
                                                    facecolor="w",
                                                    zorder=0)
                self.ax.add_patch(circle)
                circle = matplotlib.patches.Ellipse(xy=[4, 2], width=0.5, height=1.0, angle=0, edgecolor="k",
                                                    facecolor="w",
                                                    zorder=0)
                self.ax.add_patch(circle)
                # add a nose
                circle = matplotlib.patches.Ellipse(xy=[2, 4], width=0.2, height=0.7, angle=0, edgecolor="k",
                                                    facecolor="w",
                                                    zorder=0)
                self.ax.add_patch(circle)
                # set axes limits
                self.ax.set_xlim(-0.5, 4.5)
                self.ax.set_ylim(-0.5, 4.5)

                self.ax.set_title('EEG Montage')

                self.dll.draw()







class recievedata(QtCore.QObject):
    import datetime
    def __init__(self,powerlist, parent=None):
        import time
        super(recievedata, self).__init__(parent)
        f = h5py.File('RecordSession_2020.01.08_09.05.25.hdf5', 'r')
        rawdata = f['RawData']
        self.realrawdata = rawdata['Samples']
        self.queue = powerlist

    def uuu(self):
        for zz in range(10):
            zzz=zz*500
            aa = np.array(self.realrawdata[500+zzz:,:], float)
            y = aa.T
            powerlist = []
            xy_center = [2, 2]

            radius = 2

            for ss in range(20):
                if ss >= 16:
                    powerlist.append(min(powerlist))
                else:
                    yf1 = abs(fft(y[ss])) / len(y[ss])  # 歸一化處理
                    yf2 = yf1[range(int(len(y[ss]) / 2))]
                    sum1 = yf2.sum()
                    powerlist.append(sum1)
            print(self.queue.qsize())

            time.sleep(2)
            atime=datetime.datetime.now()
            self.queue.put(powerlist)
            btime=datetime.datetime.now()
            print(self.queue.qsize(),str(btime-atime))







class Ui_Dialog(object):
    def setupUi(self, Dialog):
        # dr = Figure_Canvas()
        # dr.test()
        self.queue1_data_to_plot = Queue()
        self.dr2 = PlotCanvas()
        self.plot_auth = plot_D(self.dr2,self.queue1_data_to_plot)

        self.plot_auth_thread = QtCore.QThread()
        self.plot_auth.moveToThread(self.plot_auth_thread)
        self.recievess = recievedata(self.queue1_data_to_plot)
        self.recieve_thread = QtCore.QThread()
        self.recievess.moveToThread(self.recieve_thread)
        self.recieve_thread.started.connect(self.recievess.uuu)
        self.recieve_thread.start()

        Dialog.setObjectName("Dialog")
        Dialog.resize(1200, 1200)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(30, 40, 89, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(170, 40, 89, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.check)

        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        # self.graphicsView.setGeometry(QtCore.QRect(300, 380, 1050, 300))
        self.graphicsView.setGeometry(QtCore.QRect(30, 80, 450, 450))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicscene = QtWidgets.QGraphicsScene()
        self.graphicscene.addWidget(self.dr2)  # 第四步，把图形放到QGraphicsScene中，注意：图形是作为一个QWidget放到QGraphicsScene中的
        self.graphicsView.setScene(self.graphicscene)  # 第五步，把QGraphicsScene放入QGraphicsView
        self.graphicsView.show()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "PushButton"))
        self.pushButton_2.setText(_translate("Dialog", "PushButton"))

    def check(self):
        if not self.plot_auth_thread.isRunning():
            self.plot_auth_thread.started.connect(self.plot_auth.aaaa)
            print('plot')
            # self.plot_auth.plot_result.connect(self.callback_plot)
            self.plot_auth_thread.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
