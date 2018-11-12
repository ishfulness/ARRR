import re
import os
import subprocess

import tools.name as name
import tools.core_image as core_image

def print_warning(warning_string):
    ansi_color_string = u'\u001b[40m\u001b[33m' + warning_string + u'\u001b[0m'
    print(ansi_color_string)


def print_error(error_string):
    ansi_color_string = u'\u001b[40m\u001b[35m' + error_string + u'\u001b[0m'
    print(ansi_color_string)


def print_color(raw_string):

    color_string = raw_string

    ansi_color = {
        'm': '\u001b[40m\u001b[35m',
        'y': '\u001b[40m\u001b[33m',
    }

    for match in re.findall(r'([@](.+?)[@])', color_string):

        ansi_prefix = ansi_color[match[0][1]]
        colored_substring = ansi_prefix + match[1][1:] + u'\u001b[0m'
        color_string = color_string.replace(match[0], colored_substring)

    print(color_string)


def read_deck_from_file(file_path):
    with open(file_path, 'r') as deck_file:
        deck_lines = deck_file.readlines()

    return deck_lines

# returns path to file saved
def save_input_deck(deck_lines, 
                    save_directory = 'K:/AT/Sheetpy/inputs', 
                    name_suffix = '',
                    file_name = None, 
                    job = False):

    if file_name:
        i_name = file_name + name_suffix
        print_color(f'Saving input deck with file name: @y{file_name}@')

        if os.path.isfile(f'{save_directory}/{i_name}.i'):
            print_error('Collision detected in name selection')
            
            random_string = name.rand_string(10)
            print_color(f'@mAppending random string@: @y{random_string}@')

            i_name = file_name + '_' + random_string

    else:
        i_name_spaces = name.generate(job = job)
        i_name = name.s_to_u(i_name_spaces) + name_suffix

        if os.path.isfile(f'{save_directory}/{i_name}.i'):
            print_error('Collision detected in name generation')
            print_color(f'@y{i_name}@ @malready exists in directory@')
            print('Generating new name')

            idx = 0
            while(os.path.isfile(f'{save_directory}/{i_name}.i') and idx<100):
                idx += 1
                i_name_spaces = name.generate(job = job)
                i_name = name.s_to_u(i_name_spaces) + name_suffix
                print_color(f'{idx} - Trying name: @y{i_name}@')

        print_color('Saving input deck with file name: '
                    f'@y{i_name}@ (generated)')

    save_file = open(f'{save_directory}/{i_name}.i', 'w')
    save_file.writelines(deck_lines)
    save_file.close()

    return f'{save_directory}/{i_name}.i'





def get_file_as_lines(file_path):
    with open(file_path, 'r') as list_file:
        lines = list_file.readlines()

    return lines





# sequence is a list of tuples (pos (str), load (str))
# loading is a dict
# u_loading is a dict with the MCNP number representation of universes

# check against approved elements / elements in store at some point
def validate_loading(loading, max_graphite = 37):
    valid = True
    
    loads = list(loading.values())
    num_graphite = loads.count('G')

    if num_graphite > max_graphite:
        print_color(f'@mToo many graphite elements in loading@: @y{num_graphite}@')
        print_color(f'@mARRR only has@ @y{max_graphite}@ @melements on hand@')
        valid = False

    num_aluminum = 0
    num_stainless = 0

    for pos, load in loading.items():
        # if there are duplicate items that aren't excepted
        if loads.count(load) > 1 and load not in ['G', 'W']:
            print_color(f'@mDuplicate items@ (@y{load}@) @mfound in loading@')
            valid = False

        elif load.isdigit():
            if int(load) > 7000:
                num_stainless += 1
            
            else:
                num_aluminum += 1

        # elif 'o' in load:
        #     num_aluminum += 1

    return valid


def loading_to_u_loading(loading, 
                         universe_codes = {
                            'SAFE': 801,
                            'SHIM': 802,
                            'REG': 900,
                            'SRC': 700,
                            'G' : 102,
                            'W' : 100,                    
                         }):
    
    u_loading = loading

    for pos, load in loading.items():
        if load in universe_codes.keys():
            u_loading[pos] = universe_codes[load]

    return u_loading


def u_loading_to_loading(u_loading,
                         universe_codes = {
                            '801': 'SAFE',
                            '802': 'SHIM',
                            '900': 'REG',
                            '700': 'SRC',
                            '102': 'G',
                            '100': 'W'
                         }):

    loading = u_loading

    for pos, u_load in u_loading.items():
        if u_load in universe_codes.keys():
            loading[pos] = universe_codes[u_load]

    return loading


# returns deck lines
# Takes dict that describes core loading
# And optionally, control rod positions
# or additionally, a deck template 
# (must be formatted in the same way as others)
# where the file and path can be specified 
def create_deck_from_loading(loading, 
                             template = 'T_2018-04-05.i',
                             template_path = 'K:/AT/Sheetpy',
                             safe = 1000,
                             shim = 1000,
                             reg = 1000,
                             particles = 50000,
                             active = 500,
                             inactive = 50,
                             keff_est = 1.0):
    
    # Open deck template file
    with open(f'{template_path}/{template}', 'r') as template_file:
        deck_lines = template_file.readlines()

    line_id_re = re.compile(r'(?<=!)\w+') 
    univ_id_re = re.compile(r'(?<=fill\=)\d+') 
    cr_id_re = re.compile(r'(?<=tr)\d')
    
    rod_values = {
        'SAFE': round(safe*0.0381, 5),
        'SHIM': round(shim*0.0381, 5),
        'REG': round(reg*0.0381, 5)
    }

    u_loading = loading_to_u_loading(loading)

    for idx, line in enumerate(deck_lines):

        if '!' in line:
        
            # Finds string following '!'
            line_id = line_id_re.findall(line)[0]

            if 'fill=' in line:

                # In this case line_id is the core position
                # for which to potentially modify loading
                univ_id = univ_id_re.findall(line)[0]

                # Some positions won't be in loading dict 
                # as they will be unloaded positions
                # In this case, the line isn't modified 
                # but unloaded positions are still tracked
                if line_id in u_loading.keys():

                    # Replace 'fill=' universe ID 
                    # with ID from sequence at that position
                    deck_lines[idx] = re.sub(univ_id_re,
                                             str(u_loading[line_id]),
                                             line)

            elif 'tr' in line:
                # Matches any transformation datacard
                # should only by CR transformations

                cr_id = cr_id_re.findall(line)[0]
                deck_lines[idx] = (f'tr{cr_id}  0.0  0.0   '
                                   f'{rod_values[line_id]} $ !{line_id}\n')


            elif 'kcode' in line:
                deck_lines[idx] = (f'kcode {particles} '
                                   f'{keff_est} {inactive} '
                                   f'{inactive + active} $ !kcode\n')



            # still need: tallies, header


    return deck_lines




def run_name(file_name,
             tasks = 8,
             input_path = 'K:/AT/Sheetpy/inputs',
             output_path = 'K:/AT/Sheetpy/outputs',
             rs_path = 'K:/AT/Sheetpy/rs',
             mcnp_dir = 'C:/Users/ishfulness/MCNP/MCNP_CODE/MCNP620/bin'):

    os.chdir(mcnp_dir)

    subprocess.check_call('mcnp6 '
                          f'i={input_path}/{file_name}.i '
                          f'o={output_path}/{file_name}.o '
                          f'name={rs_path}/{file_name}. '
                          f'tasks {tasks}')

    os.chdir('K:/AT/Sheetpy')



def run(input_path,
        output_path,
        tasks = 8,
        rs_path = 'K:/AT/Sheetpy/rs',
        mcnp_dir = 'C:/Users/ishfulness/MCNP/MCNP_CODE/MCNP620/bin'):

    os.chdir(mcnp_dir)

    file_name = get_name_from_path(input_path)

    subprocess.check_call('mcnp6 '
                          f'i={input_path} '
                          f'o={output_path} '
                          f'name={rs_path}/{file_name}. '
                          f'tasks {tasks}')

    os.chdir('K:/AT/Sheetpy')




def prepare_and_run(loading,
                    file_name = None,
                    name_suffix = '',
                    job = False,
                    **deck_params):

    # validates loading and prints warning if need be
    validate_loading(loading)

    # construct deck (as list of lines)
    # from params applied to a template
    deck_lines = create_deck_from_loading(loading, **deck_params)

    # saves to file
    input_file = save_input_deck(deck_lines,
                                 file_name = file_name,
                                 name_suffix = name_suffix,
                                 job = job)

    # creates and opens core image for file
    input_name = get_name_from_path(input_file)
    core_image.deck_to_image_default(input_file, 
                                     f'K:/AT/Sheetpy/images/{input_name}.svg')

    # runs mcnp on input deck
    run_name(input_name)


def get_name_from_path(path):
    # strips extension and encloding folders
    # could do this all with regex but I'm feeling lazy

    extension_re = re.compile(r'\.[0-9a-zA-Z]+$')

    path_no_ext = extension_re.sub('', path)
    file_name = path_no_ext.split('/')[-1]

    return file_name


# specifically ignores empty positions
def get_loading_from_deck(deck_lines):

    line_id_re = re.compile(r'(?<=!)\w+') 
    univ_id_re = re.compile(r'(?<=fill\=)\d+') 

    u_loading = {}

    for idx, line in enumerate(deck_lines):
        if '!' in line and 'fill=' in line:

            universe = univ_id_re.findall(line)[0]
            pos = line_id_re.findall(line)[0]

            if universe != '100':
                u_loading[pos] = universe

    loading = u_loading_to_loading(u_loading)

    return loading






deck_lines = get_file_as_lines('K:/AT/Sheetpy/inputs/ennui_3_testing.i')
loading = get_loading_from_deck(deck_lines)
prepare_and_run(loading, particles=500, active=40, inactive=10)





































# # want seperate from validate loading?
# # for dict key reasons? hmm idk
# def validate_deck(deck_lines):
#     pass

#     # no duplicate fuel elements
#     # up to 37 graphite
#     # No aluminum next to rods or in inner rings
#     # - with rod placements fixed


# # or do I just want line id?
# # also header needs all of C_D_F_L params...
# def todo_parse_line(line):
#     pass



# def get_loading_from_deck(deck_lines):
#     pass


# output_file_header = '          Code Name & Version = MCNP6'
