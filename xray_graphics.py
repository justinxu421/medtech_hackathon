#!/usr/bin/env python3

"""
graphics for xray project. Some stolen from babygraphics assignment
"""

import sys
import os
import numpy as np
# from model_utils import load_saved_model, run_model
from tkinter import *
from PIL import ImageTk, Image

# list of the filenames in the images directory
FILENAMES = os.listdir('images') 

# stored tuples (filename, score)
stored_scores = np.genfromtxt('sorted_scores.csv', dtype=str, delimiter=',')[:,:2]
stored_scores = [(x[0], float(x[1])) for x in stored_scores]
# dictionary mapping the scores
SCORE_DICT = dict(stored_scores)

SPACE = 10
def make_score_list(canvas, scores = sorted(SCORE_DICT.items(), key = lambda x: x[1])[-10:],
                     idx = None, color = 'blue'):
    canvas.delete('all')
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    # pesky windows errors
    space_height = height-13

    #centerline to separate the columns
    canvas.create_line(width//2, SPACE, width//2, height-3)

    for i in range(11):
        y0 = i * space_height / 11 + SPACE
        y1 = (i+1) * space_height / 11 + SPACE
        canvas.create_line(0, y0, width, y0)
        # if the corresponding rectangle is the score, color it
        if i-1 == idx:
            canvas.create_rectangle(0, y0, width//2, y1, fill = color)
            canvas.create_rectangle(width//2, y0, width, y1, fill = color)
        # create the name labels if first row
        if i == 0:
            canvas.create_rectangle(0, y0, width//2, y1, fill = 'orange')
            canvas.create_rectangle(width//2, y0, width, y1, fill = 'yellow')
            canvas.create_text(width//4, y0+10, text="Filename")
            canvas.create_text(3*width//4, y0+10, text="Scores")
        # otherwise insert the data
        else:
            canvas.create_text(width//4, y0+10, text=str(scores[i-1][0]))
            canvas.create_text(3*width//4, y0+10, text=str(scores[i-1][1]))

    y0 = 11 * space_height / 11 + SPACE
    canvas.create_line(0, y0, width, y0)

# provided function to build the GUI
def make_gui(top, width, height, vision_model):
    """
    Set up the GUI elements for Baby Names, returning the Canvas to use.
    top is TK root, width/height is canvas size
    """
    # size of the image
    size = min(width,height)

    # header 
    space = Label(top, font=("Courrier",14), text = "Doctor X", height=3, borderwidth=0)
    space.grid(row=1, columnspan=12)

    # label and name entry field to enter filename
    label = Label(top, text="Filename:")
    label.grid(row=2, column=0)
    entry = Entry(top, width=50, name='entry', borderwidth=2)
    entry.grid(row=2, column=1)

    score_label = Label(top, font=("Courrier", 12), text="Your Score:")
    score_label.grid(row=2, column=3, columnspan = 6, padx=10)

    space2 = LabelFrame(top, width=20, height=20, borderwidth=0)
    space2.grid(row=3, columnspan=12)

    image = Image.open("images/no_image.png")
    image = image.resize((size,size), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image)
    panel = Label(top, image = img, borderwidth=2)
    panel.image = img
    panel.grid(row=4, column=0, rowspan=5, columnspan=2, sticky='w')

    # canvas for drawing the scores
    canvas = Canvas(top, width=width, height=height, name='canvas')
    canvas.grid(row=4, column=2, columnspan=8, sticky='w')

    # label for the xray's name
    xray_label = Label(top, text="Xray name: None Selected")
    xray_label.grid(row=9, column=0, padx=10, columnspan=2)

    # search bar to look for images
    search_label = Label(top, text="Search:")
    search_label.grid(row=10, column=0)
    search_entry = Entry(top, width = 50, name='searchentry')
    search_entry.grid(row=10, column=1)
    search_out = Text(top, height=2, width=70, name='searchout', borderwidth=2)
    search_out.grid(row=10, column=6, sticky='w')

    # When <return> key is hit in a text field .. connect to the handle_draw()
    entry.bind("<Return>", lambda event: handle_draw(entry, panel, canvas, xray_label, score_label, vision_model))
    search_entry.bind("<Return>", lambda event: handle_search(search_entry, search_out))

    top.update()
    make_score_list(canvas)
    # return canvas

# get scores in close proximity to the score of the current filename
def get_proximity_scores(filename):
    # sort the items by score
    score = SCORE_DICT[filename]
    sorted_scores = sorted(SCORE_DICT.items(), key = lambda x: x[1])
    idx = sorted_scores.index((filename, score))
    print(idx)

    # get the color based on the score 
    if score > 1:
        color = 'red'
    elif score > 0.5:
        color = 'blue'
    else:
        color = 'green'

    if idx < 5:
        return sorted_scores[:10], idx, color 
    elif idx > len(sorted_scores) - 5:
        return sorted_scores[-10:], 10 - (len(sorted_scores) - idx), color
    else:
        return sorted_scores[idx-5:idx+5], 5, color 

def handle_draw(entry, panel, canvas, xray_label, score_label, vision_model):
    """
    Called when <return> key hit in given entry text field.
    Gets search text from given entry, draws picture 
    to the given canvas.
    """
    global FILENAMES
    filename = entry.get()
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    size = min(width, height)

    # get a score and update the image if filename exists
    if filename in FILENAMES:
        image = Image.open("images/" + filename)
        image = image.resize((size,size), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        panel.configure(image=img)
        panel.image = img
        xray_label.configure(text = "Xray name: " + filename)
        # run the model to calculate the score
        score = run_model(filename, vision_model)
        # update score label 
        score = round(score, 4)
        print(score)
        # add to the score dictionary if not in already
        if filename not in SCORE_DICT:
            SCORE_DICT[filename] = score
        # get the 10 scores in proximity to the calculated one
        scores, idx, color = get_proximity_scores(filename)
        score_label.configure(fg=color, text = "Your Score: {}".format(str(score)))
        make_score_list(canvas, scores, idx, color)

    else:
        image = Image.open("images/no_image.png")
        image = image.resize((300,300), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        panel.configure(image=img)
        panel.image = img
        xray_label.configure(text = "Filename not found")
        score_label.configure(text = "Your Score: N/A")
        make_score_list(canvas)

# looks for matching files based on the search entry
def search_files(target, max_names = 5):
    global FILENAMES
    result = []
    target = target.lower()
    for name in FILENAMES:
        if target in name.lower():
            result.append(name)
            if len(result) >= max_names:
                break
    return sorted(result)

def handle_search(search_entry, search_out):
    """
    Calls search() and displays results in GUI.
    Gets search target from given search_entry, puts results
    in given search_out text area.
    """
    # update filenames when searching
    global FILENAMES
    FILENAMES = os.listdir('images') 

    target = search_entry.get().strip()
    if target:
        # return at most 20 names
        result = search_files(target)
        out = ' '.join(result)
        #searchout = top.children['searchout']  # alt strategy to access fields
        search_out.delete('1.0', END)
        search_out.insert('1.0', out)

# main() code is provided
def main():
    args = sys.argv[1:]
    # Establish size - user can override
    width = 600 
    height = 400
    if len(args) == 2:
        width = int(args.pop(0))
        height = int(args.pop(0))

    # Make window
    top = Tk()
    top.wm_title('XRAY scores')

    # initializes the model
    # vision_model = load_saved_model() 
    vision_model = None

    # make the gui
    make_gui(top, width, height, vision_model)

    # draw_fixed once at startup so we have the lines
    # even before the user types anything.
    # draw_fixed(canvas)
    top.mainloop()


if __name__ == '__main__':
    main()