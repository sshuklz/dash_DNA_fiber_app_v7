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
import skimage.transform

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

color_types=['T0 Red : T1 Green',
             'T0 Green : T1 Red',
             'T0 Red : T1 Blue',
             'T0 Blue : T1 Red',
             'T0 Green : T1 Blue',
             'T0 Blue : T1 Green',
             'T0 Red : T1 Green : FISH Blue',
            'T0 Green : T1 Red : FISH Blue',
            'T0 Red : T1 Blue : FISH Green',
            'T0 Blue : T1 Red : FISH Green',
            'T0 Green : T1 Blue : FISH Red',
            'T0 Blue : T1 Green : FISH Red']



colors=[['R','G'],['G','R'],['R','B'],['B','R'],['G','B'],['B','G'],
        ['R','G','F'],['G','R','F'],['R','B','F'],['B','R','F'],['G','B','F'],['B','G','F']]

df=pd.DataFrame(columns=['Fiber', 'Type', 'Length', 'Width', 'Segments'])

columns=['Fiber', 'Type', 'Length', 'Width', 'Segments']

color_options=[]
height_vals=[10,10,30,10,10,30]

for i in range(len(colors)):

    c1=colors[i][0] ; c2=colors[i][1]
    label_name = '_' + c1 + '_' + c2 + '.png'

    try:
        
        F=colors[i][2]
        label_name = '_' + c1 + '_' + c2 + '_' + F + '.png'
        
    except:
        
        pass
        

    color_options.append({
        
        "label": html.Div([
            
            html.Img(src="/assets/Color_options/Label" +
                     label_name, width = 280,height = 30),
            
            html.Div(color_types[i],
                     style={'font-size':15,'padding-left':10}),
        
        ], style={'display': 'flex',
                  'align-items': 'center', 
                  'justify-content': 'left'}),"value": color_types[i]
        
    })

def fiber_dropdown_images(c1,c2,F):

    fiber_options=[]

    for i in range(6):
    
        label_name = (DNA_fiber_types[i] + '_' + c1 + '_' + c2 + F + '.png')
    
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

legend = ("Segments abbreviations: \n\nG = green, R = red, B = blue, "
          "F = FISH label, \nOV = overlap, GP = gap, : = new segment\n\n")

app.layout=html.Div([
    
        html.Meta(charSet='UTF-8'),
        html.Meta(name='viewport', 
                  content='width=device-width, initial-scale=1.0'),
        
        dcc.Store(id='shape_coords', storage_type='memory'), 
        dcc.Store(id='shape_number', storage_type='memory'),
        dcc.Store(id='im_sliders', storage_type='memory', data = [0,0,0,1,1,0]),
        dcc.Store(id='im_rotation', storage_type='memory', data = 0),
        dcc.Store(id='im_flip', storage_type='memory', data = [False,False]),
        
        dcc.Download(id="download-dataframe-csv"),
        dcc.Download(id="download-plot-Image"),
        dcc.Download(id="download-sel-current"),
        dcc.Download(id="download-sel-all"),

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
                            label='1 - Label Details',
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
                            label='2 - Image Operations',
                            value='image_tab',
                            
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
                                    id='slider-RC',
                                    min=0,
                                    max=255,
                                    step=1,
                                    value=0,
                                    size=540,
                                    color='red',
                                    marks={i: str(i) for i in range(0, 256, 15)}),
                                
                                html.H6(' ', style={'paddingTop' : 15}),
                                
                                daq.Slider(
                                    id='slider-GC',
                                    min=0,
                                    max=255,
                                    step=1,
                                    value=0,
                                    size=540,
                                    color='green',
                                    marks={i: str(i) for i in range(0, 256, 15)}),
                                           
                                html.H6(' ', style={'paddingTop' : 15}),
                                
                                daq.Slider(
                                    id='slider-BC',
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
                                                       'paddingLeft' : 10,
                                                       'textAlign':'center',
                                                       'height' : 35,
                                                       'width' : 200}),
                                        
                                        html.Div([
                                                  
                                            daq.Knob(id='rotate_knob',
                                                     min = -150,
                                                     max = 150,
                                                     size = 110, 
                                                     value = 0,
                                                     color = '#e6e6e6',
                                                     
                                                     scale={'labelInterval': 1, 
                                                            'interval': 30})
                                        
                                        ], style={'height' : 150,
                                                  'paddingLeft' : 10}),
                                        
                                        dmc.Group(grow = True, children = [
                                        
                                            dmc.ActionIcon(
                                                
                                                DashIconify(
                                                    icon="charm:rotate-anti-clockwise",
                                                    width=20),
                                                
                                                id='rotate_left',
                                                radius= 6,
                                                size = 'md',
                                                color="blue", 
                                                variant="filled",
                                                style={'width' : 52}
                                                
                                            ),
                                            
                                            dmc.ActionIcon(
                                                
                                                DashIconify(
                                                    icon="charm:rotate-clockwise",
                                                    width=20),
                                                
                                                id='rotate_right',
                                                radius= 6,
                                                size = 'md',
                                                color="blue", 
                                                variant="filled",
                                                style={'width' : 52}
                                            
                                            ),
                                            
                                            dmc.ActionIcon(
                                                
                                                DashIconify(
                                                    icon="eva:flip-2-fill",
                                                    width=22),
                                                
                                                id='flip_hor',
                                                radius=6,
                                                size = 'md',
                                                color="blue", 
                                                variant="filled",
                                                style={'width' : 52}
                                                
                                            ),
                                            
                                            dmc.ActionIcon(
                                                
                                                DashIconify(
                                                     icon="eva:flip-fill",
                                                     width=22),
                                                
                                                id='flip_ver',
                                                radius=6,
                                                size = 'md',
                                                color="blue", 
                                                variant="filled",
                                                style={'width' : 52}
                                                       
                                            )
                                        
                                        ], style={'paddingTop' : 18,
                                                  'paddingBottom' : 55,
                                                  'height' : 30,
                                                  'width' : 200,
                                                  'display':'flex',
                                                  'textAlign': 'center',
                                                  'justify-content':'space-around'}),
                                        
                                                  

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
                            label='3 - Image Selections',
                            value='select_tab',
                            
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
                                            
                                            dmc.Tooltip(
                                                withArrow=True,
                                                position="bottom",
                                                placement="start",
                                                transition="fade",
                                                transitionDuration=200,
                                                arrowSize = 5,
                                                label='Changes will reset data table',
                                                
                                                children=[
                                                    
                                                    html.H6('Selection type', 
                                                            style={'paddingTop' : 15}),
                                                    
                                                ]),
                                            
                                            dcc.Dropdown(
                                                ['Rectangle','Lasso','Line'],
                                                'Rectangle', 
                                                clearable=False,
                                                searchable=False,
                                                id='method-dropdown'),
                                                      
                                            html.H6('DNA fiber type',
                                                    style={'paddingTop' : 10}),
                                                
                                            dcc.Dropdown(
                                                fiber_dropdown_images('R','G',''),
                                                DNA_fiber_types[0], 
                                                clearable=False,
                                                searchable=False,
                                                id='fiber-dropdown'),
                                            
                                            html.Div([
                                            
                                                dmc.Tooltip(
                                                    wrapLines=True,
                                                    width=540,
                                                    withArrow=True,
                                                    position="bottom",
                                                    placement="end",
                                                    transition="fade",
                                                    transitionDuration=200,
                                                    gutter = 10,
                                                    arrowSize = 5,
                                                    label=legend,
                                                    
                                                    children=[
                                                        
                                                        dmc.Button("Fiber table",
                                                                   size='xl',
                                                                   style={'width' : 230},
                                                                   leftIcon=[DashIconify(
                                                        icon="fluent:table-settings-28-filled")])
                                                        
                                                    ])
                                            
                                            ],style={'paddingTop' : 32})
                                            
                                        ], style={'width': '256px',
                                                  'paddingRight' : 20,
                                                  'paddingBottom' : 18}),
                                        
                                        html.Div([
                                            
                                            dmc.Tooltip(
                                                withArrow=True,
                                                position="bottom",
                                                placement="start",
                                                transition="fade",
                                                transitionDuration=200,
                                                arrowSize = 5,
                                                label='Changes will reset data table',
                                                
                                                children=[
                                                    
                                                    html.H6('Border width', 
                                                            style={'paddingTop' : 14}),
                                                    
                                                ]),
                                            
                                            dbc.Input(type="number",
                                                      id="border_w",
                                                      min=0.25,
                                                      max=3, 
                                                      step=0.25,
                                                      value=1.5,
                                                      style={"width": 70}),
                                            
                                            html.H6('Max fiber width', 
                                                    style={'paddingTop' : 9,
                                                           'width' : 139}),
                                            
                                            dbc.Input(type="number",
                                                      id="max_fw",
                                                      min=1,
                                                      step=1,
                                                      value=20,
                                                      style={"width": 70}),
                                            
                                            html.H6('Min gap size', 
                                                    style={'paddingTop' : 9}),
                                            
                                            dbc.Input(type="number",
                                                      id="min_gap",
                                                      min=1,
                                                      step=1,
                                                      value=5,
                                                      style={"width": 70}),
                                            
                                            
                                        ], style={'paddingRight' : 20,
                                                  'paddingBottom' : 0}),
                                        
                                        html.Div([
                                            
                                            dmc.Tooltip(
                                                withArrow=True,
                                                position="bottom",
                                                placement="start",
                                                transition="fade",
                                                transitionDuration=200,
                                                arrowSize = 5,
                                                label='Changes will reset data table',
                                                
                                                children=[
                                                    
                                                    html.H6('Border color', 
                                                            style={'paddingTop' : 14}),
                                                    
                                                ]),
                                            
                                            dbc.Input(
                                                type="color",
                                                id="border_color",
                                                value="#ffffff",
                                                style={"width": 110,
                                                       "height": 35}),
                                            
                                            html.H6('Cursor box', 
                                                    style={'paddingTop' : 11,
                                                           'paddingBottom' : 5}),
                                            
                                            dmc.Switch(
                                                size="md",
                                                radius="xl",
                                                label="Show",
                                                id='cursor-switch',
                                                checked=True
                                            ),
                                            
                                            html.H6('Fiber overlay', 
                                                    style={'paddingTop' : 16,
                                                           'paddingBottom' : 0}),
                                            
                                            dmc.Switch(
                                                size="md",
                                                radius="xl",
                                                label="Show",
                                                id='overlay-switch',
                                                checked=True,
                                                style={'height':30}
                                            )
                                            
                                        ])
                                        
                                    ], className='flex-container'),
                                
                                ]),
                                
                                html.Div([
                                    
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
                                        page_size=8,
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
                
                html.Div([
                
                    dcc.Graph(id='out-op-img', 
                              figure=fig,
                              
                              config={'displaylogo':False,
                                      
                                      'modeBarButtonsToAdd':[
                                          'eraseshape'],
                                      
                                      'modeBarButtonsToRemove':[
                                          'zoom2d',
                                          'pan2d',
                                          'zoomIn2d',
                                          'zoomOuT2d',
                                          'autoScale2d',
                                          'resetScale2d']}),
                
                    dcc.Tooltip(id="graph-tooltip",
                                loading_text = '',
                                style = {'height':16,
                                         'width':25,
                                         'font-size': 14}),
                
                ],style={'paddingRight' : 25}),
                
                html.Div(id='download  div'),

            ]
                
        ),
        
        html.Div(
                
            children=[
                
                html.H4(' ',
                        id='Selected_Fiber_Title', 
                        style={'textAlign' : 'center',
                               'paddingBottom' : 15,
                               'paddingTop' : 50,
                               'paddingRight' : 20}),
                
                html.Div(
                    
                    dcc.Graph(id='sel-op-img', 
                              figure=blank_fig(),
                              config={'displayModeBar' : False})
                    
                )
                
            ], style={'width': '130px','paddingRight' : 20,'paddingLeft' : 0}
                
        )
        
    ], className='flex-container')

], className='flex-container')



@app.callback(
    Output('out-op-img', 'relayoutData'),
    Input('image-processors-tabs', 'value'),
    Input('method-dropdown', 'value'),
    Input("border_color", "value"),
    Input("border_w", "value"),
    prevent_initial_call=True)

def reset_relayout(tab,shape_dropdown,color,width):
    
    ctx = dash.callback_context
    ctx_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if ctx_id == 'image-processors-tabs':
    
        if tab=='select_tab':
            
            return dash.no_update
        
        return None
    
    return None


@app.callback(
    Output("fiber-dropdown", "options"),
    Input('image-processors-tabs', 'value'),
    Input("color_label-dropdown", "value"))

def color_fiber_display(tab, color_selection):
    
    if color_selection is None:
        
        return dash.no_update
    
    if tab != 'select_tab':
    
        return dash.no_update
    
    i = color_types.index(color_selection)
    
    try:
        
        return fiber_dropdown_images(colors[i][0], 
                                     colors[i][1], 
                                     '_' + colors[i][2])
        
    except:
        
        return fiber_dropdown_images(colors[i][0], colors[i][1], '')
    
    



@app.callback(
    Output('schema', 'src'),
    Input('image-processors-tabs', 'value'),
    Input("color_label-dropdown", "value"))

def color_fiber_schema(tab, color_selection):
    
    if color_selection is None:
        
        return dash.no_update
    
    if tab != 'color_tab':
    
        return dash.no_update
    
    i=color_types.index(color_selection)
    
    try:
        
        return ('/assets/Schema/Schema_' + colors[i][0] + '_' + colors[i][1]
                + '_' + colors[i][2] +'.png')
        
    except:
        
        return '/assets/Schema/Schema_' + colors[i][0] + '_' + colors[i][1] +'.png'



@app.callback(Output('slider-RC', 'value'),
              Output('slider-GC', 'value'),
              Output('slider-BC', 'value'),
              Output('slider-Gamma', 'value'),
              Output('slider-Contrast', 'value'),
              Output('slider-DI', 'value'),
              Input('image-processors-tabs', 'value'),
              Input('reset-btn', 'n_clicks'),
              Input('auto-btn', 'n_clicks'),
              Input('rotate_knob', 'value'),
              Input("color_label-dropdown", "value"),
              Input('upload-image', 'contents'),
              State('out-op-img', 'figure'),
              State('upload-image', 'filename'))

def set_vals(tab,btn1,btn2,knob,color_selection,contents,filenames,dates):
    
    if contents is None:
        
        return dash.no_update
    
    if tab !='image_tab':
        
        return dash.no_update
    
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    if 'reset-btn' in changed_id:
        
        return 0,0,0,1,1,0
        
    if 'auto-btn' in changed_id:

        i=color_types.index(color_selection)
        c1=colors[i][0] ; c2=colors[i][1]
        imsrc=parse_contents(contents, filenames, dates)
        imo=ImageOperations(image_file_src=imsrc)
        
        try:

            return imo.auto_correct_operation(c1,c2,colors[i][2])
            
        except:
            
            return imo.auto_correct_operation(c1,c2,None)
        
    else:
        
        return dash.no_update



@app.callback(
    Output('out-op-img', 'figure'),
    Output('im_sliders', 'data'),
    Output('im_rotation', 'data'),
    Output('im_flip', 'data'),
    [Input('upload-image', 'contents'),
     Input('im_sliders', 'data'),
     Input("color_label-dropdown", "value"),
     Input("slider-Gamma", "value"),
     Input("slider-RC", "value"),
     Input("slider-GC", "value"),
     Input("slider-BC", "value"),
     Input("slider-DI", "value"),
     Input("slider-Contrast", "value"),
     Input('im_rotation', 'data'),
     Input('im_flip', 'data'),
     Input("rotate_left", "n_clicks"),
     Input("rotate_right", "n_clicks"),
     Input("flip_hor", "n_clicks"),
     Input("flip_ver", "n_clicks"),
     Input('rotate_knob', 'value'),
     Input('auto-btn', 'n_clicks'),
     Input('reset-btn', 'n_clicks'),
     Input('image-processors-tabs', 'value'),
     Input('method-dropdown', 'value'),
     Input("border_color", "value"),
     Input("border_w", "value"),
     State('out-op-img', 'figure'),
     State('upload-image', 'filename')],
    )

def get_operated_image(contents, sliders, color_selection, gam, RC, GC, BC, DI, con, rotation, flip, RL, RR, FH, FV, RF, auto, reset, tab, method, color, width, filenames, dates):
    
    if contents is not None:
        
        imsrc=parse_contents(contents, filenames, dates)
        imo=ImageOperations(image_file_src=imsrc)
        out_img=imo.read_operation()
        
        if tab =='image_tab':
            
            ctx = dash.callback_context
            ctx_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if ctx_id == 'auto-btn':
    
                i=color_types.index(color_selection)
                
                try:
                    
                    sliders = list(imo.auto_correct_operation(colors[i][0],
                                                              colors[i][1],
                                                              colors[i][2]))
                
                except:
                    
                    sliders = list(imo.auto_correct_operation(colors[i][0],
                                                              colors[i][1],
                                                              None))
            
            elif ctx_id == 'slider-RC':
            
                sliders[0] = RC
                
            elif ctx_id == 'slider-GC':
            
                sliders[1] = GC
                
            elif ctx_id == 'slider-BC':
            
                sliders[2] = BC
                
            elif ctx_id == 'slider-Gamma':
            
                sliders[3] = gam
                
            elif ctx_id == 'slider-Contrast':
            
                sliders[4] = con
                
            elif ctx_id == 'slider-DI':
            
                sliders[5] = DI
            
            elif ctx_id == 'rotate_left':
                
                rotation += 90
                
            elif ctx_id == 'rotate_right':
                
                rotation -= 90
                
            elif ctx_id == 'flip_hor':
                
                flip[0] = not flip[0]
    
            elif ctx_id == 'flip_ver':
                
                flip[1] = not flip[1]
                    
            elif ctx_id == 'reset-btn':
                
                rotation = 0 ; RF = 0 ; 
                flip = [False, False] ; sliders = [0,0,0,1,1,0]
        
        out_img=imo.color_operation(*sliders[:3])
        
        out_img=imo.transform_operation(rotation - RF , 
                                     flip,
                                     sliders[3],
                                     sliders[4],
                                     sliders[5])
        
        out_image_fig=px.imshow(out_img)
        
        out_image_fig.update_layout(
            coloraxis_showscale=False, 
            width=1000, height=750, 
            margin=dict(l=0, r=0, b=0, t=0)
        )
        
        out_image_fig.update_layout(hovermode=False)
        out_image_fig.update_layout(dragmode=False)
        
        out_image_fig.update_xaxes(showticklabels=False,
                                   zerolinecolor = 'rgba(0,0,0,0)')
        
        out_image_fig.update_yaxes(showticklabels=False,
                                   zerolinecolor = 'rgba(0,0,0,0)')
        
        out_image_fig.update_layout(plot_bgcolor='rgb(0,0,0)',
                                    paper_bgcolor='rgb(0,0,0)')
        
        if tab=='select_tab':
            
            out_image_fig.update_layout(hovermode='closest')
            out_image_fig.update_traces(hoverinfo='none', hovertemplate='')
            
            if method=='Rectangle':
                
                out_image_fig.update_layout(dragmode='drawrect',
            newshape=dict(line={"color": color, "width": width, "dash": "solid"}))
                
            elif method=='Lasso':
                
                out_image_fig.update_layout(dragmode='drawclosedpath',
            newshape=dict(line={"color": color, "width": width, "dash": "solid"}))
                
            elif method=='Line':
                
                out_image_fig.update_layout(dragmode='drawline',
            newshape=dict(line={"color": color, "width": width, "dash": "solid"}))
                    
        return out_image_fig, sliders, rotation, flip
    
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
    State("annotations-table", "data"),
    prevent_initial_call=True)

def shape_added(fig_data, fig, tab, fiber, s_coords, shape_number, new_row): 
    
    if tab=='select_tab':
        
        if fig_data is None:
            
            return None, None, None
        
        if fiber is None:
            
            return None, None, None
        
        nparr=np.frombuffer(
            base64.b64decode(fig['data'][0]['source'][22:]), np.uint8)
        
        img=cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imo=ImageOperations(image_file_src=img)
        
        if 'shapes' in fig_data:
            
            shape_n = len(fig_data["shapes"])
            
            x0, y0=int(fig_data["shapes"][-1]["x0"]), int(fig_data["shapes"][-1]["y0"])
            x1, y1=int(fig_data["shapes"][-1]["x1"]), int(fig_data["shapes"][-1]["y1"])
            
            if x0 > x1:
                
                x0, x1 = x1, x0
                
            if y0 > y1:
                
                y0, y1 = y1, y0
            
            Length=int(abs(x1 - x0))
            Width=int(abs(y1 - y0))
            
            if Length < Width:
                
                Length, Width = Width, Length
            
            if new_row is None:
            
                n=0
                new_row=[{'Fiber':n, 
                            'Type':fiber, 
                            'Length': Length, 
                            'Width': Width, 
                            'Segments':imo.G_R_operation(x0, x1, y0, y1)}]
                
            else:
                
                if shape_n < shape_number: #for annotation deletion
                    
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
                        
                if [new_row[-1]['Length'], new_row[-1]['Width'], new_row[-1]['Segments']] == [
                        Length, Width, imo.G_R_operation(x0, x1, y0, y1)]: #for fiber type change
                    
                    return dash.no_update
                
                n=new_row[-1]['Fiber'] + 1
                
                new_row.append({'Fiber':n, 
                                'Type':fiber, 
                                'Length': Length, 
                                'Width': Width, 
                                'Segments':imo.G_R_operation(x0, x1, y0, y1)})
            
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
            
            if [s_coords[-1]['x0'],
                s_coords[-1]['y0'],
                s_coords[-1]['x1'],
                s_coords[-1]['y1']]  == [x0,y0,x1,y1]:
                
                dash.no_update
            
            Length=int(abs(x1 - x0))
            Width=int(abs(y1 - y0))
            
            if Length < Width:
                
                Length, Width = Width, Length
            
            n=int(shape_nb)
            
            new_row[int(shape_nb)]['Fiber']=n
            new_row[int(shape_nb)]['Type']=fiber
            new_row[int(shape_nb)]['Length']=Length
            new_row[int(shape_nb)]['Width']=Width
            new_row[int(shape_nb)]['Segments']=imo.G_R_operation(x0, x1, y0, y1)

        if s_coords is None:
            
            s_coords=[{'n':n, 'x0':x0, 'y0': y0, 'x1': x1, 'y1':y1}]
            
        else:
            
            s_coords.append({'n':n, 'x0':x0, 'y0': y0, 'x1': x1, 'y1':y1})
        
        return new_row, shape_n, s_coords
    
    else:
        
        return None, None, None



@app.callback(
    Output('sel-op-img', 'figure'), 
    Output('Selected_Fiber_Title', 'children'),
    Output("annotations-table", "style_data_conditional"),
    [Input('out-op-img', 'relayoutData'),
     Input('out-op-img', 'figure'),
     Input('image-processors-tabs', 'value'),
     Input('out-op-img', 'hoverData'),
     Input('shape_coords', 'data'),
     Input("overlay-switch", "checked")],
    prevent_initial_call=True)

def selection_fiber_image(fig_data, fig, tab, hover_data, shape_coords, overlay): 
    
    if tab=='select_tab':
        
        if fig_data is None:
            
            return dash.no_update
        
        if shape_coords is None:
            
            return dash.no_update
        
        x0, y0=shape_coords[-1]['x0'], shape_coords[-1]['y0']
        x1, y1=shape_coords[-1]['x1'], shape_coords[-1]['y1']
        style_data_conditional = []
        
        if hover_data is not None:
            
            x0_h=hover_data["points"][0]["x"] ; y0_h=hover_data["points"][0]["y"]
            
            for i in range(len(shape_coords)):
                
                if x0_h >=shape_coords[i]['x0'] and x0_h <=shape_coords[i]['x1']:
                    
                    if y0_h >=shape_coords[i]['y0'] and y0_h <=shape_coords[i]['y1']:
                        
                        x0, x1=shape_coords[i]['x0'], shape_coords[i]['x1']
                        y0, y1=shape_coords[i]['y0'], shape_coords[i]['y1']
                        
                        style_data_conditional=[
                            
                            {
                                'if': {
                                    'filter_query': '{{Fiber}}={}'.format(shape_coords[i]['n']),
                                },
                                'backgroundColor': '#0074D9',
                                'color': 'white'
                            }
                        ]
        
        if overlay is False:
        
            return blank_fig(),' ', style_data_conditional
        
        nparr=np.frombuffer(base64.b64decode(fig['data'][0]['source'][22:]), 
                            np.uint8)
        
        img=cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        imo=ImageOperations(image_file_src=img)
        out_img=imo.read_operation()
        
        out_img = imo.crop_operation(x0,x1,y0,y1)
        
        if(x1-x0)>(y1-y0):
        
            out_img=skimage.transform.rotate(out_img,-90,resize=True)
        
        out_image_fig=px.imshow(out_img)
        
        out_image_fig.update_layout(height=750,
            coloraxis_showscale=False, 
            margin=dict(l=0, r=0, b=0, t=0))
        
        out_image_fig.update_layout(hovermode=False)
        out_image_fig.update_xaxes(showticklabels=False)
        out_image_fig.update_yaxes(showticklabels=False)
        out_image_fig.update_layout(dragmode=False)

        return out_image_fig, "Selected Fiber", style_data_conditional
    
    else:
        
        return blank_fig(), ' ', [] 
        
    
    
@app.callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input('out-op-img', 'hoverData'),
    Input('shape_coords', 'data'),
    Input("cursor-switch", "checked"))

def style_selected_rows(hover_data, shape_coords, cursor):
    
    if shape_coords is None:
        
        return dash.no_update
    
    if cursor is False:
    
        return dash.no_update
    
    if hover_data is not None:
        
        x0=hover_data["points"][0]["x"] ; y0=hover_data["points"][0]["y"]
        bbox = hover_data["points"][0]["bbox"]
        
        for i in range(len(shape_coords)):
            
            if x0 >=shape_coords[i]['x0'] and x0 <=shape_coords[i]['x1']:
                
                if y0 >=shape_coords[i]['y0'] and y0 <=shape_coords[i]['y1']:
                    
                    if shape_coords[i]['n'] < 10:
                    
                        children = [html.P([f"{shape_coords[i]['n']}"],
                                           className='flex-text_0-9')]
                        
                    elif shape_coords[i]['n'] < 100:
                    
                        children = [html.P([f"{shape_coords[i]['n']}"],
                                           className='flex-text_10-99')]
                        
                    else:
                        
                        children = [html.P([f"{shape_coords[i]['n'] + 100}"],
                                           className='flex-text_99-plus')]
                    
                    return True, bbox, children
        
        return False, None, None
            
    else:
        
        return False, None, None
    


@app.callback(
    Output('download  div', 'children'), 
    Input('image-processors-tabs', 'value'))

def show_text_selection_title(tab):
    
    if tab=='select_tab':
        
        return  html.Div([
            
            dmc.Group(grow = True, spacing = 'xs', children =[

                dmc.Button("Data table CSV", 
                           id="btn_csv",
                           style={'width' : 246},
                           n_clicks=0,
                           leftIcon=[DashIconify(
                                icon="akar-icons:download")
                            ]),
                
                dmc.Button("annotated Image PNG", 
                           id="btn_im",
                           style={'width' : 246},
                           n_clicks=0,
                           leftIcon=[DashIconify(
                                icon="akar-icons:download")
                            ]),
                
                dmc.Button("current Fiber plot", 
                           id="btn_sel_c",
                           style={'width' : 246},
                           n_clicks=0,
                           leftIcon=[DashIconify(
                                icon="akar-icons:download")
                            ]),
                                          
                dmc.Button("all fiber plots", 
                           id="btn_sel_a",
                           style={'width' : 246},
                           n_clicks=0,
                           leftIcon=[DashIconify(
                                icon="akar-icons:download")
                            ])
                
            ],style = {'width' : 996, 'paddingTop': 5, 'justify-content': 'center'})

        ])
    
    return " ", None
    


if __name__=='__main__':
    app.run_server(debug=True)