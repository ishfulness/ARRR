import random
import string

given_name_file_path = 'K:/AT/Sheetpy/tools/names/given.txt'
job_title_file_path = 'K:/AT/Sheetpy/tools/names/occupation.txt'


def generate(job = False):
    
    with open(given_name_file_path, 'r') as name_file:
        names = name_file.readlines()

    name = random.choice(names)[:-1]

    if job:

        with open(job_title_file_path, 'r') as job_file:
            jobs = job_file.readlines()

        job = random.choice(jobs)[:-1]
        return f'{name} the {job}'

    return name


def s_to_u(spaces_string):
    under_string = spaces_string.replace(' ', '_')

    return under_string

def rand_string(length):
    random_string = ''.join(
        random.choice(string.ascii_uppercase + string.digits) 
        for _ in range(length))

    return random_string

