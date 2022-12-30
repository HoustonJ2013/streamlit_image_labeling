import json
import streamlit as st


def load_session(session_file):
    with open(session_file) as json_file:
        data = json_file.read()
    return json.loads(data)


def save_session(session_file, session_state):
    with open(session_file, "w") as outfile:
        json_dumps = json.dumps(dict(session_state))
        outfile.write(json_dumps)


def update_session_file():
    if "session_file" in st.session_state:
        save_session(st.session_state["session_file"], st.session_state)


def load_label_json(label_path):
    with open(label_path) as json_file:
        data = json_file.read()
    return json.loads(data)


def update_label_json(label_path, label_dict):
    with open(label_path, "w") as outfile:
        json_dumps = json.dumps(dict(label_dict))
        outfile.write(json_dumps)


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            # del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True
