# import streamlit as st
# values = st.slider(
#     'Select a range of values',
#     0.0, 100.0, (25.0, 75.0), key="slider_value")
# print(values)
# print(st.session_state["slider_value"])
# st.write('Values:', values)

import json 


def load_session(session_file):
    with open(session_file) as json_file:
        data = json_file.read()
    return json.loads(data)


def save_session(session_file, session_state):
    with open(session_file, "w") as outfile:
        json_dumps = json.dumps(dict(session_state))
        outfile.write(json_dumps)


tem_data = {"a": 1, "b": "hello", "c": {"d": 1, "e": (10, 5)}, "f": (1.2, 2.3), "g": [10.1, 20.1]}
print(tem_data)
print(json.dumps(tem_data))
save_session("tem.json", tem_data)
print(load_session("tem.json"))