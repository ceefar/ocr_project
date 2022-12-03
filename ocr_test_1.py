# -- author : ceefar --

# -- imports --
import cv2
from pytesseract import pytesseract
from pytesseract import Output
import numpy as np
from matplotlib import pyplot as plt
import os

# [setup tesseract]
pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # < [ REQUIREMENT ]

# -- optical character recognition --
def draw_word_boxes(img, active_user_name):
    """ """
    image_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    user_name_words_y_pos = 0
    word_list = []
    for i, word in enumerate(image_data["text"]):
        if word != "":
            x, y = image_data["left"][i], image_data["top"][i]
            w, h = image_data["width"][i], image_data["height"][i]
            # -- the first profile word is always word 4 (i wanna say due the fact its finding 3 artifacts beforehand consistently but i will confirm this shortly) --
            if y >= 4:
                # -- only set this if it hasnt been set yet -- 
                if not user_name_words_y_pos:
                    user_name_words_y_pos = y           
                # -- if this word is on the same y pos as the first word in the username, draw word in rect, print word to console, save word--          
                if y <= user_name_words_y_pos + 10 and y >= user_name_words_y_pos - 10:
                    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 3) # note rect and putText can be run outside of this if statement, just doing like this for pfp (again, hence the need for decorator lol)
                    cv2.putText(img, word, (x, y-16), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    # -- if theres already a word in there - i.e. the username is a multiline string --
                    if len(active_user_name) > 1: 
                        active_user_name += f"_{word}" # using an underline as this is only used for the directory name
                    # -- else just save it to the var --
                    else:
                        active_user_name = word  
        # -- finally save all the words so we can check the exact outputs later --   
        word_list.append(word)                           
    # -- return the user name --
    return img, active_user_name, word_list

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

def get_resized_img(img:np.ndarray, size=0.9):
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

# -- create user info file -- 
def create_user_info_file(user_dir, user_name, img_word_list):
    dest = f"user_data/{user_dir}/{user_name}_data.txt"
    with open(dest, 'w') as f:
        for a_word in img_word_list:
            if a_word:
                f.write(f"{a_word}\n")

# -- main -- 
def main():
    make_user_data_dir()
    successful_extractions = 0 # temp counter for quality assurance while developing
    for i, file in enumerate(os.listdir()):
        if file.endswith(".png"):
            # -- read in the image and save a copy --
            original_img = cv2.imread(f"{file}", 0)
            img_copy = original_img.copy()  
            # -- run ocr on the image and draw boxes around those words, get back the username to use for the directory name -- 
            user_name = ""
            img_word_list = []
            img, user_name, img_word_list = draw_word_boxes(img_copy, user_name)
            # -- start some simple qa -- 
            got_right_name = check_if_name_accurate(user_name)
            msg = f"{user_name.replace('_',' ')} - Success!" if got_right_name else f"{user_name} - Failed"
            if got_right_name:
                successful_extractions += 1
            print(msg)
            # -- create dir for user --        
            if user_name:
                user_dir = make_user_dir(f"{user_name}")  
            else:
                user_dir = make_user_dir(f"user_{i}") # temporary while testing - `i` here is the file index 
            # -- save images --
            cv2.imwrite(f"user_data/{user_dir}/profile_{user_name}_img.png", img)
            # -- save info --
            create_user_info_file(user_dir, user_name, img_word_list)
            plt.show()
    # -- finally, print the qa results --
    print(f"{successful_extractions} of 6 Successfully Extracted [ {((successful_extractions/6) * 100):.0f}% ]")

# -- development testing x debug area --
def check_if_name_accurate(user_name:str):
    """ check the verfied names from a list of the actual names to start getting some basic quality assurance data back during development """
    verified_names = ["iSmurFromlronV", "lumpyflump1", "Rhaast so Cuite", "SUPER MARIO", "Malignat Force"]
    # -- reformat the name to check for accuracy -- 
    true_name = user_name.replace("_", " ")
    # -- return true if the name is in the verified list else return false -- 
    return True if true_name in verified_names else False

# [driver]
if __name__ == "__main__":
    main()

# -- notes --
# - save the qa as a file at the root directory duhhhh
# - get the preprocessing loop in here
# - get it in streamlit
# - save it to repo, and get some ss or gif of current state and do the readme
#   - note current state doesnt matter, actually would quite like to document the learning journey on this one too tbf 

# -- end of file -- 