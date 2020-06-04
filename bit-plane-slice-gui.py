import os
import time

import tkinter.messagebox
from tkinter import *
from tkinter import filedialog

import cv2
import numpy as np


def convert_image_to_bit_planes(img, bit_size):
    """
    Convert a color image to separate rgb bit planes
    Parameters:
    img: OpenCV image
    bit_size:
    Returns
    b_bits: Blue channel bit planes
    g_bits: Green channel bit planes
    r_bits: Red channel bit planes

    """
    # split channels in a color (3-channel) image
    b, g, r = cv2.split(img)
    # convert image integers to bits assuming 8 bit image for each color channel
    b_bits = np.unpackbits(b).reshape(bit_size)
    g_bits = np.unpackbits(g).reshape(bit_size)
    r_bits = np.unpackbits(r).reshape(bit_size)

    return b_bits, g_bits, r_bits

def convert_bit_planes_to_image(b_bits, g_bits, r_bits, img_size):
    """
    Convert RGB bit planes back into a color image
    Parameters
    b_bits: Blue channel bit planes
    g_bits: Green channel bit planes
    r_bits: Red channel bit planes
    Returns
    img: OpenCV image
    """
    # convert back to 8-bit integer in the original shape
    b_aug = np.packbits(b_bits).reshape(img_size)
    g_aug = np.packbits(g_bits).reshape(img_size)
    r_aug = np.packbits(r_bits).reshape(img_size)
    # DEBUG USE : see b g r value written to exported image
    # np.savetxt('baug.csv', b_aug, delimiter=',')
    # combine the channels back into a color image
    return cv2.merge((b_aug, g_aug, r_aug))

def bit_plane_slice(b_bits, g_bits, r_bits, bit_plane_list):
    """
    Zeroize the bit planes in the list for all the rgb bit plane images
    Parameters
    b_bits: Blue channel bit planes
    g_bits: Green channel bit planes
    r_bits: Red channel bit planes
    bit_plane_list: list of channels to zeroize
    """
    if bit_plane_list is not None:
        # tkinter.messagebox.showwarning(title='Message', message=bit_plane_list)
        for bit_plane in range(0, 8):
            if str(bit_plane) not in str(bit_plane_list):
                # tkinter.messagebox.showwarning(title='Message', message='bit_plane ' + str(bit_plane) + 'NOT in bit_plan_list ' + str(bit_plane_list))
                b_bits[:, :, int(bit_plane)] = 0
                g_bits[:, :, int(bit_plane)] = 0
                r_bits[:, :, int(bit_plane)] = 0
                # tkinter.messagebox.showwarning(title='Message', message='bitplane' + str(bit_plane) + ' cleared')

class GUI(Frame):
    def __init__(self, master=None):
        self.updateflag = 0
        self.filecontent = []
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    # Generate GUI
    def createWidgets(self):
        # Label GUI objects
        Label(self, text='Keep these Bitplanes : \r (example input: 0,2,7)').grid(row=1, column=0, sticky=E)
        Label(self, text='Import image :').grid(row=2, column=0, sticky=E)
        Label(self, text='Export to :').grid(row=3, column=0, sticky=E)

        # Choose bitplane number
        # self.boxValueBitplane = IntVar()
        # self.BitplaneChoice = ttk.Combobox(self, textvariable=self.boxValueBitplane, state='readonly', width=8)
        # self.BitplaneChoice['value'] = (0, 0, 1, 2, 3, 4, 5, 6, 7)
        # self.BitplaneChoice.current(1)
        # self.BitplaneChoice.grid(row=1, column=1, padx=10, pady=5, sticky=W)
        # Input bitplane numbers
        self.inputbitplane = StringVar()
        self.BitplaneChoice = Entry(self, textvariable=self.inputbitplane, width=40)
        self.BitplaneChoice.grid(row=1, column=1, padx=10, pady=5, sticky=W)

        # Import filepath
        self.importpath = StringVar()
        self.boxImportpath = Entry(self, textvariable=self.importpath, width=40)
        self.boxImportpath.grid(row=2, column=1, padx=10, pady=5, sticky=W)
        ## Select importpath button
        self.buttonImport = Button(self, text='...', width=3, command=self.OpenImportFile)
        self.buttonImport.grid(row=2, column=2, sticky=W, padx=10, pady=5)

        # Export filepath
        self.exportpath = StringVar()
        self.boxExportpath = Entry(self, textvariable=self.exportpath, width=40)
        self.boxExportpath.grid(row=3, column=1, padx=10, pady=5, sticky=W)
        ## Select exportpath button
        self.buttonExport = Button(self, text='...', width=3, command=self.OpenExportFile)
        self.buttonExport.grid(row=3, column=2, sticky=W, padx=10, pady=5)

        # Slice button
        self.slice_service = StringVar()
        self.slice_service.set('Slice')
        Button(self, textvariable=self.slice_service, width=10, command=self.slice).grid(row=5, column=1, sticky=W, padx=10, pady=5)
        # Exit button
        Button(self, text='Exit', width=10, command=self.QuitWin).grid(row=5, column=2, sticky=W, padx=10, pady=5)

    def QuitWin(self):
        try:
            time.sleep(0.15)
            self.slice_service.close()
        except Exception:
            pass
        root.destroy()

    # Select import image
    def OpenImportFile(self):
        cur_path = os.getcwd()
        filename = filedialog.askopenfilename(initialdir=cur_path)
        if filename != '':
            self.importpath.set(filename)

    # Select export directory
    def OpenExportFile(self):
        cur_dir = os.getcwd()
        dirname = filedialog.askdirectory(initialdir=cur_dir)
        if dirname != '':
            self.exportpath.set(dirname)

    # Slice main
    def slice(self):
        # Import file name
        filepath = self.importpath.get()
        fullname = os.path.basename(filepath)
        basename = fullname.split('.')[0]
        extname = fullname.split('.')[-1]
        # Selected bitplane
        plane_list = self.inputbitplane.get().split(',')
        dash = '_'
        plane_list_num = dash.join(plane_list)
        # Export file name
        exportdir = self.exportpath.get()
        exportpathformat = [exportdir + '/' + basename, extname, 'bitplane' + plane_list_num + '.bmp']
        exportpath = dash.join(exportpathformat)
        # tkinter.messagebox.showwarning(title='Message', message='export to:' + exportpath)
        # Import file
        img = cv2.imread(filepath)
        height, width, channels = img.shape
        img_size = (height, width)
        bit_size = img_size + (8,)

        try:
            b_ch, g_ch, r_ch = convert_image_to_bit_planes(img, bit_size)
            # tkinter.messagebox.showwarning(title='Message', message=str(b_ch))
            if self.inputbitplane is not None:
                bit_plane_slice(b_ch, g_ch, r_ch, plane_list)
                img = convert_bit_planes_to_image(b_ch, g_ch, r_ch, img_size)
                # DEBUG USE : view num matrix of exported image
                # img_2d = np.reshape(img,(-1, 256))
                # np.savetxt('img_2d.csv', img_2d, delimiter=',')
                cv2.imwrite(exportpath, img)
                tkinter.messagebox.showwarning(title='Message', message='Export Suceed!')
            else:
                pass
        except Exception:
            tkinter.messagebox.showwarning(title='Message', message='Export Failure!')

root = Tk()
root.title('Bitplane slice tool GUI')
app = GUI(root)
mainloop()


    # Select export directory
    def OpenExportFile(self):
        cur_dir = os.getcwd()
        dirname = filedialog.askdirectory(initialdir=cur_dir)
        if dirname != '':
            self.exportpath.set(dirname)

    # Slice main
    def slice(self):
        # Import file name
        filepath = self.importpath.get()
        fullname = os.path.basename(filepath)
        basename = fullname.split('.')[0]
        extname = fullname.split('.')[-1]
        # Selected bitplane
        plane_list = list(self.inputbitplane.get().split(','))
        # Export file name
        exportpath = self.exportpath.get() + '/' + basename + '_' + extname + '_' + 'plane' + str(plane_list) + '.jpg'
        # Import file
        img = cv2.imread(filepath)
        height, width, channels = img.shape
        img_size = (height, width)
        bit_size = img_size + (8,)

        try:
            b_ch, g_ch, r_ch = convert_image_to_bit_planes(img, bit_size)
            if self.inputbitplane is not None:
                bit_plane_slice(b_ch, g_ch, r_ch, plane_list)
                img = convert_bit_planes_to_image(b_ch, g_ch, r_ch, img_size)
                cv2.imwrite(exportpath, img)
                tkinter.messagebox.showwarning(title='Message', message='Export Suceed!')
            else:
                pass
        except Exception:
            tkinter.messagebox.showwarning(title='Message', message='Export Failure!')


root = Tk()
root.title('Bitplane slice tool GUI')
app = GUI(root)
mainloop()
