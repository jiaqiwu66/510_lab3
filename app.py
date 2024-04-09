import os
from dataclasses import dataclass

import streamlit as st
import streamlit_pydantic as sp
from pydantic import BaseModel, Field
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# connect to database
con = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)
# run before forst time

@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool = False
    created_at: str = None
    update_at: str = None

def prompt_form(prompt=Prompt("","")):
    """
    TODO: Add validation to the form, so that the title and prompt are required.
    """
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt = st.text_area("Prompt", height=200, value=prompt.prompt)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return Prompt(title, prompt)


# form part
st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s)", 
                (prompt.title, prompt.prompt,prompt.is_favorite,))
    con.commit()
    st.success("Prompt added successfully!")

cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()

"""
prompts = [
    (1,"title1", "prompt1", True,), ->p[0] ->id, p[1] ->"title1", p[2] -> "prompt1"
    (2,"title2", "prompt2", True,),
    (3,"title3", "prompt3", True,),

]

"""

# TODO: Add a search bar
# TODO: Add a sort by date
# TODO: Add favorite button
for p in prompts:
    with st.expander(p[1]):
        st.code(p[2])
        # TODO: Add a edit function
        if st.button("Delete", key=p[0]):
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.rerun()