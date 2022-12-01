# author
#   - ceefar

# project brief
#   - using optical character recognition, data viz, and data analytics 
#   - to programatically process and collate data from a popular mobile game title
#   - will further clarify the specifics in future
#   - may also inlcude some databasing too as why not

# [imports]
import cv2
from pytesseract import pytesseract
from pytesseract import Output
import numpy as np # technically only using right now for the type hints btw
import os # for file handling
from matplotlib import pyplot as plt # < will use for plotting shortly

# [setup tesseract]
pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # < [ REQUIREMENT ]

# [vars]
original_img_1 = cv2.imread("profile_stats_test_image_1.png")
image_1 = original_img_1.copy()
original_img_2 = cv2.imread("profile_stats_test_image_2.png")
image_2 = original_img_2.copy()
original_img_3 = cv2.imread("profile_stats_test_image_3.png")
image_3 = original_img_3.copy()
original_img_4 = cv2.imread("profile_stats_test_image_4.png")
image_4 = original_img_4.copy()
original_img_5 = cv2.imread("profile_stats_test_image_5.png")
image_5 = original_img_5.copy()

# [funcs]
# -- handle windows --
def create_window(name:str="Preview"):
    """ create window with given name """
    cv2.namedWindow(f"{name}", cv2.WINDOW_AUTOSIZE)

def show_img_in_window(img:np.ndarray, name="Preview"):
    """ show given image in chosen window, and wait for key press 
    - image (required)
    - name (optional)
        - defaults to `preview` """
    create_window(name)
    # -- resize so it fits on the screen, as its a large image --
    cv2.imshow(f"{name}", get_resized_img(img))
    # -- await input and destroy windows --
    cv2.waitKey(0)    
    cv2.destroyAllWindows()

# -- image manipulation --
def get_resized_img(img:np.ndarray, size=0.6):
    """ creates a new copy and returns it """
    img_copy = cv2.resize(img.copy(), (0, 0), fx=size, fy=size)
    return img_copy

def crop_image(img:np.ndarray, slice_type:str="pfp"):
    """ uses a copy of the image, returns slice based on `slice_type`
    - pfp : profile picture & name section """
    img_copy = img.copy()
    if slice_type == "pfp":
        img_slice = img_copy[290:470, 0:450] # pro pic and name @ page : profile stats - bars view
    return img_slice

# -- preprocessing --
def img_to_greyscale(img):
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return grey_img

# -- optical character recognition --
def draw_word_boxes(img, active_user_name):
    image_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    user_name_words_y_pos = 0
    for i, word in enumerate(image_data["text"]):
        if word != "":
            x, y = image_data["left"][i], image_data["top"][i]
            w, h = image_data["width"][i], image_data["height"][i]
            # -- the first profile word is always word 4 (i wanna say due the fact its finding 3 artifacts beforehand consistently but i will confirm this shortly) --
            if y >= 4:
                # -- only set this if its not been set yet -- 
                if not user_name_words_y_pos:
                    user_name_words_y_pos = y           
                # -- if this word is on the same y pos as the first word in the username, draw word in rect, print word to console, save word--                         
                if y == user_name_words_y_pos:
                    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 3) # note rect and putText can be run outside of this if statement, just doing like this for pfp (again, hence the need for decorator lol)
                    cv2.putText(img, word, (x, y-16), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    print(f"{i} : {word = }, {x = }, {y =}")
                    # -- if theres already a word in there - i.e. the username is a multiline string --
                    if len(active_user_name) > 1: 
                        active_user_name += f"_{word}" # using an underline as this is only used for the directory name
                    # -- else just save it to the var --
                    else:
                        active_user_name = word                            
    # -- show the image --
    show_img_in_window(img)
    # -- return the user name --
    return active_user_name

# -- handle directories --
def make_user_data_dir():
    """ initially create the root level folder to store all of the users data directories so everything is organised """
    # -- if the root user folder doesnt exist already, create it --
    try:
        os.mkdir(f"user_data")
    except FileExistsError:
            pass

def make_user_dir(ocr_user_name:str):
    """ create a folder for this user to store their data locally in an organised manner, returns created/desired path path as a string """
    # -- if this user doesnt have a folder already, create it --
    try:
        os.mkdir(f"user_data/{ocr_user_name}_data")
    except FileExistsError:
            pass
    finally:
        return f"{ocr_user_name}_data"

# -- main -- 
def main(img):
    """ by the way this is really still just me testing out the functionality """
    # --
    make_user_data_dir()
    # -- profile name slice --
    profile_name_img = crop_image(img)
    profile_name_img_grey = img_to_greyscale(profile_name_img)
    # -- resize after crop/slice --
    profile_name_img = get_resized_img(profile_name_img, 2)
    profile_name_img_grey = get_resized_img(profile_name_img_grey, 2)
    # -- show images --
    show_img_in_window(profile_name_img)
    show_img_in_window(profile_name_img_grey)
    # -- initialise these first so we can send them and get them back seperately -- 
    un, un_grey = "", ""
    # -- draw word boxes --
    un = draw_word_boxes(profile_name_img, un) # un = username
    un_grey = draw_word_boxes(profile_name_img_grey, un_grey)
    # -- create a user directory if we dont have one already for this user --
    user_dir = make_user_dir(un)
    # -- save images --
    cv2.imwrite(f"user_data/{user_dir}/profile_{un}_img.png", profile_name_img)
    cv2.imwrite(f"user_data/{user_dir}/profile_{un}_img_grey.png", profile_name_img_grey) # using the same name here incase there are issues with greyscale ocr, we still wanna save the file
    
# [driver]
if __name__ == "__main__":
    # img_list = [image_1, image_2, image_3, image_4, image_5]
    img_list = [image_1]
    for img in img_list:
        main(img)



# [todo]
# - add to changelog what ive done... i.e. first grab some comparative images so can test this appropriately at various stages

# - chunk up the function a bit
# - test with all test imgs



# [notes]
# get it into folders so its not annoying af
# - just do by name for now, make new name for person if folder doesnt exist, else use that folder
# - grab the code from the old reddit project
# - get 2 or 3 images to test this i == 4 thing as is kinda sus, if its fine continue ig but should find out how this works for sure at some point later or tomo

# - then do this decorator thing 100%
#   - so that one will be a pfp decorator ig

# - then do one to draw the rank
#   - this one needs some fixing too as its not really accurate and ideally need a way bigger pool of ranks

# - then ig improve the text functions a tad tho tbf this is fine for testing
# - then ig try and get that grid thing setup again, but maybe even better?! (can you draw 2 windows and *then* await_input ?)

# - then legit just comparative pre-processing stuff




# [rnrn]
# - no cap before doing below notes
# - do the two previous repo readmes, improve the profile readme, etc
# - defo do gif stuff
# - try to get pages for old nhs app looking clean as you really arent doing it justice
# - consider a projects readme repo (which will make a webpage over the christmas as a project)