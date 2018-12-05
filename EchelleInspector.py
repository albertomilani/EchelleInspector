#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import tkFileDialog
import pyfits
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import re

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Echelle Inspector")

        # FITS file
        self.f = None

        # FITS header window
        self.fits_header_window = None

        # Add menu
        self.addMenu()

    def addMenu(self):
        # Menu
        self.menubar = tk.Menu(self.master)
        # Submenu File
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.fileOpen)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.master.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # Submenu FITS
        self.fitsmenu = tk.Menu(self.menubar, tearoff=0)
        self.fitsmenu.add_command(label="Show header", command=self.fitsShowHeader)
        self.menubar.add_cascade(label="FITS", menu=self.fitsmenu)
        # Add menu
        self.master.config(menu=self.menubar)

    def fileOpen(self):
        # Permit only fits files
        file_types = (("FITS","*.FITS"), ("FIT","*.FIT"), ("fits","*.fits"), ("fit","*.fit"))
        self.filename = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = file_types)
        if self.filename:
            self.f = None
            self.f = pyfits.open(self.filename)
            self.f_wl = self.parseWavelenght(self.f[0].header)
            self.plotSpectrum(21)

    def plotSpectrum(self, order):
        aperture = self.f_wl[order]['aperture']
        scidata = self.f[0].data[aperture]
        num_pix = len(scidata)
        wl_step = self.f_wl[order]['wl_step']
        wl_start = self.f_wl[order]['wl_start']
        wl_end = wl_start + (num_pix-1)*wl_step

        f = Figure(figsize=(8, 6), dpi=100)
        t = np.arange(wl_start, wl_end, wl_step)
        f.add_subplot(111).plot(t, scidata)

        canvas = FigureCanvasTkAgg(f, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def parseWavelenght(self, header):
        string = ''
        for k in header:
            if k[0:4] == 'WAT2':
                string += header[k]
        links = re.findall('spec\d+\s=\s\"([\.\s\d]+)\"', string)
        sp_orders_wl = {}
        for r in links:
            data = r.split(' ')
            sp_orders_wl[int(data[1])] = {'aperture': int(data[0]), 'wl_start': float(data[3]), 'wl_step': float(data[4])}
        return sp_orders_wl

    def fitsShowHeader(self):
        # show header in new window
        if self.f:
            if self.fits_header_window:
                self.fits_header_window.destroy()
            self.fits_header_window = tk.Toplevel()
            self.fits_header_window.resizable(0, 0)
            self.fits_header_window.title('FITS header')
            # add textbox and scrollbar
            scrollbar = tk.Scrollbar(self.fits_header_window)
            textbox = tk.Text(self.fits_header_window, height=30, width=82)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            textbox.pack(side=tk.LEFT, fill=tk.Y)
            scrollbar.config(command=textbox.yview)
            textbox.config(yscrollcommand=scrollbar.set)
            # build text
            header_text = ''
            for i in self.f[0].header:
                header_text = header_text + str(i) + ' = \'' + str(self.f[0].header[i]) + '\'\n'
            #add text
            textbox.insert(tk.END, header_text)



root = tk.Tk()
gui = GUI(root)
root.mainloop()

