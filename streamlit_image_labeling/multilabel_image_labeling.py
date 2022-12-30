import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter
from pandas.api.types import is_numeric_dtype
from utils import (
    save_session,
    load_session,
    load_label_json,
    update_label_json,
    update_session_file,
    check_password,
)


@st.cache(allow_output_mutation=True)
def get_state():
    return {}


def display_session_setup():
    col1, col2, col3 = st.columns([1, 1, 1])
    username = st.session_state["username"]
    # col1.text_input("Please Enter your user name", key="username")
    col1.write("Current User: " + username)
    session_file = os.path.join(home_directory, username + "_session")
    if os.path.exists(session_file) and username != "":
        col2.write("You have a saved session: Load or start a new session")
        load_existing_session = col2.button(
            "Load Existing Session", key="load_existing_session"
        )
        col2.text("or")
        diff_session_file = col2.file_uploader(
            "Choose another session file on disk", key="diff_session_file"
        )
    else:
        load_existing_session = False
        col2.write("No session File Found")
        diff_session_file = col2.file_uploader(
            "Choose another session file on disk", key="diff_session_file"
        )

    def start_new_session_fn():
        clean_session()
        # st.session_state["username"] = username
        save_session(session_file, st.session_state)

    col3.write(" ")
    col3.write(" ")
    col3.write(" ")
    col3.write(" ")
    start_new_session = col3.button(
        "Start New Session", on_click=start_new_session_fn, key="start_new_session"
    )
    return username, load_existing_session, diff_session_file, start_new_session


def update_session_profile(session_dict):
    st.session_state["label_path"] = session_dict["label_path"]
    st.session_state["image_folder"] = session_dict["image_folder"]
    st.session_state["image_csv_file"] = session_dict["image_csv_file"]
    if "username" in st.session_state:
        st.session_state["username"] = session_dict["username"]
    if "filter1_values" in session_dict:
        st.session_state["filter1_values"] = tuple(session_dict["filter1_values"])
    if "multiple_labels" in session_dict:
        st.session_state["multiple_labels"] = session_dict["multiple_labels"]


def update_multiple_labels():
    st.session_state["multiple_labels"] = multiple_labels
    update_session_file()


def clean_session():
    st.session_state["label_path"] = ""
    st.session_state["image_folder"] = ""
    if "filter1_values" in st.session_state:
        del st.session_state["filter1_values"]
    if "multiple_labels" in st.session_state:
        del st.session_state["multiple_labels"]


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

# home_directory = os.path.join(os.path.expanduser("~"), ".streamlit")
home_directory = ".streamlit"
if os.path.exists(home_directory) is False:
    os.makedirs(home_directory)

if check_password():

    # st.write(st.session_state)

    ## User Session Handle
    if "session_file" in st.session_state and os.path.exists(
        st.session_state["session_file"]
    ):
        data = load_session(st.session_state["session_file"])
        # if "username" in data:
        #     del data["username"]
        update_session_profile(data)
        st.write(
            "Current session are loaded from %s" % (st.session_state["session_file"])
        )
        # st.write(st.session_state)
    else:
        (
            username,
            load_existing_session,
            diff_session_file,
            start_new_session,
        ) = display_session_setup()
        session_file = os.path.join(home_directory, username + "_session")
        st.session_state["session_file"] = session_file
        st.session_state["username"] = username
        if load_existing_session and os.path.exists(session_file):
            data = load_session(session_file)
            # if "username" in data:
            #     del data["username"]
            update_session_profile(data)
        if diff_session_file is not None:
            data = json.load(diff_session_file)
            # if "username" in data:
            #     del data["username"]
            update_session_profile(data)
            save_session(session_file, st.session_state)

    ## Step 1
    st.header("1. Load images and labels")
    st.subheader("1. Set Image Path")
    image_path_col1, image_path_col2, image_path_col3 = st.columns([2, 0.5, 2])

    image_folder_path = image_path_col1.text_input(
        "Please input the path to the folder containing images",
        key="image_folder",
        on_change=update_session_file,
    )
    image_path_col2.text("OR")
    image_csv_file = image_path_col3.text_input(
        "Please input the path to csv file with 'img_path' column to the images",
        key="image_csv_file",
        on_change=update_session_file,
    )

    st.subheader("2. Set the Label Path")
    label_path = st.text_input(
        "Please input the path to save the label (json format)",
        key="label_path",
        on_change=update_session_file,
    )

    img_df = pd.DataFrame(columns=["img_path", "img_name"])
    label_df = pd.DataFrame(columns=["label"])
    label_dict = {}
    derived_labels = ""

    if image_folder_path != "":
        if os.path.exists(image_folder_path) is False:
            st.error("%s doesn't exist" % (image_folder_path))
        img_paths = [
            os.path.join(image_folder_path, _)
            for _ in os.listdir(image_folder_path)
            if "csv" not in _
        ]
        img_names = [_.split("/")[-1].split(".")[0] for _ in img_paths]
        img_df = pd.DataFrame.from_dict(
            {
                "img_path": img_paths,
                "img_name": img_names,
            }
        )
    elif image_csv_file != "":
        if os.path.exists(image_csv_file) is False:
            st.error(image_csv_file + " doesn't exist")
        else:
            img_df = pd.read_csv(image_csv_file)
            if "img_path" not in img_df:
                st.error("'img_path' doesn't exist in the table")
            img_df["img_name"] = img_df["img_path"].apply(
                lambda x: x.split("/")[-1].split(".")[0]
            )
            if "label" in img_df:
                img_df = img_df.drop(["label"], axis=1)
    else:
        st.error("image path is not specified")

    if label_path == "":
        st.error("label_path is not specified, please set the path to save the labels")
    else:
        if os.path.exists(label_path):
            label_dict = load_label_json(label_path)
            label_df = pd.Series(label_dict).to_frame(name="label")
            json_labels = []
            for _, val in label_dict.items():
                json_labels.extend(val.split(","))
            derived_labels = ",".join(sorted(np.unique(json_labels)))

    img_df = img_df.join(label_df, on="img_path", how="left")
    img_df.loc[img_df["label"].isna(), "label"] = ""

    ## Display and filter loaded table
    state = get_state()
    st.text("Set a filter for the images (Optional)")
    filter1_col1, filter1_col2 = st.columns([1, 4])
    filter1_col = filter1_col1.text_input("Filter Column Name", key="filter1_col")
    if filter1_col in img_df and is_numeric_dtype(img_df[filter1_col]):
        min_val, max_val = float(min(0, img_df[filter1_col].min())), float(
            max(1, img_df[filter1_col].max())
        )
        if "filter1_values" in state:
            filter1_values = state["filter1_values"]
        else:
            filter1_values = (min_val, max_val)

        val1, val2 = filter1_col2.slider(
            "filter 1 range", min_val, max_val, filter1_values, key="filter1_values"
        )
        img_df = img_df[img_df[filter1_col].apply(lambda x: val1 <= x <= val2)]

    st.dataframe(img_df, width=800, height=200)

    if len(img_df) == 0:
        st.error("No images are selected for labels")
    else:
        #### Step two
        st.header("2. Label the images one by one")

        (
            img_width_col,
            img_height_col,
            label_input_buff,
            save_multilabels_to_session_col,
        ) = st.columns([1, 1, 3, 1])
        target_width = img_width_col.number_input(
            "Image width", min_value=10, max_value=1000, value=300
        )
        target_height = img_height_col.number_input(
            "height", min_value=10, max_value=1000, value=300
        )
        union_labels = []
        if "multiple_labels" in st.session_state:
            union_labels = ",".join(
                sorted(
                    list(
                        set(derived_labels).union(
                            st.session_state["multiple_labels"].split(",")
                        )
                    )
                )
            )
            multiple_labels = label_input_buff.text_input(
                "Multi-Label Options (seperate by ,)",
                value=st.session_state["multiple_labels"],
            )
        else:
            if len(derived_labels) == 0:
                multiple_labels = label_input_buff.text_input(
                    "Multi-Label Options (seperate by ,)", value="dog,cat"
                )
            else:
                multiple_labels = label_input_buff.text_input(
                    "Multi-Label Options (seperate by ,)", value=derived_labels
                )
        save_multilabels_to_session_col.button(
            "Save Multi-label Options to Session File", on_click=update_multiple_labels
        )

        target_labels = [_.strip() for _ in multiple_labels.split(",")]

        col1, col2, col3 = st.columns([1.2, 3, 2])
        with col1:

            if "current_row" not in state or state["current_row"] is None:
                state["current_row"] = 0
            if "current_row" in state:
                if state["current_row"] < 0:
                    state["current_row"] = len(img_df) - 1
                elif state["current_row"] >= len(img_df):
                    state["current_row"] = 0

            prev_click = st.button("previous")
            next_click = st.button("next")
            current_row = state["current_row"]
            if prev_click is True:
                current_row -= 1
                if current_row < 0:
                    current_row = len(img_df) - 1
            if next_click is True:
                current_row += 1
                if current_row >= len(img_df):
                    current_row = 0
            current_row = st.selectbox(
                "Select an image for labeling", img_df.index, current_row
            )
            if current_row is not None:
                state["current_row"] = current_row

        with col2:
            img_path = img_df.loc[current_row, "img_path"]
            image = Image.open(img_path)
            image = image.resize((target_width, target_height))
            image_name = img_path.split("/")[-1].split(".")[0]
            st.image(image, caption=image_name)

        current_labels = img_df.loc[current_row, "label"].split(",")
        selected_labels = col3.multiselect(
            "Current Label", options=target_labels + [""], default=current_labels
        )
        label_dict[img_path] = ",".join(sorted([_ for _ in selected_labels if _ != ""]))
        col3.button(
            "Update Label", on_click=update_label_json, args=(label_path, label_dict)
        )

        #### Step 3
        st.header("3. Label Stats")
        fig, axes = plt.subplots(2, 2)
        fig.set_figheight(8)
        fig.set_figwidth(12)
        img_df["label_category"] = img_df["label"].apply(lambda x: label_category(x))
        img_df.groupby("label_category").count()["img_path"].plot(
            kind="barh", ax=axes[0][0]
        )
        axes[0][0].set_title("Label Category")

        all_labels = extract_all_labels(img_df["label"].values)
        w = Counter(all_labels)
        axes[0][1].barh(list(w.keys()), list(w.values()))
        axes[0][1].set_title("All Labels")

        single_labels = extract_all_labels(
            img_df[img_df["label_category"] == "Single Label"]["label"].values
        )
        w2 = Counter(single_labels)
        axes[1][0].barh(list(w2.keys()), list(w2.values()))
        axes[1][0].set_title("Single Labels")

        multi_labels = extract_multilabels(
            img_df[img_df["label_category"] == "Multi Label"]["label"].values
        )
        w3 = Counter(multi_labels)
        axes[1][1].barh(list(w3.keys()), list(w3.values()))
        axes[1][1].set_title("Multi Labels")

        st.pyplot(fig)
