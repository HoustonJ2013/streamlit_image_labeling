# streamlit_image_labeling
Recent advances in self-supervised learning has enabled the possibilities of building robust deep learning models with much fewer human labels. The number of required labels could be only 1% of the number required by the supervised version. The quality of the labels matters in this case. A quick labeling tool is built here for data scientist to review, modify and label the small amount of images. The tool is good for the internal use of a small team and not for enterprise. The sticky session and username and password are managed in a local folder ".streamlit/". You need to create the folder and add your username and password following the [streamlit instruction](https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso) option2/step1.


## multilabel_image_labeling

multilabel app for image annotation. You need to install the required packages in your conda environment before use. After clone the repo and create a new conda environment, install the required packages. 
```
pip install -r requirements.txt
```
Then create a local folder ".streamlit/" if the folder doesn't exist. Set up the username and password. 
```
streamlit run streamlit_image_labeling/multilabel_image_labeling.py 
```
Login with your username and password

<img src="tests/log_in_page.png" alt="login" width="400"/>

Load existing session associated with your username, or load another session from file, or create a new session. 

<img src="tests/load_or_new_session.png" alt="session" width="400"/>

Specify the paths to the image files using the folder path or a csv file. Specify the file to save the label in json format. 

<img src="tests/specify_image_path_and_label_save_file.png" alt="image_file" width="400"/>

Navigate the images using the button on the left panel and label the images using the multiselect button on the right panel. Click "update label" button to save the label. 

<img src="tests/label_image_with_multilabel_dropdown.png" alt="labeling" width="400"/>

Review some statistics of the labels. 

<img src="tests/label_stats.png" alt="label_stats" width="400"/>

