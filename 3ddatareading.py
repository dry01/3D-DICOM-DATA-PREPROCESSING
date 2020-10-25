# -*- coding: utf-8 -*-
"""3DDATAREADING.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gsarmHR79jBb4mkRVGtL53NxyAnlml8p
"""

!pip install pydicom

!pip install pynrrd

# Commented out IPython magic to ensure Python compatibility.
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib
import tensorflow as tf
import os
import sys
import pydicom as dicom
import  nrrd
import scipy.ndimage
import scipy.misc
import pickle
import random
# %matplotlib notebook

def return_nrrd(file_path):

    out_nrrd = {}
    for dirName, subdirList, fileList in os.walk(file_path):
        for filename in fileList:
            if ".nrrd" in filename.lower():
                name = filename.split('_')[0] 
                name = name.split('.')[0] 
                out_nrrd[name] = os.path.join(dirName,filename)
    return out_nrrd

def return_dcm(file_path, check_term = 'Prostate'):
    
    out_dcm = {}
    for dirName, subdirList, fileList in os.walk(file_path):
        c_dcm = []
        cur_name = ""
        dir_split = dirName.split("/")
        for f_chk in dir_split:
            if check_term in f_chk:
                cur_name = f_chk
        for filename in fileList:
            if ".dcm" in filename.lower():
                name = int(os.path.splitext(filename)[0])
                c_dcm.append((os.path.join(dirName,filename), name))
        if len(c_dcm) > 0:
            c_dcm = sorted(c_dcm, key = lambda t: t[1]) 
            out_dcm[cur_name] = [c[0] for c in c_dcm] 
    return out_dcm

def get_dataset(data_dir, anns_dir):
    
    data_out = []
    shapes = {}
    d_dcm = return_dcm(data_dir)
    d_nrrd = return_nrrd(anns_dir)
    for i in d_nrrd:
        seg, opts = nrrd.read(d_nrrd[i])
        voxels = np.zeros(np.shape(seg))
        for j in range(len(d_dcm[i])):
            dicom_ref = dicom.read_file(d_dcm[i][j])
            found = False
            chk_val = dicom_ref[("0020", "0013")].value 
          
            if int(chk_val.__str__()) - 1 < np.shape(voxels)[-1]:
                voxels[:, :, int(chk_val.__str__()) - 1] = dicom_ref.pixel_array
            else: 
                print('Index: ',str(int(chk_val.__str__()) - 1), ' too large for ', i, ' skipping!')

        seg = scipy.ndimage.interpolation.rotate(seg, 90, reshape = False)
        for i in range(np.shape(seg)[2]):
            cur_img = np.squeeze(seg[:, :, i])
            seg[:, :, i] = np.flipud(cur_img)
        
        if voxels.shape in shapes:
            shapes[voxels.shape] += 1
        else:
            shapes[voxels.shape] = 1
        
        data_out.append((voxels, seg))
    return data_out

def plot_slice(slice_in, is_anns = False, num_anns = 4):
    
    slice_in = np.squeeze(slice_in)
    plt.figure()
    plt.set_cmap(plt.bone())
    if is_anns:
        plt.pcolormesh(slice_in, vmin = 0, vmax = num_anns - 1)
    else:
        plt.pcolormesh(slice_in)
    plt.show()

def multi_slice_viewer(feats, anns = None, preds = None, num_classes = 4):
    
    if anns is None:
        fig, ax = plt.subplots()
        ax.volume = feats
        ax.index = feats.shape[-1] // 2
        ax.imshow(feats[:, :, ax.index],  cmap='bone')
        fig.canvas.mpl_connect('key_press_event', process_key)
    else:
        if preds is None:
            fig, axarr = plt.subplots(1, 2)
            plt.tight_layout()
            axarr[0].volume = feats
            axarr[0].index = 0
            axarr[0].imshow(feats[:, :, axarr[0].index],  cmap='bone')
            axarr[0].set_title('Scans')
            axarr[1].volume = anns
            axarr[1].index = 0
            axarr[1].imshow(anns[:, :, axarr[1].index],  cmap='bone', vmin = 0, vmax = num_classes)
            axarr[1].set_title('Annotations')
            fig.canvas.mpl_connect('key_press_event', process_key)
        else:
            fig, axarr = plt.subplots(1, 3)
            plt.tight_layout()
            axarr[0].volume = feats
            axarr[0].index = 0
            axarr[0].imshow(feats[:, :, axarr[0].index],  cmap='bone')
            axarr[0].set_title('Scans')
            axarr[1].volume = anns
            axarr[1].index = 0
            axarr[1].imshow(anns[:, :, axarr[1].index],  cmap='bone', vmin = 0, vmax = num_classes)
            axarr[1].set_title('Annotations')
            axarr[2].volume = preds
            axarr[2].index = 0
            axarr[2].imshow(preds[:, :, axarr[2].index],  cmap='bone', vmin = 0, vmax = num_classes)
            axarr[2].set_title('Predictions')
            fig.canvas.mpl_connect('key_press_event', process_key)

def process_key(event):
    
    fig = event.canvas.figure
    if event.key == 'j':
        for ax in fig.axes: 
            previous_slice(ax)
    elif event.key == 'k':
        for ax in fig.axes: 
            next_slice(ax)            
    fig.canvas.draw()

def previous_slice(ax):
    """ previous slice."""
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[-1]  
    ax.images[0].set_array(volume[:, :, ax.index])

def next_slice(ax):
    """ next slice."""
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[-1]
    ax.images[0].set_array(volume[:, :, ax.index])

from google.colab import drive
drive.mount('/gdrive')

data_leader_dir = '/gdrive/My Drive/ ISBI- 2013/Leaderboard data'
anns_leader_dir = '/gdrive/My Drive/ ISBI- 2013/Leaderboard'
data_test_dir = '/gdrive/My Drive/ ISBI- 2013/test data'
anns_test_dir = '/gdrive/My Drive/ ISBI- 2013/Test 2'
data_train_dir = '/gdrive/My Drive/ ISBI- 2013/training data'
anns_train_dir = '/gdrive/My Drive/ ISBI- 2013/Training'

#train = get_dataset(data_train_dir, anns_train_dir)
test = get_dataset(data_test_dir, anns_test_dir)
#train = train + get_dataset(data_leader_dir, anns_leader_dir)

