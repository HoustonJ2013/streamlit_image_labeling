import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter


@st.cache(allow_output_mutation=True)
def get_state():
    return {}


def load_session(session_file):
    with open(session_file) as json_file:
        data = json.load(json_file)
    return data


def save_session(session_file, session_state):
    with open(session_file, "w") as outfile:
        json.dump(dict(session_state), outfile)


def update_session_file():
    if "session_file" in st.session_state:
        save_session(st.session_state["session_file"], st.session_state)


def load_label_json(label_path):
    with open(label_path) as json_file:
        label = json.load(json_file)
    return label

def update_label_json(label_path, label_dict):
    with open(label_path, "w") as outfile:
        json.dump(label_dict, outfile)


def display_session_setup():
    col1, col2, col3 = st.columns([1, 1, 1])
    username = col1.text_input("Please Enter your user name", key="username")
    load_existing_session = col2.button("Load Existing Session", key="load_existing_session")
    diff_session_file = col2.file_uploader("Choose a different session file", key="diff_session_file")
    start_new_session = col3.button("Start New Session", key="start_new_session")
    return username, load_existing_session, diff_session_file, start_new_session


def update_session_profile(session_dict):
    st.session_state["label_path"] = session_dict["label_path"]
    st.session_state["image_folder"] = session_dict["image_folder"]


def clean_session():
    st.session_state["label_path"] = ""
    st.session_state["image_folder"] = ""


def display_image_selection():
    index = [i for i, user in enumerate(img_df.index) if user == state["current_row"]][0]
    prev_key = "prev" + str(index)
    next_key = "next" + str(index)
    return (st.selectbox("Select an image for labeling", 
                            img_df.index, index), 
           st.button("previous", key=prev_key), 
            st.button("next", key=next_key))


def label_category(label_str):
    if len(label_str) == 0:
        return "Unlabeled"
    labels = label_str.split(",")
    if len(labels) == 1:
        return "Single Label"
    else:
        return "Multi Label"


def extract_all_labels(label_str_list):
    all_labels = []
    for label_str in label_str_list:
        if len(label_str) > 0:
            labels = label_str.split(",")
            all_labels.extend(labels)
    return all_labels


def extract_multilabels(label_str_list):
    all_labels = []
    for label_str in label_str_list:
        if len(label_str) > 0:
            labels = label_str.split(",")
            if len(labels) > 1:
                all_labels.append(",".join(sorted(labels)))
    return all_labels


### Instruction
st.markdown(
    """
    This is an image category labeling APP created with Streamlit
    Please follow the instructions to load, label images and save your labels
    ### Main Steps
    1. Load images and labels
    2. Label the images one by one
    3. Label stats
"""
)

home_directory = os.path.join(os.path.expanduser('~'), ".streamlit")


## User Session Handle
if "session_file" in st.session_state and os.path.exists(st.session_state["session_file"]):
    data = load_session(st.session_state["session_file"])
    if "username" in data:
        del data["username"]
    update_session_profile(data)
    st.write("Current session are loaded from %s"%(st.session_state["session_file"]))
else:
    (username, 
    load_existing_session, 
    diff_session_file, 
    start_new_session) = display_session_setup()
    session_file = os.path.join(home_directory, username + "_session") 
    if load_existing_session and os.path.exists(session_file):
        data = load_session(session_file)
        if "username" in data:
            del data["username"]
        update_session_profile(data)
        st.session_state["session_file"] = session_file
    if diff_session_file is not None:
        data = json.load(diff_session_file) 
        if "username" in data:
            del data["username"]
        update_session_profile(data)
        save_session(session_file, st.session_state)
        st.session_state["session_file"] = session_file
    if start_new_session is True:
        username = st.session_state["username"]
        clean_session()
        st.session_state["username"] = username 
        save_session(session_file, st.session_state)
        st.session_state["session_file"] = session_file
    
## Step 1
st.header("1. Load images and labels")
st.subheader("1. Set Image Path")
image_path_col1, image_path_col2, image_path_col3 = st.columns([2, 0.5, 2])

image_folder_path = image_path_col1.text_input("Please input the path to the folder containing images", 
                                        key="image_folder", 
                                        on_change=update_session_file)
image_path_col2.text("OR")
image_csv_file = image_path_col3.file_uploader("Please input the path to csv file with 'img_path' column to the images", 
                            key="image_csv_file")

st.subheader("2. Set the Label Path")
label_path = st.text_input("Please input the path to save the label (json format)", 
                            key="label_path", 
                            on_change=update_session_file)

img_df = pd.DataFrame(columns=["img_path", "img_name"])
label_df = pd.DataFrame(columns=["label"])
label_dict = {"session_file": st.session_state["session_file"]}

if image_folder_path != "":
    if os.path.exists(image_folder_path) is False: 
        st.error("%s doesn't exist"%(image_folder_path))
    img_paths = [os.path.join(image_folder_path, _) 
                 for _ in os.listdir(image_folder_path) if "csv" not in _]
    img_names = [_.split("/")[-1].split(".")[0] for _ in img_paths]
    img_df = pd.DataFrame.from_dict({"img_path": img_paths, 
                                     "img_name": img_names,
                                     })
if image_csv_file is not None:
    img_df = pd.read_csv(image_csv_file)
    if "img_path" not in img_df:
        st.error("'img_path' doesn't exist in the table")
    img_df["img_name"] = img_df["img_path"].apply(lambda x: x.split("/")[-1].split(".")[0])
    if "label" in img_df:
        img_df = img_df.drop(["label"], axis=1)

if label_path == "":
    st.error("label_path is not specified, please set the path to save the labels")
else:
    if os.path.exists(label_path):
        label_dict = load_label_json(label_path)
        label_df = pd.Series(label_dict).to_frame(name="label")

img_df = img_df.join(label_df, on="img_path", how="left")
img_df.loc[img_df["label"].isna(), "label"] = ""
## Display the loaded table 
st.text("Loaded Image and Labels")
st.dataframe(img_df, width=500, height=200)


#### Step two
st.header("2. Label the images one by one")

img_width_col, img_height_col, label_input_buff = st.columns([1, 1, 3])
target_width = img_width_col.number_input("Image target width", min_value=10, max_value=1000, value=300)
target_height = img_height_col.number_input("target height", min_value=10, max_value=1000, value=300)
multiple_labels = label_input_buff.text_input("Labels (seperate by ,)", value="dog,cat", key="multiple_labels")
target_labels = [_.strip() for _ in multiple_labels.split(",")]

col1, col2, col3 = st.columns([1.2, 3, 2])

state = get_state()

with col1:
    if "current_row" not in state:
        state["current_row"] = 0
    if "current_row" in state:
        if state["current_row"] < 0:
            state["current_row"] = len(img_df) - 1
        elif state["current_row"] >= len(img_df):
            state["current_row"] = 0
    
    current_row, prev_click, next_click = display_image_selection()

    input_changed = False 
    if current_row != state["current_row"] and input_changed is False:
        state["current_row"] = current_row
        input_changed = True 
        # display_image_selection()
    if prev_click is True and input_changed is False:
        state["current_row"] -= 1
        input_changed = True 
        # display_image_selection()
    if next_click is True and input_changed is False:
        state["current_row"] += 1
        input_changed = True 
        # display_image_selection()
    if st.button("Save_session", key="save2"):
        with open(st.session_state["session_file"], "w") as outfile:
            json.dump(dict(st.session_state), outfile)


with col2:
    img_path = img_df.loc[current_row,"img_path"]
    image = Image.open(img_path)
    image = image.resize((target_width, target_height))
    image_name = img_path.split("/")[-1].split(".")[0]
    st.image(image, caption=image_name)


current_labels = img_df.loc[current_row, "label"].split(",")
selected_labels = col3.multiselect("Label", 
                                    options=target_labels + [""], 
                                    default=current_labels)
label_dict[img_path] = ",".join([_ for _ in selected_labels if _ != ""])
col3.button("Update Label", on_click=update_label_json, args=(label_path, label_dict))


#### Step 3
st.header("3. Label Stats")
fig, axes = plt.subplots(2, 2)
fig.set_figheight(8)
fig.set_figwidth(12)
img_df["label_category"] = img_df["label"].apply(lambda x: label_category(x))
img_df.groupby("label_category").count()["img_path"].plot(kind="barh", ax=axes[0][0])
axes[0][0].set_title("Label Category")

all_labels = extract_all_labels(img_df["label"].values)
w = Counter(all_labels)
axes[0][1].barh(list(w.keys()), list(w.values()))
axes[0][1].set_title("All Labels")

single_labels = extract_all_labels(img_df[img_df["label_category"] == "Single Label"]["label"].values)
w2 = Counter(single_labels)
axes[1][0].barh(list(w2.keys()), list(w2.values()))
axes[1][0].set_title("Single Labels")

multi_labels = extract_multilabels(img_df[img_df["label_category"] == "Multi Label"]["label"].values)
w3 = Counter(multi_labels)
axes[1][1].barh(list(w3.keys()), list(w3.values()))
axes[1][1].set_title("Multi Labels")

st.pyplot(fig)

