#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:16:40 2022

@author: Shalabh
"""
import dash
from dash import callback_context
from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import dash_daq as daq
from dash.dependencies import (Input, Output, State)

import base64
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import re
from skimage import io

from ImageOPs import (ImageOperations, parse_contents, blank_fig)

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.config['suppress_callback_exceptions']=True
app.title='DNA Fiber Analysis DEMO'


DNA_fiber_types=['stalled',
                '2nd origin',
                'one-way fork',
                'two-way fork',
                'terminated fork',
                'interspersed']

color_types=['Primary Red : Secondary Green',
             'Primary Green : Secondary Red',
             'Primary Red : Secondary Blue',
             'Primary Blue : Secondary Red',
             'Primary Green : Secondary Blue',
             'Primary Blue : Secondary Green',
               
             'Primary Yellow : Secondary Blue',
             'Primary Blue : Secondary Yellow',
             'Primary Magenta : Secondary Green',
             'Primary Green : Secondary Magenta',
             'Primary Red : Secondary Cyan',
             'Primary Cyan : Secondary Red',
              
             'Primary Yellow : Secondary Magenta',
             'Primary Magenta : Secondary Yellow',
             'Primary Cyan : Secondary Magenta',
             'Primary Magenta : Secondary Cyan',
             'Primary Cyan : Secondary Yellow',
             'Primary Yellow : Secondary Cyan']

colors=[['R','G'],['G','R'],['R','B'],['B','R'],['G','B'],['B','G'],
        ['Y','B'],['B','Y'],['M','G'],['G','M'],['R','C'],['C','R'],
        ['Y','M'],['M','Y'],['C','M'],['M','C'],['C','Y'],['Y','C']]

df=pd.DataFrame(columns=['Fiber', 'Type', 'Length', 'Width', 'Segments'])

columns=['Fiber', 'Type', 'Length', 'Width', 'Segments']

color_options=[]
height_vals=[10,10,30,10,10,30]

for i in range(len(colors)):

    c1=colors[i][0] ; c2=colors[i][1]
    label_name = c1 +c2 + '.png'

    color_options.append({
        
        "label": html.Div([
            
            html.Img(src="/assets/Color_options/Label_" +
                     label_name,height=30),
            
            html.Div(color_types[i],
                     style={'font-size':15,'padding-left':10}),
        
        ], style={'display': 'flex',
                  'align-items': 'center', 
                  'justify-content': 'left'}),"value": color_types[i]
        
    })

def fiber_dropdown_images(c1,c2):

    fiber_options=[]

    for i in range(6):
    
        label_name = (DNA_fiber_types[i] +
                      '_' + c1 + '_' + c2 + '.png')
    
        fiber_options.append({
            
            "label": html.Div([
                
                html.Img(src="/assets/Fib_colored/" +
                         label_name, height=height_vals[i], width = 80),
                
                html.Div(DNA_fiber_types[i], 
                         style={'font-size': 15, 'padding-left': 10}),
                
            ], style={'display': 'flex',
                      'align-items': 'center',
                      'justify-content': 'start'}),"value": DNA_fiber_types[i]
                      
        })
        
    return(fiber_options)

fig = px.imshow(io.imread("assets/blank.png"))

fig.update_layout(
    coloraxis_showscale=False, 
    width=1000, height=750, 
    margin=dict(l=0, r=0, b=0, t=0))

fig.update_layout(hovermode=False)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.update_layout(dragmode=False)

app.layout=html.Div([
    
    html.Meta(charSet='UTF-8'),
    html.Meta(name='viewport', 
              content='width=device-width, initial-scale=1.0'),
    
    dcc.Store(id='shape_coords', storage_type='memory'), 
    dcc.Store(id='shape_number', storage_type='memory'), 

        html.Div([
            
            html.Div(
                id='title-app', 
                children=[html.H1(app.title)],
                
                style={'textAlign' : 'center',
                       'paddingTop' : 0,
                       'width' : '540px'}),
            
            html.Div([
                
                dcc.Upload(
                    id='upload-image',
                    
                    children=html.Div(
                        
                        ['Drag and Drop or ', html.A('Select Files')]
                    
                    ),style={
                        'width': '540px',
                        'height': '70px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                        'backgroundColor': '#F0F1F1'},multiple=True)
                
            ], style={'paddingTop' : 30}),
            
            html.Div([
                
                dcc.Tabs(
                    id='image-processors-tabs',
                    value='color_tab',
                    children=[
                        
                        dcc.Tab(
                            label='Label and Fiber Details',
                            value='color_tab',
                            
                            style={'borderBottom': '1px solid #d6d6d6',
                                   'padding': '6px',
                                   'fontWeight': 'bold',
                                   'align-items': 'center'},
                            
                            selected_style={'borderTop': '1px solid #d6d6d6',
                                            'borderBottom': '1px solid #d6d6d6',
                                            'backgroundColor': '#228bee',
                                            'color': 'white',
                                            'fontWeight': 'bold',
                                            'padding': '6px',
                                            'align-items': 'center',
                                            'justify-content' : 'center'},
                            
                            children=[html.Div([
                                    
                                html.H6('Label Colors', 
                                        style={'paddingTop' : 15}),
                                
                                
                                html.Div([
                                    
                                    dcc.Dropdown(color_options, 
                                                 color_types[0],
                                                 searchable=False, 
                                                 clearable=False,
                                                 id='color_label-dropdown')
                                    
                                ]),
                                
                                html.H6('Corrosponding Schema', 
                                        style={'paddingTop' : 15,
                                               'paddingBottom' : 15}),
                                
                                html.Img(id='schema', 
                                         style={'height':'100%', 
                                                'width':'100%'})
                                
                            ])]
                            
                        ),
                        
                        dcc.Tab(
                            label='Image Operations',
                            value='operators',
                            
                            style={'borderBottom': '1px solid #d6d6d6',
                                   'padding': '6px',
                                   'fontWeight': 'bold',
                                   'align-items': 'center'},
                            
                            selected_style={'borderTop': '1px solid #d6d6d6',
                                            'borderBottom': '1px solid #d6d6d6',
                                            'backgroundColor': '#228bee',
                                            'color': 'white',
                                            'fontWeight': 'bold',
                                            'padding': '6px',
                                            'align-items': 'center',
                                            'justify-content' : 'center'},
                            
                            children=[html.Div([
                                
                                html.H6('Subtract RGB From Image', 
                                        style={'paddingTop' : 15}),
                                
                                daq.Slider(
                                    id='slider-CR',
                                    min=0,
                                    max=255,
                                    step=1,
                                    value=0,
                                    size=540,
                                    color='red',
                                    marks={i: str(i) for i in range(0, 256, 15)}),
                                
                                html.H6(' ', style={'paddingTop' : 15}),
                                
                                daq.Slider(
                                    id='slider-GR',
                                    min=0,
                                    max=255,
                                    step=1,
                                    value=0,
                                    size=540,
                                    color='green',
                                    marks={i: str(i) for i in range(0, 256, 15)}),
                                           
                                html.H6(' ', style={'paddingTop' : 15}),
                                
                                daq.Slider(
                                    id='slider-BR',
                                    min=0,
                                    max=255,
                                    step=1,
                                    value=0,
                                    size=540,
                                    color='blue',
                                    marks={i: str(i) for i in range(0, 256, 15)}),
                                        
                                html.Div([
                                
                                    dmc.Button('BKG Correct',
                                                id='auto-btn',
                                                n_clicks=0,
                                                style={'font-size': '14px',
                                                       'width': '180px'}
                                                
                                )], style={'paddingTop' : 45,
                                           'margin-bottom': '10px',
                                           'textAlign':'center',
                                           'width': '220px',
                                           'margin':'auto'}),
                                
                                html.Div(children=[
                                    
                                    html.Div([
                                          
                                        html.H6('Gamma', 
                                                style={'paddingTop' : 15}),
                                        
                                        daq.Slider(
                                            id='slider-Gamma',
                                            min=0.01,
                                            max=2,
                                            step=0.01,
                                            value=1,
                                            size=270,
                                            color='DarkGrey',
                                            marks={i: str(i) for i in range(0, 3, 1)}),
                                        
                                        html.H6('Contrast', 
                                                style={'paddingTop' : 15}),
                                        
                                        daq.Slider(
                                            id='slider-Contrast',
                                            min=0.01,
                                            max=2,
                                            step=0.01,
                                            value=1,
                                            size=270,
                                            color='DarkGrey',
                                            marks={i: str(i) for i in range(0, 3, 1)}),
                                        
                                        html.H6('Denoise', 
                                                style={'paddingTop' : 15}),
                                        
                                        daq.Slider(
                                            id='slider-DI',
                                            min=0,
                                            max=50,
                                            step=1,
                                            value=0,
                                            size=270,
                                            color='DarkGrey',
                                            marks={i: str(i) for i in range(0, 60, 10)})
                                        
                                        ]),
                                    
                                    html.Div([
                                        
                                        html.H6('Rotate Image', 
                                                style={'paddingTop' : 15,
                                                       'textAlign':'center',
                                                       'height' : 40,
                                                       'width' : 200}),
                                        
                                        html.Div([
                                        
                                            dmc.Button(id='rotate_left',
                                                       radius= 1,
                                                       size = 'xs',
                                                       style={'width' : 55},
                                                       leftIcon=[
                                                            DashIconify(
                                                            icon="carbon:rotate-counterclockwise-alt",
                                                            width=35,
                                                            style={'paddingLeft' : 10})
                                                        ]),
                                            
                                            dmc.Button(id='rotate_right',
                                                       radius= 1,
                                                       size = 'xs',
                                                       style={'width' : 55},
                                                       leftIcon=[
                                                            DashIconify(
                                                            icon="carbon:rotate-clockwise-alt",
                                                            width=35,
                                                            style={'paddingLeft' : 10})
                                                        ]),
                                            
                                            dmc.Button(id='flip_hor',
                                                       radius= 1,
                                                       size = 'xs',
                                                       style={'width' : 55},
                                                       leftIcon=[
                                                            DashIconify(
                                                            icon="eva:flip-2-fill",
                                                            width=30,
                                                            style={'paddingLeft' : 10})
                                                        ]),
                                            
                                            dmc.Button(id='flip_ver',
                                                       radius= 1,
                                                       size = 'xs',
                                                       style={'width' : 55},
                                                       leftIcon=[
                                                            DashIconify(
                                                            id='rotate_left',
                                                            icon="eva:flip-fill",
                                                            width=29,
                                                            style={'paddingLeft' : 10})
                                                        ])
                                        
                                        ], style={'paddingBottom' : 15,
                                                  'height' : 30,
                                                  'width' : 200,
                                                  'display':'flex',
                                                  'justify-content':'space-around'}),
                                        
                                                  
                                        html.Div([
                                                  
                                            daq.Knob(id='rotate-knob',
                                                     min = -150,
                                                     max = 150,
                                                     size = 120, 
                                                     value = 0,
                                                     color = '#e6e6e6',
                                                     scale={'labelInterval': 1, 
                                                            'interval': 30})
                                        
                                        ], style={'textAlign' : 'center'})
                                    ]),

                                ], style={'display':'flex',
                                          'justify-content':'space-between'}),
                                     
                                html.Div([
                                          
                                    dmc.Button('Reset Image',
                                                id='reset-btn',
                                                n_clicks=0,
                                                style={'font-size': '14px',
                                                       'width': '180px'})
                                
                                ], style={'paddingTop' : 0,
                                          'margin-bottom': '10px',
                                          'textAlign':'center',
                                          'width': '220px',
                                          'margin':'auto'})
                                     
                            ])]
                            
                        ),
                    
                        dcc.Tab(
                            label='Image Selections',
                            value='selections',
                            
                            style={'borderBottom': '1px solid #d6d6d6',
                                   'padding': '6px',
                                   'fontWeight': 'bold',
                                   'align-items': 'center'},
                            
                            selected_style={'borderTop': '1px solid #d6d6d6',
                                            'borderBottom': '1px solid #d6d6d6',
                                            'backgroundColor': '#228bee',
                                            'color': 'white',
                                            'fontWeight': 'bold',
                                            'padding': '6px',
                                            'align-items': 'center',
                                            'justify-content' : 'center'},
                            
                            children=[
                                
                                html.Div([
                                        
                                    html.Div([
                                        
                                        html.Div([
                                            
                                            html.H6('Selection type', 
                                                    style={'paddingTop' : 15}),
                                                
                                                dcc.Dropdown(
                                                    ['Rectangle', 'Lasso', 'Line'], 
                                                    'Rectangle', 
                                                    clearable=False,
                                                    searchable=False,
                                                    id='method-dropdown'),
                                                      
                                            html.H6('DNA fiber type',
                                                    style={'paddingTop' : 10}),
                                                
                                                dcc.Dropdown(
                                                    fiber_dropdown_images('R','G'),
                                                    DNA_fiber_types[0], 
                                                    clearable=False,
                                                    searchable=False,
                                                    id='fiber-dropdown')
                                            
                                        ], style={'width': '256px',
                                                  'paddingRight' : 25,
                                                  'paddingBottom' : 20}),
                                        
                                        html.Div([
                                            
                                            html.H6('Border width', 
                                                    style={'paddingTop' : 14}),
                                            
                                            dbc.Input(type="number",
                                                      id="border_w",
                                                      min=0.25,
                                                      max=3, 
                                                      step=0.25,
                                                      value=0.5,
                                                      style={"width": 70}),
                                            
                                            html.H6('Max fiber width', 
                                                    style={'paddingTop' : 9}),
                                            
                                            dbc.Input(type="number",
                                                      id="max_fw",
                                                      min=1,
                                                      step=1,
                                                      value=20,
                                                      style={"width": 70}),
                                            
                                            
                                        ], style={'paddingRight' : 25}),
                                        
                                        html.Div([
                                            
                                            html.H6('Border color', 
                                                    style={'paddingTop' : 14}),
                                            
                                            dbc.Input(
                                                type="color",
                                                id="border_color",
                                                value="#ffffff",
                                                style={"width": 110, "height": 35}),
                                            
                                            html.H6('Show overlay', 
                                                    style={'paddingTop' : 11,
                                                           'paddingBottom' : 5}),
                                            
                                            daq.BooleanSwitch(id='overlay-switch',
                                                              on=False),
                                            
                                        ])
                                        
                                    ], className='flex-container'),
                                
                                ]),
                                
                                html.Div([
                                    
                                    html.Div([
                                        
                                        html.H6('Selected Fiber Data Table', 
                                                style={'paddingBottom' : 20,
                                                       'paddingRight' : 80}),
                                    
                                        html.Div([
                                            
                                                dmc.Button("Download CSV", 
                                                           id="btn_csv"),
                                                                          
                                                dcc.Download(id="download-dataframe-csv"),
                                                
                                        ],style={'paddingTop' : 4})

                                    ], className='flex-container'),
                                    
                                    dash_table.DataTable(
                                        id="annotations-table",
                                        columns=[
                                            
                                            dict(name=n,
                                                id=n,
                                                presentation=("input"))
                                            for n in columns
                                        
                                        ],
                                        editable=True,
                                        fill_width=True,
                                        page_action="native",
                                        page_current=0,
                                        page_size=9,
                                        style_data={"height": 15},
                                        style_cell={
                                            "textAlign": "left",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                            "maxWidth": 0,
                                        }
                                    
                                    ),
                                    
                                ])
                                
                            ]
                        )
                        
                    ]
                    
                )
                
            ], className='tab-div')
            
        ], className='flex-item-left'),

    html.Div(children=[
                                          
        html.Div(
                
            children=[
                
                html.H4('Image Used - Output', style={"textAlign": "center",
                                                      'paddingBottom' : 50,
                                                      'paddingTop' : 50,
                                                      'paddingRight' : 25}),
                
                dcc.Loading(
                    id='loading-op',
                    type='dot',
                    children=html.Div([
                        
                        dcc.Graph(id='out-op-img', 
                                  figure=fig,
                                  config={'displaylogo':False,
                                          'modeBarButtonsToAdd':['eraseshape'],
                                          'modeBarButtonsToRemove':[
                                              'zoom2d',
                                              'pan2d',
                                              'zoomIn2d',
                                              'zoomOut2d',
                                              'autoScale2d',
                                              'resetScale2d']})
                        
                    ],style={'paddingRight' : 25})
                )
                
            ]
                
        ),
        
        html.Div(
                
            children=[
                
                html.H4(' ',
                        id='Selected_Fiber_Title', 
                        style={"textAlign": "center",
                               'paddingBottom' : 15,
                               'paddingTop' : 50,
                               'paddingRight' : 20}),
                
                dcc.Loading(
                    id='loading-sel',
                    type='dot',
                    children=html.Div(
                        
                        dcc.Graph(id='sel-op-img', 
                                  figure=blank_fig(),
                                  config={'displayModeBar' : False})
                        
                    )
                ),
                
            ], style={'width': '128px','paddingRight' : 20}
                
        )
        
    ], className='flex-container')

], className='flex-container')



@app.callback(
    Output('out-op-img', 'relayoutData'),
    Input('image-processors-tabs', 'value'))

def reset_relayout(tab):
    
    if tab=='selections':
        
        return dash.no_update
    
    return None



@app.callback(
    Output('Selected_Fiber_Title', 'children'),
    Input('image-processors-tabs', 'value'))

def show_text_selection_title(tab):
    
    if tab=='selections':
        
        return "Selected Fiber"
    
    return " "



@app.callback(
    [Output("fiber-dropdown", "options"),
     Output('schema', 'src')],
    Input("color_label-dropdown", "value"))

def color_fiber_display(color_selection):
    
    if color_selection is None:
        
        return dash.no_update
    
    i=color_types.index(color_selection)
    c1=colors[i][0] ; c2=colors[i][1]
    src_path='/assets/Schema/Schema_' + c1 +'_' + c2 +'.png'
    
    return fiber_dropdown_images(c1,c2), src_path



@app.callback(Output('slider-CR', 'value'),
              Output('slider-GR', 'value'),
              Output('slider-BR', 'value'),
              Output('slider-Gamma', 'value'),
              Output('slider-Contrast', 'value'),
              Output('slider-DI', 'value'),
              Input('image-processors-tabs', 'value'),
              Input('reset-btn', 'n_clicks'),
              Input('auto-btn', 'n_clicks'),
              Input("color_label-dropdown", "value"),
              Input('upload-image', 'contents'),
              State('out-op-img', 'figure'),
              State('upload-image', 'filename'))

def autocorrect(tab,btn1,btn2,color_selection,contents,filenames,dates):
    
    if contents is None:
        
        return dash.no_update
    
    if tab !='operators':
        
        return dash.no_update
    
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    if 'reset-btn' in changed_id:
        
        return 0,0,0,1,1,0
        
    elif 'auto-btn' in changed_id:

        i=color_types.index(color_selection)
        c1=colors[i][0] ; c2=colors[i][1]
        
        imsrc=parse_contents(contents, filenames, dates)
        imo=ImageOperations(image_file_src=imsrc)

        return imo.auto_correct_operation(c1,c2)
    
    else:
        
        return dash.no_update



@app.callback(
    Output('out-op-img', 'figure'),
    [Input('upload-image', 'contents'),
     Input("slider-Gamma", "value"),
     Input("slider-CR", "value"),
     Input("slider-GR", "value"),
     Input("slider-BR", "value"),
     Input("slider-DI", "value"),
     Input("slider-Contrast", "value"),
     Input('image-processors-tabs', 'value'),
     Input('method-dropdown', 'value'),
     State('out-op-img', 'figure'),
     State('upload-image', 'filename')])

def get_operated_image(contents, gam, CR, GR, BR, DI, con, tab, method, filenames, dates):
    
    if contents is not None:
        
        imsrc=parse_contents(contents, filenames, dates)
        imo=ImageOperations(image_file_src=imsrc)
        out_img=imo.read_operation()
        
        if gam !=1:
        
            out_img=imo.gamma_operation(thresh_val=gam)
            
        if CR > 0:
        
            out_img=imo.CR_operation(thresh_val=CR)
            
        if GR > 0:
        
            out_img=imo.GR_operation(thresh_val=GR)
            
        if BR > 0:
        
            out_img=imo.BR_operation(thresh_val=BR)
            
        if DI > 0:
        
            out_img=imo.denoiseI_operation(thresh_val=DI)
            
        if con > 1:
        
            out_img=imo.contrast_operation(thresh_val=con)

        out_image_fig=px.imshow(out_img)
        out_image_fig.update_layout(
            coloraxis_showscale=False, 
            width=1000, height=750, 
            margin=dict(l=0, r=0, b=0, t=0)
        )
        out_image_fig.update_traces(hoverinfo='none', hovertemplate='')
        out_image_fig.update_xaxes(showticklabels=False)
        out_image_fig.update_yaxes(showticklabels=False)
        out_image_fig.update_layout(dragmode=False)
        
        if tab=='selections':
            
            if method=='Rectangle':
                
                out_image_fig.update_layout(dragmode='drawrect',
            newshape=dict(line={"color": "#0066ff", "width": 1.5, "dash": "solid"}))
                
            if method=='Lasso':
                
                out_image_fig.update_layout(dragmode='drawclosedpath',
            newshape=dict(line={"color": "#0066ff", "width": 1.5, "dash": "solid"}))
                
            if method=='Line':
                
                out_image_fig.update_layout(dragmode='drawline',
            newshape=dict(line={"color": "#0066ff", "width": 1.5, "dash": "solid"}))
                    
        return out_image_fig
    
    else:
        
        return dash.no_update



@app.callback(
    [Output("annotations-table", "data"),
     Output('shape_number', 'data'), 
     Output('shape_coords', 'data')], 
    [Input('out-op-img', 'relayoutData'),
     Input('out-op-img', 'figure'),
     Input('image-processors-tabs', 'value'),
     Input('fiber-dropdown', 'value'),
     Input('shape_coords', 'data'),
     Input('shape_number', 'data')],
    State("annotations-table", "data"),prevent_initial_call=True)

def shape_added(fig_data, fig, tab, fiber, s_coords, shape_number, new_row): 
    
    if tab=='selections':
        
        nparr=np.frombuffer(
            base64.b64decode(fig['data'][0]['source'][22:]), np.uint8)
        
        img=cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imo=ImageOperations(image_file_src=img)
        
        if fig_data is None:
            
            return None, None, None
        
        if fiber is None:
            
            return None, None, None
        
        if 'shapes' in fig_data:
            
            shape_n = len(fig_data["shapes"])
            
            last_shape=fig_data["shapes"][-1]
            x0, y0=int(last_shape["x0"]), int(last_shape["y0"])
            x1, y1=int(last_shape["x1"]), int(last_shape["y1"])
            
            if x0 > x1:
                
                x0, x1=x1, x0
                
            if y0 > y1:
                
                y0, y1=y1, y0
            
            Length=int(abs(y1 - y0))
            Width=int(abs(x1 - x0))
            ratio=imo.G_R_operation(x0, x1, y0, y1)
            
            if new_row is None:
            
                n=0
                new_row=[{'Fiber':n, 
                            'Type':fiber, 
                            'Length': Length, 
                            'Width': Width, 
                            'Segments':ratio}]
                
            else:
                
                if shape_n < shape_number:
                    
                    shape_coord=[]; table_coord=[]
                    
                    for shape in fig_data["shapes"]:
                        
                        x0, y0=int(shape["x0"]), int(shape["y0"])
                        x1, y1=int(shape["x1"]), int(shape["y1"])
                        
                        if x0 > x1:
                            
                            x0, x1=x1, x0
                            
                        if y0 > y1:
                            
                            y0, y1=y1, y0
                        
                        shape_coord +=[[x0,x1,y0,y1]]
                    
                    for coord in s_coords:
                            
                        table_coord +=[[coord['x0'],
                                         coord['x1'],
                                         coord['y0'],
                                         coord['y1']]]
                            
                    for i in table_coord:
                        
                        if i not in shape_coord:
                            
                            x0=i[0] ; x1=i[1] ; y0=i[2] ; y1=i[3]
                            
                    for coord in s_coords:
                        
                        if [coord['x0'],coord['x1'],coord['y0'],coord['y1']]==[x0,x1,y0,y1]:
                            
                            new_row=list(filter(lambda i: i['Fiber'] !=coord['n'], new_row))
                            s_coords=list(filter(lambda i: i['n'] !=coord['n'], s_coords))

                            return new_row, len(fig_data["shapes"]), s_coords
                        
                if new_row[-1]=={'Fiber':new_row[-1]['Fiber'],
                                   'Type':fiber, 
                                   'Length': Length, 
                                   'Width': Width, 
                                   'Segments':ratio}:
                    
                    return dash.no_update
                
                n=new_row[-1]['Fiber'] + 1
                
                new_row.append({'Fiber':n, 
                                'Type':fiber, 
                                'Length': Length, 
                                'Width': Width, 
                                'Segments':ratio})
            
        elif re.match("shapes\[[0-9]+\].x0", list(fig_data.keys())[0]):
            
            shape_n = shape_number
            
            for key, val in fig_data.items():
                
                shape_nb, coord=key.split(".")
                shape_nb=shape_nb.split(".")[0].split("[")[-1].split("]")[0]
                
                if coord=='x0':
                    
                    x0=int(fig_data[key])
                    
                elif coord=='x1':
                    
                    x1=int(fig_data[key])
                
                elif coord=='y0':
                    
                    y0=int(fig_data[key])
                
                elif coord=='y1':
                    
                    y1=int(fig_data[key])
            
            if x0 > x1:
                
                x0, x1=x1, x0
                
            if y0 > y1:
                
                y0, y1=y1, y0
            
            Length=int(abs(y1 - y0))
            Width=int(abs(x1 - x0))
            ratio=imo.G_R_operation(x0, x1, y0, y1)
            n=int(shape_nb)
            
            new_row[int(shape_nb)]['Fiber']=n
            new_row[int(shape_nb)]['Type']=fiber
            new_row[int(shape_nb)]['Length']=Length
            new_row[int(shape_nb)]['Width']=Width
            new_row[int(shape_nb)]['Segments']=ratio
        
            if [s_coords[-1]['x0'],s_coords[-1]['y0'],s_coords[-1]['x1'],s_coords[-1]['y1']] \
                == [x0,y0,x1,y1]:
                
                dash.no_update
        
        if s_coords is None:
            
            s_coords=[{'n':n, 'x0':x0, 'y0': y0, 'x1': x1, 'y1':y1}]
            
        else:
            
            s_coords.append({'n':n, 'x0':x0, 'y0': y0, 'x1': x1, 'y1':y1})
        
        return new_row, shape_n, s_coords
    
    else:
        
        return None, None, None

@app.callback(
    Output('sel-op-img', 'figure'), 
    [Input('out-op-img', 'relayoutData'),
     Input('out-op-img', 'figure'),
     Input('image-processors-tabs', 'value'),
     Input('shape_coords', 'data')],prevent_initial_call=True)

def selection_fiber_image(fig_data, fig, tab, shape_coords): 
    
    if tab=='selections':
        
        if fig_data is None:
            
            return blank_fig()
        
        nparr=np.frombuffer(base64.b64decode(fig['data'][0]['source'][22:]), np.uint8)
        img=cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imo=ImageOperations(image_file_src=img)
        out_img=imo.read_operation()
        
        x0, y0=shape_coords[-1]['x0'], shape_coords[-1]['y0']
        x1, y1=shape_coords[-1]['x1'], shape_coords[-1]['y1']
        
        out_img=imo.crop_operation(x0,x1,y0,y1)
        out_image_fig=px.imshow(out_img)
        
        out_image_fig.update_layout(height=750,
            coloraxis_showscale=False, 
            margin=dict(l=0, r=0, b=0, t=0)
        )
        
        out_image_fig.update_traces(hoverinfo='none', hovertemplate='')
        out_image_fig.update_xaxes(showticklabels=False)
        out_image_fig.update_yaxes(showticklabels=False)
        out_image_fig.update_layout(dragmode=False)
        
        return out_image_fig
    
    else:
        
        return blank_fig()
        
@app.callback(
    Output("annotations-table", "style_data_conditional"),
    Input('shape_number', 'data'),
    Input('out-op-img', 'hoverData'),
    Input('shape_coords', 'data')
)

def style_selected_rows(shape_number, hover_data, shape_coords):
    
    if shape_number is None:
        
        return dash.no_update
    
    if hover_data is not None:
        
        x0=hover_data["points"][0]["x"] ; y0=hover_data["points"][0]["y"]
        
        for i in range(len(shape_coords)):
            
            if x0 >=shape_coords[i]['x0'] and x0 <=shape_coords[i]['x1']:
                
                if y0 >=shape_coords[i]['y0'] and y0 <=shape_coords[i]['y1']:
                    
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{{Fiber}}={}'.format(shape_coords[i]['n']),
                            },
                            'backgroundColor': '#0074D9',
                            'color': 'white'
                        }
                    ]
    
                    return style_data_conditional
    
if __name__=='__main__':
    app.run_server(debug=True)