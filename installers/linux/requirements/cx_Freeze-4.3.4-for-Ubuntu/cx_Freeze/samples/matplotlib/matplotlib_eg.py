#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx


class CanvasFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'CanvasFrame', size=(550, 350))
        self.SetBackgroundColour(wx.NamedColor('WHITE'))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizerAndFit(self.sizer)
        self.add_toolbar()

    def add_toolbar(self):
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            self.SetToolBar(self.toolbar)
        else:
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.toolbar.update()

    def OnPaint(self, event):
        self.canvas.draw()


class App(wx.App):
    def OnInit(self):
        '''Create the main window and insert the custom frame'''
        frame = CanvasFrame()
        frame.Show(True)
        return True

app = App(0)
app.MainLoop()
