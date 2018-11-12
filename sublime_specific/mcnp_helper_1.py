import sublime
import sublime_plugin

import re
from binascii import crc32


CM_CYAN = '#78DCE8' # cyan
CM_MAGENTA = '#FF6188' # Magenta
CM_ORANGE = '#FC9867' # orange?
CM_WHITE = 'white'
CM_LIGHTGRAY = '#AAAAAA' # light gray
CM_DARKGRAY = '#333333' # dark gray
CM_PURPLE = '#AB9DF2' # purple
CM_YELLOW = '#FFD866' # yellow
CM_GREEN = '#A9DC76' # green

# Starts with cell identifier or at least 6 spaces (continuation)
# maybe have different regex for continuation?
# valid_cell_card = re.compile(r'^(\d| {6}+)+ .*$')
# good enough for now
valid_cell_card = re.compile(r'^\d+\s+\d+.*')
valid_continuation_card = re.compile(r'^\s{6}.*')
valid_inline_comment = re.compile(r'\$.*$')



# cell_card = re.compile('')

# cell id, material, and density if applicable
# ^\d+\s+(0|\d+\s+[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)
# or wait I can just do, not a surface card (and I know what those look like)






# def parse_cell_card(card):
#     # removes the whitespace!
#     c = card.split()


#     return ''.join(c)



# def valid_card(card):
#     if valid_cell_card.match(card):
#         return True

#     else:
#         return False
def valid_card(card):
    return True

    # stupidly verbose
    # I think I can just use the




# class McnpHelperCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         # self.view.insert(edit, 0, "Hello, World!")
#         print(parse_cell_card(test_card))



# TODO
def zaid_to_text(zaid):

    z = int(zaid[0:2])
    a = int(zaid[2:])


    # elements = {
    #     1: 'H',
    #     2: 'He',
    #     3: 'Li',
    #     4: 'Be',
    #     5: 'B',
    #     6: 'C',
    #     7: 'N',
    #     8: 'O',
    #     9: 'F',
    #     10: 'Ne',
    #     11: 'Na',
    #     12: 'Mg',
    #     13: 'Al',
    #     14: 'Si',
    #     15: 'P',
    #     16: 'S',
    #     17:
    # }


    pass









class RelapTooltipCommand(sublime_plugin.EventListener):



    def parse_material_card(card):
        card, comment = raw_card.split('$', 1)
        c = card.split()

        zaid, xsn = c[0].split('.')
        material_name = zaid_to_text(zaid)



    def reference_material(self, m_card, mt_card):
        
        # Really shitty hack for mt_card not found
        if mt_card == 'c':
            if '$' in m_card:
                comment = m_card.split('$')
                return comment[1]
            
            return

        mt = mt_card.split()

        # return self.color_to_span('^' + mt[0] + '^$: $ ^'+ mt[1] + '^')
        return self.color_to_span('^' + mt[1] + '^')



    def reference_surface(self, raw_card):

        # Splits out comments, if any
        if '$' in raw_card:
            card, comment = raw_card.split('$', 1)
        else:
            card = raw_card
            comment = ' '

        # Remove whitespace and isolate each entry into index of list
        c = card.split()

        identifier = c[0]
        mnemonic = c[1]




        # for two letter mnemonics only,
        # for longer mnemonic words i'll need to do something
        # entirely different

        # remember the just-plain surface card!!!

        # have names and which dimension needs what?
        # list form maybe
        mnemonics = {
            'p': {
                'name': 'plane (form Ax+By+Cz-D=0).  Normal vector is (A, B, C) and D is distance along that vector',
                'entries': ['A', 'B', 'C', 'D']
            },
            'px': {
                'name': 'plane aligned with x-axis',
                'entries': ['x-axis coincident point']
            },
            'py': {
                'name': 'plane aligned with y-axis',
                'entries': ['y-axis coincident point']
            },
            'pz': {
                'name': 'plane aligned with z-axis',
                'entries': ['z-axis height']
            },
            'so': {
                'name': 'sphere centered at origin',
                'entries': ['radius']
            },
            's': {
                'name': 'sphere',
                'entries': ['x', 'y', 'z', 'radius']
            },
            'cx': {
                'name': 'cylinder on x-axis',
                'entries': ['radius']
            },
            'cy': {
                'name': 'cylinder on y-axis',
                'entries': ['radius']
            },
            'cz': {
                'name': 'cylinder on z-axis',
                'entries': ['radius']
            },
            'c/x': {
                'name': 'cylinder parallel to x-axis',
                'entries': ['y', 'z', 'radius']
            },
            'c/y': {
                'name': 'cylinder parallel to y-axis',
                'entries': ['x', 'z', 'radius']
            },
            'c/z': {
                'name': 'cylinder parallel to z-axis',
                'entries': ['x', 'y', 'radius']
            },
            'kx': {
                'name': 'cone on x-axis',
                'entries': ['cone tip (x)', 'tsquared', 'direction (+/- 1)']
            },
            'ky': {
                'name': 'cone on x-axis',
                'entries': ['cone tip (y)', 'tsquared', 'direction (+/- 1)']
            },
            'kz': {
                'name': 'cone on z-axis',
                'entries': ['cone tip (z)', 'tsquared', 'direction (+/- 1)']
            },
            'k/x': {
                'name': 'cone parallel to x-axis',
                'entries': ['x', 'y', 'z', 'tsquared', 'direction (+/- 1)']
            },
            'k/y': {
                'name': 'cone parallel to x-axis',
                'entries': ['x', 'y', 'z', 'tsquared', 'direction (+/- 1)']
            },
            'k/z': {
                'name': 'cone parallel to z-axis',
                'entries': ['x', 'y', 'z', 'tsquared', 'direction (+/- 1)']
            },
            'tx': {
                'name': 'elliptical torus parallel to x-axis',
                'entries': ['center x', 'center y', 'center z', 'radius to rotated ellipse', 
                'radius of rotated ellipse along axial (up and down) axis', 
                'radius of rotated ellipse along radial axis (see MCNP user manual p. 3-11)']
            },
            'ty': {
                'name': 'elliptical torus parallel to y-axis',
                'entries': ['center x', 'center y', 'center z', 'radius to rotated ellipse', 
                'radius of rotated ellipse along axial (up and down) axis', 
                'radius of rotated ellipse along radial axis (see MCNP user manual p. 3-11)']
            },
            'tz': {
                'name': 'elliptical torus parallel to z-axis',
                'entries': ['center x', 'center y', 'center z', 'radius to rotated ellipse', 
                'axial radius of rotated ellipse', 
                'radial radius of roteted ellipse']
            },
        }


        surface_colors = {
            'p': '!',
            'c': '~',
            'k': '@',
            't': '&',
        }

        title = self.color_to_span('^' + identifier + '^ $:  $' + 
            surface_colors[mnemonic[0]] + mnemonic + surface_colors[mnemonic[0]] + 
            '$ : $' + mnemonics[mnemonic]['name'])

        body_text = []
        for idx, entry in enumerate(mnemonics[mnemonic]['entries']):
            body_text.append(self.color_to_span('$' + entry + ':$ ' + 
                c[2+idx] + ' cm ('+ str(round(float(c[2+idx])/2.54,7)) + ' in.) <br>'))

        body = ''.join(body_text)


        foot = self.color_to_span('$' + comment + '$')

        html = (
            '<div>' + title + '</div>' +
            '<div>' + body + '</div>' +
            '<div>' + foot + '</div>' 
            )




        return html


    # def parse_cell_card(self, raw_card, entry, point, view):


    def color_to_span(self, content):

        html_content = content

        color_codes = {
            '@': CM_CYAN,
            '!': CM_MAGENTA,
            '$': CM_LIGHTGRAY,
            '%': CM_YELLOW, 
            '~': CM_GREEN,
            '&': CM_PURPLE,
            '`': CM_DARKGRAY
        }

        for match in re.findall(r'([&`@^!$%~](.+?)[&`@^!$%~])', html_content):
            if match[0][0] == '^':
                color = self.hash_color(match[1])

            else:
                color = color_codes[match[0][0]]

            color_span = ('<span style="color:{};">{}</span>'
                ).format(color, match[1])

            html_content = html_content.replace(match[0], color_span)

        return html_content





    def hash_color(self, text):
        text_hash = crc32(text.encode('utf-8')) & 0xffffffff

        h = (text_hash % 359)
        text_hash //= 360

        s = (0.35, 0.5, 0.65)[text_hash % 3]
        text_hash //= 3

        l = (0.35, 0.5, 0.65)[text_hash % 3]

        h /= 360
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q


        rgb = []
        for c in (h + 1 / 3, h, h - 1 / 3):
            if c < 0:
                c += 1
            elif c > 1:
                c -= 1

            if c < 1 / 6:
                c = p + (q - p) * 6 * c
            elif c < 0.5:
                c = q
            elif c < 2 / 3:
                c = p + (q - p) * 6 * (2 / 3 - c)
            else:
                c = p
            rgb.append(round(c * 255))

        return '#%02x%02x%02x' % tuple(rgb)






    def parse_cell_card(self, raw_card, card_component, point, view: sublime.View):
        card_information = {} # we'll fuck with this later

        # seperates any comment 
        # matches comment by the first instance of the dollar sign in card
        # That way i can use dollar sign in comments when I want
        # (important b/c reactivity)
        if '$' in raw_card:
            card, comment = raw_card.split('$', 1)
        else:
            card = raw_card


        # removes the whitespace!
        c = card.split()

        identifier = c[0]
        # we already know first index is the identifier
        # so move on to the material identifier

        # if material identifier is zero, 
        if c[1] == '0':
            material = c[1]
            density = 0
            surfaces_and_keywords = c[2:]


        else:
            material = c[1]
            density = c[2]

            surfaces_and_keywords = c[3:]


            # Find text of corresponding material card
            material_card = view.substr(
                view.line(view.find('m'+c[1], view.text_point(0,0))))

            mt_card = view.substr(
                view.line(view.find('mt'+c[1]+' ', view.text_point(0,0))))


            # material_info = self.parse_material_card(material_card)



        surfaces = []
        keywords = []

        for item in surfaces_and_keywords:
            if re.match(r'^[+-]?\d+$',item):
                surfaces.append(item)

            else:
                keywords.append(item)


        # Note, this won't work if material number = surface number
        # for something you're hovering over
        # I'll probably have to redo this using the sublime region's
        # coordinates and stuff

        # also the 'word' function in sublime doesn't play well with
        # string reprentation of floats, especially the decimal place

        # wait this won't work at all it doesn't do negatives...

        if card_component == identifier:
            print('you are over identifier')

        elif card_component == material:
            print('you are over material')
            return self.reference_material(material_card, mt_card)

        # Hack to make this work until I can make getting a word
        # using sublime's API better suited for my needs
        elif (card_component in surfaces or
            '+' + card_component in surfaces or
            '-' + card_component in surfaces):

            surface_card = view.substr(view.line(
                view.find(r'^' + card_component + r'\s+[ptck](/)?[zxy]', point)))

            
            return self.reference_surface(surface_card)





            # print(surface_card) 

            # print(self.parse_surface_card(surface_card))


        # from here, assume cell card


        return ' | '.join(c)




    # def get_prev_line(self, point, view: sublime.View):
    #     pr, _ = view.rowcol(point)
    #     prev_line_point = view.text_point(pr-1, 0)
    #     return view.substr(view.line(prev_line_point))


    # def get_next_line(self, point, view: sublime.View):
    #     nr, _ = view.rowcol(point)
    #     next_line_point = view.text_point(nr+1, 0)
    #     return view.substr(view.line(next_line_point))




    def increment_point(self, point, view: sublime.View):
        nr, _ = view.rowcol(point)
        next_line_point = view.text_point(nr+1, 0)
        return next_line_point

    def decrement_point(self, point, view: sublime.View):
        pr, _ = view.rowcol(point)
        prev_line_point = view.text_point(pr-1, 0)
        return prev_line_point


    # for reference, in mcnp they're called 'data entries'
    def get_mcnp_entry(self, view: sublime.View, point):
        pass # TODO




    def on_hover(self, view: sublime.View, point: int, hover_zone: int) -> None:


        # hacky for only running on mcnp input files
        if view.file_name()[-2:] != '.i':
            return


        # Continue only if cursor is over text
        if hover_zone != sublime.HOVER_TEXT:
            return


        # Get content of entire line under cursor as string
        line_content = view.substr(view.line(point))

        # Also get the specific word that is being hovered over
        # This doesn't really work for me because the 'word' according
        # to sublime doesn't include characters like '-' or '.'
        line_element = view.substr(view.word(point))


        # stop here if line is a comment or blank
        if not line_content:
            return

        if line_content[0] == 'c':
            return



        # # prints what's shown on the window rn
        # print(view.substr(view.visible_region()))







        # if the line is a continuation line, prepend all previous 
        # lines until start of card
        if valid_continuation_card.match(line_content):
            cont_point = self.decrement_point(point, view)
            while valid_continuation_card.match(view.substr(view.line(cont_point))): # while

                line_content = view.substr(view.line(cont_point)) + line_content
                cont_point = self.decrement_point(cont_point, view)

            line_content = view.substr(view.line(cont_point)) + line_content




        # if the next line continues this one, append all following 
        # continuations 
        cont_point = self.increment_point(point, view)
        while valid_continuation_card.match(
            view.substr(view.line(cont_point))):

            line_content += view.substr(view.line(cont_point))

            cont_point = self.increment_point(cont_point, view)




        # Check to see the type of card
        # if line starts with letter, then data card
        # if it matches simple regex, then surface
        # else, cell



        # makes sure it looks like a valid card before passing it on to the parser
        # This just returns true rn (probably should get rid of it)
        if valid_card(line_content):

            # parse the content to an html popup based on 
            if re.match(r'^[mM]', line_content):
                print('this is a material card')
                popup = 'material'

            elif re.match(r'^[abd-z]', line_content):
                print('this is a data card')
                # todo!!!!
                popup = 'data card'

            elif re.match(r'^\d+\s+[ctpck](/)?[zxy]', line_content):
                print('this is a surface card')
                # todo!!!!!!
                popup = 'surface'

            else:
                popup = self.parse_cell_card(line_content, line_element, point, view)


            # if an html popup exists, show it at the cursor
            # hide if the mouse moves away
            if popup:
                view.show_popup(popup,
                                sublime.HIDE_ON_MOUSE_MOVE_AWAY, 
                                point)

