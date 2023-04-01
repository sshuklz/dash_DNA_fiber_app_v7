
"""
Created on Tue Jul 19 16:00:28 2022

@author: Shalabh
"""

import numpy as np
import cv2
import base64
import plotly.graph_objects as go
from scipy import ndimage

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
    
    def crop_operation(self, c1,c2,c3, overlay_type, x0, x1, y0, y1):
        
        image_src = self.image_file_src
        image_src = image_src[y0:y1 , x0:x1]  
        tracks = (image_src[:,:,:3])
        
        if c3 is None:
        
            if c1 in ['R','G'] and c2 in ['R','G']:
                
               tracks[:,:,2] = np.zeros([tracks.shape[0], tracks.shape[1]])
                
            if c1 in ['B','R'] and c2 in ['B','R']:
                
                tracks[:,:,1] = np.zeros([tracks.shape[0], tracks.shape[1]])
                
            if c1 in ['B','G'] and c2 in ['B','G']:
                
                tracks[:,:,0] = np.zeros([tracks.shape[0], tracks.shape[1]])
        
        if overlay_type == 'Selection' or overlay_type == 'Segments':
            
            return tracks, None
        
        if overlay_type == '1º label':
            
            if c1 == 'R':
            
                cmap = ['#000000', '#ff0000']
                return tracks[:,:,0], cmap
                
            elif c1 == 'G':
            
                cmap = ['#000000', '#00ff00']
                return tracks[:,:,1], cmap
                
            elif c1 == 'B':
            
                cmap = ['#000000', '#0000ff']
                return tracks[:,:,2], cmap
            
        if overlay_type == '2º label':
            
            if c2 == 'R':
            
                cmap = ['#000000', '#ff0000']
                return tracks[:,:,0], cmap
                
            elif c2 == 'G':
            
                cmap = ['#000000', '#00ff00']
                return tracks[:,:,1], cmap
                
            elif c2 == 'B':
            
                cmap = ['#000000', '#0000ff']
                return tracks[:,:,2], cmap
        
        if overlay_type == 'Fish label':
            
            cmap = None
            
            if c3 == 'R':
            
                cmap = ['#000000', '#ff0000']
                
            elif c3 == 'G':
            
                cmap = ['#000000', '#00ff00']
                
            elif c3 == 'B':
            
                cmap = ['#000000', '#0000ff']
            
            return tracks[:,:,2],cmap
        
        max_vals = [tracks[:,:,0].max(),tracks[:,:,1].max(),tracks[:,:,2].max()]

        dim_red= (max_vals[0]/6, 0, 0)
        full_red = (255, max_vals[1]/2.5, max_vals[2]/2.5)
        dim_green= (0, max_vals[1]/6, 0)
        full_green = (max_vals[0]/2.5, 255, max_vals[2]/2.5)
        dim_blue= (0, 0, max_vals[2]/6)
        full_blue = (max_vals[0]/2.5, max_vals[1]/2.5, 255)
        
        dim_yellow =(max_vals[0]/1.2, max_vals[1]/1.2, 0)
        dim_cyan= (0, max_vals[1]/1.2, max_vals[2]/1.2)
        dim_magenta = (max_vals[0]/1.2, 0, max_vals[2]/1.2)
        full= (255, 255, 255)
        
        mask_R = cv2.inRange(tracks, dim_red, full_red)
        mask_R = (ndimage.binary_fill_holes(mask_R).astype(np.uint8))*255
        
        mask_G = cv2.inRange(tracks, dim_green, full_green)
        mask_G = (ndimage.binary_fill_holes(mask_G).astype(np.uint8))*255
        
        mask_B = cv2.inRange(tracks, dim_blue, full_blue)
        mask_B = (ndimage.binary_fill_holes(mask_B).astype(np.uint8))*255
        
        if c3 is  None:
        
            if c1 in ['R','G'] and c2 in ['R','G']:
                
                mask_B = tracks[:,:,2]
                cmap_overlay = ['#000000', '#ffff00']
                
            if c1 in ['B','R'] and c2 in ['B','R']:
                
                mask_G = tracks[:,:,1]
                cmap_overlay = ['#000000', '#ff00ff']
            if c1 in ['B','G'] and c2 in ['B','G']:
                
                mask_R = tracks[:,:,0]
                cmap_overlay = ['#000000', '#00ffff']
        
        mask_Y = cv2.inRange(tracks, dim_yellow, full)
        mask_C = cv2.inRange(tracks, dim_cyan, full)
        mask_M = cv2.inRange(tracks, dim_magenta, full)
        
        full_mask = cv2.bitwise_or(mask_Y, mask_C)
        full_mask = cv2.bitwise_or(full_mask, mask_M)
        full_mask = (ndimage.binary_fill_holes(full_mask).astype(np.uint8))*255
        full_mask_IM = cv2.merge([full_mask,full_mask,full_mask])
        full_mask_IM[:,:,2] = np.zeros([full_mask_IM.shape[0], full_mask_IM.shape[1]])
        
        rgb_mask = cv2.merge([mask_R,mask_G,mask_B]) + full_mask_IM
        
        if overlay_type == 'Overlap':
            
            return full_mask,cmap_overlay
        
        if overlay_type == 'Binarized':
            
            return rgb_mask,None
        
        return tracks
        
        return 
        
    def G_R_B_GP_OV_operation(self, c1,c2,c3, DNA_fiber_type, x0, x1, y0, y1):
            
        image_src = self.image_file_src
        
        if x0 != None:
            
            image_src = image_src[y0:y1 , x0:x1]
         
        tracks = (image_src[:,:,:3])
        length = tracks.shape[0]
        width = tracks.shape[1]
        
        if c3 is None:
        
            if c1 in ['R','G'] and c2 in ['R','G']:
                
               tracks[:,:,2] = np.zeros([length, width])
                
            if c1 in ['B','R'] and c2 in ['B','R']:
                
                tracks[:,:,1] = np.zeros([length, width])
                
            if c1 in ['B','G'] and c2 in ['B','G']:
        
                tracks[:,:,0] = np.zeros([length, width])
        
        max_vals = [tracks[:,:,0].max(),tracks[:,:,1].max(),tracks[:,:,2].max()]
        
        dim_red= (max_vals[0]/6, 0, 0)
        full_red = (255, max_vals[1]/2.5, max_vals[2]/2.5)
        dim_green= (0, max_vals[1]/6, 0)
        full_green = (max_vals[0]/2.5, 255, max_vals[2]/2.5)
        dim_blue= (0, 0, max_vals[2]/6)
        full_blue = (max_vals[0]/2.5, max_vals[1]/2.5, 255)
        
        dim_yellow =(max_vals[0]/1.5, max_vals[1]/1.5, 0)
        dim_cyan= (0, max_vals[1]/1.5, max_vals[2]/1.5)
        dim_magenta = (max_vals[0]/1.5, 0, max_vals[2]/1.5)
        full= (255, 255, 255)
        
        mask_R = cv2.inRange(tracks, dim_red, full_red)
        mask_R = (ndimage.binary_fill_holes(mask_R).astype(np.uint8))*255
        R_onehot = (mask_R / 255).sum(axis=0)
        
        mask_G = cv2.inRange(tracks, dim_green, full_green)
        mask_G = (ndimage.binary_fill_holes(mask_G).astype(np.uint8))*255
        G_onehot = (mask_G / 255).sum(axis=0)
        
        mask_B = cv2.inRange(tracks, dim_blue, full_blue)
        mask_B = (ndimage.binary_fill_holes(mask_B).astype(np.uint8))*255
        B_onehot = (mask_B / 255).sum(axis=0)
        
        if c3 is  None:
        
            if c1 in ['R','G'] and c2 in ['R','G']:
                
                mask_B = tracks[:,:,2]
                B_onehot = tracks[:,:,2].sum(axis=0)
                
            if c1 in ['B','R'] and c2 in ['B','R']:
                
                mask_G = tracks[:,:,1]
                G_onehot = tracks[:,:,1].sum(axis=0)
                
            if c1 in ['B','G'] and c2 in ['B','G']:
                
                mask_R = tracks[:,:,0]
                R_onehot = tracks[:,:,0].sum(axis=0)
        
        mask_Y = cv2.inRange(tracks, dim_yellow, full)
        mask_C = cv2.inRange(tracks, dim_cyan, full)
        mask_M = cv2.inRange(tracks, dim_magenta, full)
        
        full_mask = cv2.bitwise_or(mask_Y, mask_C)
        full_mask = cv2.bitwise_or(full_mask, mask_M)
        full_mask = (ndimage.binary_fill_holes(full_mask).astype(np.uint8))*255
        full_mask_onehot = (full_mask / 255).sum(axis=0)
        full_mask_IM = cv2.merge([full_mask,full_mask,full_mask])
        full_mask_IM[:,:,2] = np.zeros([full_mask_IM.shape[0], full_mask_IM.shape[1]])
        
        rgb_mask = cv2.merge([mask_R,mask_G,mask_B]) + full_mask_IM
        
        y_nonzero, x_nonzero, _ = np.nonzero(rgb_mask)
        y0 = np.min(y_nonzero); y1 = np.max(y_nonzero)
        x0 = np.min(x_nonzero); x1 = np.max(x_nonzero)
        
        onehotRGB = np.array([R_onehot,G_onehot,B_onehot,full_mask_onehot])
        
        onehot_RGB_lim = (np.array([R_onehot[x0:x1],
                                     G_onehot[x0:x1],
                                     B_onehot[x0:x1],
                                     full_mask_onehot[x0:x1]])).sum(axis=0)
        
        half_mean_width = np.ceil(np.mean(onehot_RGB_lim) - (np.std(onehot_RGB_lim))) / 2
        
        onehotRGB_1d = []; onehotRGB_1d_trim = []; color_len_str = '{' ; n = 1 ; m = 1;
        
        for col_id in range(onehotRGB.shape[1]):
            
            col = onehotRGB[:, col_id].tolist()
            
            if sum(col) < half_mean_width or sum(col) == 0.0:
                
                onehotRGB_1d += ['GP']
                
            else:
                
                if col.index(max(col)) == 0:
                    
                    onehotRGB_1d += ['R']
                    
                elif col.index(max(col)) == 1:
                    
                    onehotRGB_1d += ['G']
                    
                elif col.index(max(col)) == 2:
                    
                    onehotRGB_1d += ['B']
                    
                elif col.index(max(col)) == 3:
                    
                    onehotRGB_1d += ['OV']
                    
                elif len([index for index in range(len(col[:-1])) if col[:-1][index] == max(col[:-1])]) > 1:
                     
                     onehotRGB_1d += ['OV']
        
            if color_len_str == '{':
                
                color_len_str += str(onehotRGB_1d[col_id])
                
            else: 
                
                if onehotRGB_1d[col_id] == onehotRGB_1d[-2]:
                
                    n+=1
                
                    if col_id == onehotRGB.shape[1]-1:
                        
                        color_len_str += (str(n) + '}')
                
                else:
                    
                    color_len_str += (str(n) + ':' + str(onehotRGB_1d[col_id]))
                    n = 1
        
        for i in range(len(onehotRGB_1d)):
            
            if i > 0:
            
                if onehotRGB_1d[i] == onehotRGB_1d[i-1]:
                    
                    m+=1
                    
                    if i == len(onehotRGB_1d) - 1:
                        
                        onehotRGB_1d_trim += [[onehotRGB_1d[i-1],m]]
                    
                else:
                    
                    onehotRGB_1d_trim += [[onehotRGB_1d[i-1],m]] ; m=1
        
        try:
            
            for i in range(len(onehotRGB_1d_trim)):
                
                if onehotRGB_1d_trim[i][0] == c1 or onehotRGB_1d_trim[i][0] == c2:
                    
                    if onehotRGB_1d_trim[i][1] <= 3:
                        
                        onehotRGB_1d_trim[i][0] = 'GP'
                        
                        if onehotRGB_1d_trim[i+1][0] == 'GP':
                            
                            onehotRGB_1d_trim[i+1][1] += onehotRGB_1d_trim[i][1]
                            onehotRGB_1d_trim.pop(i)
                            
                            if onehotRGB_1d_trim[i][0] == 'GP' and i!=0:
                                
                                onehotRGB_1d_trim[i+1][1] += onehotRGB_1d_trim[i][1]
                                onehotRGB_1d_trim.pop(i)
                        
                        elif onehotRGB_1d_trim[i-1][0] == 'GP':
                            
                            onehotRGB_1d_trim[i-1][1] += onehotRGB_1d_trim[i][1]
                            onehotRGB_1d_trim.pop(i)
                            
                            if onehotRGB_1d_trim[i][0] == 'GP' and i!=0:
                                
                                onehotRGB_1d_trim[i-1][1] += onehotRGB_1d_trim[i][1]
                                onehotRGB_1d_trim.pop(i)
        
        except:
            
            pass
        
        def remove_gaps():
        
            n = 0 ; m =len(onehotRGB_1d_trim)
        
            for x,y,z in zip(onehotRGB_1d_trim, onehotRGB_1d_trim[1:], onehotRGB_1d_trim[2:]):
                
                if x[0] == z[0]:
                    
                    if y[0] == 'GP' or  y[0] == 'OV':
                        
                        onehotRGB_1d_trim[n][1] += (y[1] + z[1])
                        onehotRGB_1d_trim.pop(n+1) ; onehotRGB_1d_trim.pop(n+1)
                        break
                        
                n+=1
                
            if len(onehotRGB_1d_trim) != m:
                remove_gaps()
                
        remove_gaps()
        
        try:
        
            for i in range(len(onehotRGB_1d_trim)):
                
                if i > 0:
                
                    if onehotRGB_1d_trim[i][0] == onehotRGB_1d_trim[i-1][0]:
                        
                        onehotRGB_1d_trim[i-1][1] += onehotRGB_1d_trim[i][1]
                        onehotRGB_1d_trim.pop(i)
                    
        except:
            
            pass
        
        hc_list = ''
        
        if DNA_fiber_type == 'interspersed':
        
            for i in range(len(onehotRGB_1d_trim)):
                
                if i == 0:
                
                    hc_list += "{"
                    
                hc_list += ':' 
                hc_list += onehotRGB_1d_trim[i][0] 
                hc_list += str(onehotRGB_1d_trim[i][1])
        
            
            hc_list += "}" 
        
        try:
        
            if DNA_fiber_type == 'stalled':
                
                first_c1 = None ; second_c1 = None ; c1_len = 0; GP1_len = 0 ; GP2_len = 0 ;
                 
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if onehotRGB_1d_trim[i][0] == c1  and first_c1 == None:
                        
                        first_c1 = i
                        
                    elif onehotRGB_1d_trim[i][0] == c1:
                        
                        second_c1 = i
                        
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if i < first_c1:
                        
                        GP1_len +=  onehotRGB_1d_trim[i][1]
                    
                    elif i >= first_c1 and i <= second_c1:
                        
                        c1_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i > second_c1:
                         
                        GP2_len +=  onehotRGB_1d_trim[i][1]
                        
                onehotRGB_1d_trim = [['GP',GP1_len],
                                     [c1,c1_len],
                                     ['GP',GP2_len]]
                
                hc_list = '{GP' + str(GP1_len) + ':' + c1 + str(c1_len) + ':GP' + str(GP2_len) + '}'
                       
            elif DNA_fiber_type == '2nd origin':
                
                first_c2 = None ; second_c2 = None ; c2_len = 0; GP1_len = 0 ; GP2_len = 0 ;
                 
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if onehotRGB_1d_trim[i][0] == c2  and first_c1 == None:
                        
                        first_c2 = i
                        
                    elif onehotRGB_1d_trim[i][0] == c2:
                        
                        second_c2 = i
                        
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if i < first_c2:
                        
                        GP1_len +=  onehotRGB_1d_trim[i][1]
                    
                    elif i >= first_c2 and i <= second_c2:
                        
                        c2_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i > second_c2:
                         
                        GP2_len +=  onehotRGB_1d_trim[i][1]
                        
                onehotRGB_1d_trim = [['GP',GP1_len],
                                     [c2,c2_len],
                                     ['GP',GP2_len]]
                        
                hc_list = '{GP' + str(GP1_len) + ':' + c2 + str(c2_len) + ':GP' + str(GP2_len) + '}'
                
            elif DNA_fiber_type == 'one-way fork':
                
                max_c1 = None ; first_c2 = None ; second_c2 = None ;
                c1_len = 0; GP1_len = 0 ; GP2_len = 0 ; first_c2_len = 0 ; second_c2_len = 0
                 
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if onehotRGB_1d_trim[i][0] == c2 and first_c2 == None:
                        
                        first_c2 = i
                    
                    if onehotRGB_1d_trim[i][0] == c1  and c1_len < onehotRGB_1d_trim[i][1] and first_c2 != None:
        
                        max_c1 = i
                        c1_len = onehotRGB_1d_trim[i][1]
                        
                    if onehotRGB_1d_trim[i][0] == c2 and max_c1 != None:
                        
                        second_c2 =i
                        
                if second_c2 == None or second_c2_len < first_c2_len:
                    
                    for i in range(len(onehotRGB_1d_trim)):
                        
                        if i < first_c2:
                            
                            GP1_len +=  onehotRGB_1d_trim[i][1]
                            
                        elif i >= first_c2 and i < max_c1:
                             
                            first_c2_len +=  onehotRGB_1d_trim[i][1]
                            
                        elif i > max_c1:
                             
                            GP2_len +=  onehotRGB_1d_trim[i][1]
                    
                    onehotRGB_1d_trim = [['GP',GP1_len],
                                         [c2,first_c2_len],
                                         [c1,c1_len],
                                         ['GP',GP2_len]]
                    
                    hc_list = ('{GP' + str(GP1_len) +
                               ':' + c2 + str(first_c2_len) +
                               ':' + c1 + str(c1_len) +
                               ':GP' + str(GP2_len) + '}')
                    
                else:
                    
                    for i in range(len(onehotRGB_1d_trim)):
                        
                        if i < max_c1:
                            
                            GP1_len +=  onehotRGB_1d_trim[i][1]
                            
                        elif i <= second_c2 and i > max_c1:
                             
                            second_c2_len +=  onehotRGB_1d_trim[i][1]
                            
                        elif i > second_c2:
                             
                            GP2_len +=  onehotRGB_1d_trim[i][1]
                            
                    onehotRGB_1d_trim = [['GP',GP1_len],
                                         [c1,c1_len],
                                         [c2,second_c2_len],
                                         ['GP',GP2_len]]
                            
                    hc_list = ('{GP' + str(GP1_len) +
                               ':' + c1 + str(c1_len) +
                               ':' + c2 + str(second_c2_len) +
                               ':GP' + str(GP2_len) + '}')
                
            elif DNA_fiber_type == 'two-way fork':
                
                max_c1 = None ; first_c2 = None ; second_c2 = None ;
                c1_len = 0; GP1_len = 0 ; GP2_len = 0 ; first_c2_len = 0 ; second_c2_len = 0
                 
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if onehotRGB_1d_trim[i][0] == c2 and first_c2 == None:
                        
                        first_c2 = i
                    
                    elif onehotRGB_1d_trim[i][0] == c1  and c1_len < onehotRGB_1d_trim[i][1] and first_c2 != None:
        
                        max_c1 = i
                        c1_len = onehotRGB_1d_trim[i][1]
                        
                    elif onehotRGB_1d_trim[i][0] == c2 and max_c1 != None:
                        
                        second_c2 = i
                        
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if i < first_c2:
                        
                        GP1_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i >= first_c2 and i < max_c1:
                         
                        first_c2_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i <= second_c2 and i > max_c1:
                         
                        second_c2_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i > second_c2:
                         
                        GP2_len +=  onehotRGB_1d_trim[i][1]
                
                onehotRGB_1d_trim = [['GP',GP1_len],
                                     [c2,first_c2_len],
                                     [c1,c1_len],
                                     [c2,second_c2_len],
                                     ['GP',GP2_len]]
                
                hc_list = ('{GP' + str(GP1_len) +
                           ':' + c2 + str(first_c2_len) +
                           ':' + c1 + str(c1_len) +
                           ':' + c2 + str(second_c2_len) +
                           ':GP' + str(GP2_len) + '}')
                
            elif DNA_fiber_type == 'terminated fork':
                
                first_max_c1 = None ; second_max_c1 = None ; first_c2 = None ; second_c2 = None ;
                c2_len = 0; GP1_len = 0 ; GP2_len = 0 ; first_c1_len = 0 ; second_c1_len = 0
                 
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if onehotRGB_1d_trim[i][0] == c1 and first_c1_len < onehotRGB_1d_trim[i][1]:
                        
                        first_max_c1 = i
                        first_c1_len = onehotRGB_1d_trim[i][1]
                    
                    elif onehotRGB_1d_trim[i][0] == c2 and first_c2 != None:
        
                        first_c2 = i
                        
                    elif onehotRGB_1d_trim[i][0] == c2:
                        
                        second_c2 =i
                        
                    elif onehotRGB_1d_trim[i][0] == c1 and second_c2 != None and second_c1_len < onehotRGB_1d_trim[i][1]:
                        
                        second_max_c1 = i
                        second_c1_len = onehotRGB_1d_trim[i][1]
                        
                for i in range(len(onehotRGB_1d_trim)):
                    
                    if i < first_max_c1:
                        
                        GP1_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i > first_max_c1 and i < second_max_c1:
                         
                        c2_len +=  onehotRGB_1d_trim[i][1]
                        
                    elif i > second_max_c1:
                         
                        GP2_len +=  onehotRGB_1d_trim[i][1]
                        
                onehotRGB_1d_trim = [['GP',GP1_len],
                                     [c1,first_c1_len],
                                     [c2,c1_len],
                                     [c1,second_c1_len],
                                     ['GP',GP2_len]]
                        
                hc_list = ('{GP' + str(GP1_len) +
                           ':' + c1 + str(first_c1_len) +
                           ':' + c2 + str(c2_len) +
                           ':' + c1 + str(second_c1_len) +
                           ':GP' + str(GP2_len) + '}')
                
        except:
            
            for i in range(len(onehotRGB_1d_trim)):
                
                if i == 0:
                
                    hc_list += "{"
                    
                hc_list += onehotRGB_1d_trim[i][0] 
                hc_list += str(onehotRGB_1d_trim[i][1])
                hc_list += ':'
        
            hc_list += "}" 
            
            pass

        return (onehotRGB_1d_trim, 
                "\n".join([" ".join([str(item) for item in sublist]) for sublist in onehotRGB_1d_trim]),
                [x0,x1,y0,y1])
        