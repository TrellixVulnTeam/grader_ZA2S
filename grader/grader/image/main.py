'''Logic and functionality for creating images with payloads
'''

from grader.utils.utils import get_folder

def build_image(target, args):
    print("Obtaining source")
    f = get_folder(target)
