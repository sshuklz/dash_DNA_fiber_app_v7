#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:00:28 2022

@author: Shalabh
"""

import numpy as np
import cv2
import base64
import plotly.graph_objects as go

def blank_fig():
    
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig

def read_image_string(contents):
    
   encoded_data = contents[0].split(',')[1]
   nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
   
   return img

def parse_contents(contents, filename, date):
    
    image_mat = read_image_string(contents=contents)
    
    return image_mat

class ImageOperations(object):
    
    def __init__(self, image_file_src):
        
        self.image_file_src = image_file_src
        self.MAX_PIXEL = 255
        self.MIN_PIXEL = 0
        self.MID_PIXEL = self.MAX_PIXEL // 2
    
    def read_operation(self):
        
        image_src = self.image_file_src
            
        return image_src
    
    def rotate_operation(self, angle, flipped):

        image_src = self.image_file_src
        
        if flipped[0] is True:
        
            image_src = np.fliplr(image_src)
            
        if flipped[1] is True:
        
            image_src = np.flipud(image_src)
        
        height, width = image_src.shape[:2]
        image_center = (width/2, height/2)
        
        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)
        
        abs_cos = abs(rotation_mat[0,0]) 
        abs_sin = abs(rotation_mat[0,1])
        
        bound_w = int(height * abs_sin + width * abs_cos)
        bound_h = int(height * abs_cos + width * abs_sin)
    
        rotation_mat[0, 2] += bound_w/2 - image_center[0]
        rotation_mat[1, 2] += bound_h/2 - image_center[1]

        rotated_mat = cv2.warpAffine(image_src, rotation_mat, (bound_w, bound_h))
        
        return rotated_mat
    
    def crop_operation(self, x0, x1, y0, y1):
        
        image_src = self.image_file_src
        image_src = image_src[y0:y1 , x0:x1]  
        
        return image_src
        
    def G_R_operation(self, x0, x1, y0, y1):
        
        image_src = self.image_file_src
        image_src = image_src[y0:y1 , x0:x1]  
        reds = sum(image_src[:,:,0].flatten())
        greens = sum(image_src[:,:,1].flatten())
        
        if reds > greens:
        
            reds_new = reds / reds
            greens_new = greens / reds
            
        else:
            
            reds_new = reds / greens
            greens_new = greens / greens
            
        ratio =  ("%.2f" % greens_new) + ' : ' + ("%.2f" % reds_new)
        
        return ratio

    def gamma_operation(self, thresh_val):
        
        image_src = self.image_file_src
        invGamma = 1 / (thresh_val)
 
        table = [((i / 255) ** invGamma) * 255 for i in range(256)]
        table = np.array(table, np.uint8)
        
        image_src = cv2.LUT(image_src, table)
        return image_src
    
    def auto_correct_operation(self, c1, c2):
        
        image_src = self.image_file_src
        
        if c1 not in ['B','M','C'] and c2 not in ['B','M','C']:

            image_src[:,:,2] = np.zeros([image_src.shape[0], image_src.shape[1]])
            
        if c1 not in ['G','Y','C'] and c2 not in ['G','Y','C']:

            image_src[:,:,1] = np.zeros([image_src.shape[0], image_src.shape[1]])
            
        if c1 not in ['R','Y','M'] and c2 not in ['R','Y','M']:

            image_src[:,:,0] = np.zeros([image_src.shape[0], image_src.shape[1]])
            
        blue_val = np.mean(image_src[:,:,2].flatten()) + np.std(image_src[:,:,2].flatten())
        green_val = np.mean(image_src[:,:,1].flatten()) + np.std(image_src[:,:,1].flatten())
        red_val = np.mean(image_src[:,:,0].flatten()) + np.std(image_src[:,:,0].flatten())
        
        if c1 not in ['B','M','C'] and c2 not in ['B','M','C']:
            
            blue_val = 255
            
        if c1 not in ['G','Y','C'] and c2 not in ['G','Y','C']:
            
            green_val = 255
            
        if c1 not in ['R','Y','M'] and c2 not in ['R','Y','M']:
            
            red_val = 255
        
        image_src = self.image_file_src
        
        return int(red_val), int(green_val), int(blue_val), 1, 1, 0
    
    def denoiseI_operation(self, thresh_val):
        
        image_src = self.image_file_src
        image_src = cv2.fastNlMeansDenoisingColored(image_src,None,thresh_val,thresh_val,7,21)
        
        return image_src
    
    def contrast_operation(self, thresh_val):
        
        image_src = self.image_file_src
        image_src = cv2.convertScaleAbs(image_src, alpha = thresh_val, beta=0)

        return image_src

    def CR_operation(self, thresh_val):
        
        image_src = self.read_operation()
        image_src[:,:,0][image_src[:,:,0] < thresh_val] = 0
        
        return image_src
        
    def GR_operation(self, thresh_val):
        
        image_src = self.read_operation()
        image_src[:,:,1][image_src[:,:,1] < thresh_val] = 0
        
        return image_src
    
    def BR_operation(self, thresh_val):
        
        image_src = self.read_operation()
        image_src[:,:,2][image_src[:,:,2] < thresh_val] = 0
        
        return image_src