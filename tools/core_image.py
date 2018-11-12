import os
import re
import json
import sys

import matplotlib
import matplotlib.pyplot as plt

import colorsys

configuration = {}

other_items = {
    'bottom_label': '',
    'top_label': '', 
}


def deck_to_u_loading(deck_file_path):

    # Imports whole deck file as list of lines
    # this may not work for very long output files
    with open(deck_file_path, 'r') as deck_file:
        deck_lines = deck_file.readlines()

    line_id = re.compile(r'(?<=!)\w+') # matches str following '!' in comment
    univ_id = re.compile(r'(?<=fill\=)\d+') # matches univ. following 'fill='

    universe_loading = {}

    for line in deck_lines:

        # Get univ id after 'fill=' only in the core config section

        if '!' in line and univ_id.search(line):
            core_position = line_id.findall(line)[0]
            universe = univ_id.findall(line)[0]

            universe_loading[core_position] = universe


    return universe_loading


def deck_to_k(deck_file_poth):

    with open(deck_file_path, 'r') as deck_file:
        deck_lines = deck_file.readlines()

    for line in deck_lines:
        if 'final result' in line:
            final_result_line = line.split()
            break

    k = float(final_result_line[0])
    err = float(final_result_line[1])


def u_loading_to_loading(universe_loading):

    loading = universe_loading

    special_universes_dict = {
        '100' : '',
        '102' : 'G',
        '700' : 'SRC',
        '801' : 'SAFE',
        '802' : 'SHIM',
        '900' : 'REG',
    }

    for position, load in universe_loading.items():
        if load in special_universes_dict.keys():
            loading[position] = special_universes_dict[load]

    return loading


def dollars(k, beff=0.0075, precision=4):
    if k == 0:
        return 0

    dollar_value = ((k-1)/k)/beff

    return round(dollar_value, precision)


def dollar_with_error(k, err, precision=4):

    dollar_value = round(dollars(k), precision)
    error_plus = round(dollars(k+err), precision)
    error_minus = round(dollars(k-err), precision)

    return (dollar_value, error_plus, error_minus)


def construct_core_position_origins():
    with open('K:/AT/Sheetpy/tools/core_image/origins.json') as origins_file:
        origins_cm = json.load(origins_file)

    origins_in = {}

    for position, xy in origins_cm.items():
        origins_in[position] = (xy[0]/2.54 , xy[1]/2.54)

    return origins_in




# setting origin to center of images 
# 12 inches, 12 inches from corner
# And scaling it to 40 pixels per inch
# hard coding in pixel -> image coordinates
# Because it's just a scaling factor + a translation
# And I can't imagine using anything else
def in_coords_to_px(in_x, in_y):
    px_x = (in_x + 12)*40
    px_y = (12 - in_y)*40

    px_x_round = round(px_x, 7)
    px_y_round = round(px_y, 7)

    return (px_x_round, px_y_round)

def in_to_px(inches):
    px = inches*40
    return round(px, 7)




# takes x, y, and radius in inches
def circle(x, 
           y, 
           radius = 0.7525, # Radius in inches of grid plate holes
           fill = 'none',
           stroke_color = '#000000',
           stroke_size = 1.5):
    
    cx, cy = in_coords_to_px(x, y)
    cr = in_to_px(radius)

    circle_string = (
        f'<circle fill="{fill}" '
        f'stroke="{stroke_color}" '
        f'stroke-width="{stroke_size}" '
        'stroke-linecap="round" '
        'stroke-linejoin="round" '
        'stroke-miterlimit="10" '
        f'cx="{cx}" '
        f'cy="{cy}" '
        f'r="{cr}"'
        '/>\n'
    )

    return circle_string


def label(x,
          y,
          text_content,
          font_size,
          color = '#000000',
          anchor = 'middle'):
    
    lx, ly = in_coords_to_px(x, y)

    label_string = (
        '<text '
        'alignment-baseline="middle" '
        f'x="{lx}" '
        f'y="{ly}" '
        """font-family="'Y14.5M-2009'" """
        f'font-size="{font_size}px" '
        f'text-anchor="{anchor}" '
        f'fill="{color}" '
        f'>{text_content}</text>\n'
    )

    return label_string



def svg_save(file_path, contents):
    file = open(file_path, 'w')
    file.write(contents)
    file.close()

def svg_save_and_open(file_path, contents):
    svg_save(file_path, contents)

    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file_path))
    elif os.name == 'nt':
        os.startfile(file_path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', file_path))




def default_colors_into_config(loading):

    element_colors = {
        'steel': '#DB45FF',
        'aluminum': '#48FFBD',
        'G': '#AAAAAA',
        'SAFE': '#FFE600',
        'SHIM': '#FFE600',
        'REG': '#FFE600',
        'SRC': '#4A90FF',
        'W': 'none',
        '': 'none'
    }

    for position, load in loading.items():

        if load in ('SAFE','SHIM','REG','SRC','G','W', ''):
            configuration[position]['color'] = element_colors[load]

        else:

            if int(load) < 7000:
                configuration[position]['color'] = element_colors['aluminum']

            else:
                configuration[position]['color'] = element_colors['steel']



def non_fuel_color_map_compatible_colors_into_config():
    graphite_color = '#AAAAAA'
    non_fuel_color = '#666666'

    for pos, pos_info in configuration.items():
        
        if pos_info['element'] == 'G':
            configuration[pos]['color'] = graphite_color

        elif pos_info['element'] in ('SAFE', 'SHIM', 'REG', 'SRC'):
            configuration[pos]['color'] = non_fuel_color





def color_hex_to_hsl(color):

    # strips the '#'
    hex_color = color[1:]
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2 ,4))

    h, l, s = colorsys.rgb_to_hls(r, g, b)

    return (h, s, l)



def color_dark(color, threshold = 100):

    h, s, l = color_hex_to_hsl(color)

    if l < threshold:
        return True


def config_dark_color_invert():
    for pos, pos_info in configuration.items():

        if pos_info['color'] != 'none':
            if color_dark(pos_info['color']):
                pos_info['invert'] = True


# SN = 'center' or w/e?
# in another function for construction probably

def configuration_to_core_pos_svg_substring():

    svg = []
    o = construct_core_position_origins()

    for position, pos_info in configuration.items():
        color = '#000000'

        if 'invert' in pos_info:
            color = '#FFFFFF'

        # circle with fill
        svg.append(
            circle(*o[position], 
                   fill=pos_info['color']))

        # center label
        if pos_info['center'] != '':
            svg.append(
                label(*o[position], pos_info['center'], 20, color=color))

        # bottom label
        if pos_info['bottom'] != '':
            
            x, ly = o[position]
            y = ly - 0.45

            svg.append(
                label(x, y, pos_info['bottom'], 13, color=color))

        # top label
        if pos_info['top'] != '':
            
            x, ly = o[position]
            y = ly + 0.45

            svg.append(
                label(x, y, pos_info['top'], 13, color=color))


    svg_string = ''.join(svg)

    return svg_string


def configuration_to_svg_string():

    svg = []

    # start svg string
    header = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"'
        ' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
        '<svg version="1.1"\n' 
        '   id="core"\n'
        '   xmlns="http://www.w3.org/2000/svg"\n'
        '   width="960px"\n'
        '   height="960px">\n'
    )

    svg.append(header)
    

    # embed font
    svg.append(
        """<defs><style type="text/css">@font-face """
        """{font-family: 'Y14.5M-2009';font-weight: """
        """normal;font-style: normal; }</style></defs>"""
        '\n'
        )


    # Circles around core
    svg.append(
        circle(0, 0, radius=10.75))

    svg.append(
        circle(0, 0, radius=10.5))



    svg.append(configuration_to_core_pos_svg_substring())

    svg.append('</svg>')

    svg_string = ''.join(svg)

    return svg_string




# string core position and normalize 0-1 color map value
# in dict
def color_map_into_config_by_position(position_colors, 
                                      name = 'color_quantity', 
                                      normalize = False, 
                                      color_map = 'viridis'):

    max_value = next(iter(position_colors.values()))
    min_value = next(iter(position_colors.values()))
    if normalize:
        for pos, value in position_colors.items():
            if value > max_value:
                max_value = value
            elif value < min_value:
                min_value = value

    
    color_map = matplotlib.cm.get_cmap(color_map)

    for position, value in position_colors.items():

        configuration[position][name] = value

        if normalize:
            value = (value - min_value) / (max_value - min_value)
            configuration[position][f'n_{name}'] = value

        r, g, b = [int(x*255) for x in color_map(value)[:3]]
        color = '#{:02x}{:02x}{:02x}'.format(r,g,b)

        configuration[position]['color'] = color


def color_map_into_config(quantity, name = 'viridis'):
    
    color_map = matplotlib.cm.get_cmap(name)

    for pos, pos_info in configuration.items():

        if quantity in pos_info:

            value = pos_info[quantity]

            r, g, b = [int(x*255) for x in color_map(value)[:3]]
            color = '#{:02x}{:02x}{:02x}'.format(r,g,b)

            configuration[pos]['color'] = color


# dict of element SNs and other core components
# and value normalized 0-1 for color
# Has to be done after deck has been imported or w/e
# def element_color_map(element_colors, name = 'viridis'):



def fuel_mass_info_into_config():

    # Get fuel informationm
    with open('K:/AT/Sheetpy/tools/core_image/235mass.json') as mass_file:
        fuel_mass = json.load(mass_file)


    for position, pos_info in configuration.items():

        if pos_info['element'].isdigit():
            sn = pos_info['element']
            mass = fuel_mass[sn]

            configuration[position]['mass'] = mass


def quantity_to_svg_label(label, quantity):
    

    for pos, pos_info in configuration.items():
        if quantity in pos_info:
            pos_info[label] = pos_info[quantity]

    # TODO



def normalize_config_quantity(quantity):
        
    min_quantity = None
    max_quantity = None

    for pos, pos_info in configuration.items():
        if quantity in pos_info:
            if not max_quantity:
                max_quantity = pos_info[quantity]

            if not min_quantity:
                min_quantity = pos_info[quantity]

            if pos_info[quantity] > max_quantity:
                max_quantity = pos_info[quantity]

            elif pos_info[quantity] < min_quantity:
                min_quantity = pos_info[quantity]

    norm_quantity = f'n_{quantity}'

    for pos, pos_info in configuration.items():
        if quantity in pos_info:
            configuration[pos][norm_quantity] = (
                (pos_info[quantity] - min_quantity) / 
                (max_quantity - min_quantity))




def other_items_to_svg_string():
        
    svg = []

    # You might wanna abstract this with a dict
    # if it ever gets that complicated

    # bottom label
    if other_items['bottom_label'] != '':
        svg.append(
            label(0, -11.5, other_items['bottom_label'], 36))


    svg_string = ''.join(svg)
    return svg_string


def deck_to_image_default(deck_file_path, output_path):

    universe_loading = deck_to_u_loading(deck_file_path)
    loading = u_loading_to_loading(universe_loading)

    construct_configuration_from_loading_default(loading)

    svg = configuration_to_svg_string()

    svg_save_and_open(output_path, svg)


def deck_to_configuration_blank(deck_file_path):
    universe_loading = deck_to_u_loading(deck_file_path)
    loading = u_loading_to_loading(universe_loading)
    construct_configuration_blank_from_loading(loading)
    fuel_mass_info_into_config()
    normalize_config_quantity('mass')




def testing_max_color_map(deck_file_path, output_path):

    universe_loading = deck_to_u_loading(deck_file_path)
    loading = u_loading_to_loading(universe_loading)

    construct_configuration_from_loading_default(loading)
    
    fuel_mass_info_into_config()
    normalize_config_quantity('mass')
    color_map_into_config('n_mass')

    quantity_to_svg_label('top', 'mass')


    svg = configuration_to_svg_string()

    svg_save_and_open(output_path, svg)





def deck_to_loading(deck_file_path):

    universe_loading = deck_to_u_loading(deck_file_path)
    loading = u_loading_to_loading(universe_loading)

    return loading



def construct_configuration_blank_from_loading(loading):
    for position, element in loading.items():
        configuration[position] = {
            'top': '',
            'center': '',
            'bottom': '',
            'element': element,
            'position': position,
            'color': 'none',
        }


def construct_configuration_from_loading_default(loading):

    construct_configuration_blank_from_loading(loading)
    quantity_to_svg_label('center', 'element')
    quantity_to_svg_label('bottom', 'position')


    default_colors_into_config(loading)
    # non_fuel_color_map_compatible_colors_into_config() # fix this function yo


