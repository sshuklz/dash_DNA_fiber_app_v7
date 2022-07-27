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
    
    def color_operation(self, RC, GC, BC):
        
        image_src = self.image_file_src
        
        if RC > 0:
        
            image_src[:,:,0][image_src[:,:,0] < RC] = 0
            
        if GC > 0:
            
            image_src[:,:,1][image_src[:,:,1] < GC] = 0
            
        if BC > 0:
            
            image_src[:,:,2][image_src[:,:,2] < BC] = 0
        
        return image_src
    
    def auto_correct_operation(self, c1, c2, c3):
        
        image_src = self.image_file_src

        blue_val = (np.mean(image_src[:,:,2].flatten()) + np.std(image_src[:,:,2].flatten()))
        
        green_val = (np.mean(image_src[:,:,1].flatten()) + np.std(image_src[:,:,1].flatten()))
        
        red_val = (np.mean(image_src[:,:,0].flatten()) + np.std(image_src[:,:,0].flatten()))
        
        if c3 is None:
        
            if c1 in ['R','G'] and c2 in ['R','G']:
                
                blue_val = 255
                
            if c1 in ['B','R'] and c2 in ['B','R']:
                
                green_val = 255
                
            if c1 in ['B','G'] and c2 in ['B','G']:
                
                red_val = 255
        
        return int(red_val), int(green_val), int(blue_val), 1, 1, 0
    
    def transform_operation(self, angle, flipped, gam, con, DI):

        image_src = self.image_file_src
        
        if gam != 1:
            
            invGamma = 1 / (gam)
     
            table = [((i / 255) ** invGamma) * 255 for i in range(256)]
            table = np.array(table, np.uint8)
            
            image_src = cv2.LUT(image_src, table)
            
        if con != 1:

            image_src = cv2.convertScaleAbs(image_src,
                                            alpha = con,
                                            beta=0)
            
        if DI > 0:

            image_src = cv2.fastNlMeansDenoisingColored(image_src,
                                                        None,DI,DI,7,21)
        
        if flipped[0] is True:
        
            image_src = np.fliplr(image_src)
            
        elif flipped[1] is True:
        
            image_src = np.flipud(image_src)
        
        if angle > 0:
        
            height, width = image_src.shape[:2]
            image_center = (width/2, height/2)
            
            rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)
            
            abs_cos = abs(rotation_mat[0,0]) 
            abs_sin = abs(rotation_mat[0,1])
            
            bound_w = int(height * abs_sin + width * abs_cos)
            bound_h = int(height * abs_cos + width * abs_sin)
        
            rotation_mat[0, 2] += bound_w/2 - image_center[0]
            rotation_mat[1, 2] += bound_h/2 - image_center[1]
        
            image_src = cv2.warpAffine(image_src,rotation_mat,(bound_w, bound_h))
        
        return image_src
    
    def crop_operation(self, x0, x1, y0, y1):
        
        image_src = self.image_file_src
        
        return image_src[y0:y1 , x0:x1]  
        
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
        
        return ("%.2f" % greens_new) + ' : ' + ("%.2f" % reds_new)
