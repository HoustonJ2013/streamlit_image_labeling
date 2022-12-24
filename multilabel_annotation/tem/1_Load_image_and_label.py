import streamlit as st
import os
import pandas as pd
import json

# home_directory = os.path.expanduser('~')
# session_file = os.path.join(home_directory, ".streamlit_session.json")

# if os.path.exists(session_file):
#     with open(session_file) as json_file:
#         data = json.load(json_file)
#     st.session_state.update(data)

st.header("1. Set the Image Path")
image_folder_path = st.text_input("Please input the path to the folder containing images", key="image_folder")
st.text("OR")
image_csv_path = st.text_input("Please input the path to csv file with 'img_path' column to the images", key="image_csv_path")
st.header("2. Set the Label Path")
label_path = st.text_input("Please input the path to save the label (json format)", key="label_path")
st.text("OR")
label_uploaded_file = st.file_uploader("Choose the existing labels (json format)")

img_df = pd.DataFrame(columns=["img_path", "img_name", "label"])

if image_folder_path != "":
    if os.path.exists(image_folder_path) is False: 
        st.error("%s doesn't exist"%(image_folder_path))

    img_paths = [os.path.join(image_folder_path, _) for _ in os.listdir(image_folder_path)]
    img_names = [_.split("/")[-1].split(".")[0] for _ in img_paths]
    img_df = pd.DataFrame.from_dict({"img_path": img_paths, 
                                     "img_name": img_names,
                                     "label": [""] * len(img_paths)})

if image_csv_path != "":
    if os.path.exists(image_csv_path) is False: 
        st.error("%s doesn't exist"%(image_csv_path))
    img_df = pd.read_csv(image_csv_path)
    img_df["img_name"] = img_df["img_path"].apply(lambda x: x.split("/")[-1].split(".")[0])
    img_df["label"] = [""] * len(img_df)
    if "img_path" not in img_df:
        st.error("'img_path' doesn't exist in the table %s"%(image_csv_path))

if label_path == "" and label_uploaded_file is None:
    st.error("label_path is not specified, please set the path to save the labels")

st.text("Loaded Images and Labels")
# if st.button("Save_session"):
#     st.write(st.session_state)
#     with open(session_file, "w") as outfile:
#         json.dump(dict(st.session_state), outfile)
st.dataframe(img_df, width=400, height=300)
st.write({k:v for k, v in st.session_state.items()})
# st.session_state