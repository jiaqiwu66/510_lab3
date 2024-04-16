import os
from dataclasses import dataclass
import datetime
import re
import streamlit as st
import psycopg2
from dotenv import load_dotenv
import pandas as pd
import pyperclip

load_dotenv()


@dataclass
class Prompt:
    title: str
    prompt: str
    template: str
    is_favorite: bool
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None


def setup_database():
    new_connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    new_cursor = new_connection.cursor()
    new_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prompts (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            template TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    new_connection.commit()
    return new_connection, new_cursor


def prompt_form(prompt=None):
    default = Prompt("", "", "", False) if prompt is None else prompt
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=default.title)
        prompt_content = st.text_area("Prompt", height=200, value=default.prompt)
        template = st.text_area("Template", height=200, value=default.template)
        is_favorite = st.checkbox("Favorite", value=default.is_favorite)

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not title or not prompt_content:
                st.error('Please fill in both the title and prompt fields.')
                return
            return Prompt(title, prompt_content, template, is_favorite)


def display_prompts(display_cursor):
    display_cursor.execute("SELECT * FROM prompts ORDER BY created_at DESC")  # Default sort by created date
    prompts = display_cursor.fetchall()
    # TODO: Add a sort by date
    st.subheader("Prompts' List")
    st.markdown("Filter and sort here")
    with st.expander("See Prompts in Table View"):
        option = st.multiselect(
            'Which kind of prompt you want:',
            ["Favorite", "Not Favorite"])
        if len(option) == 2 or len(option) == 0:
            display_cursor.execute("SELECT * FROM prompts ORDER BY created_at DESC")  # Default sort by created date
        else:
            if option[0] == "Favorite":
                value = True
            else:
                value = False
            display_cursor.execute(f"SELECT * FROM prompts WHERE is_favorite is {value} ORDER BY created_at DESC")
        prompts = display_cursor.fetchall()
        fields = ["id", "title", "prompt", "template", "is_favorite", "created_at", "updated_at"]
        data = []
        for p in prompts:
            data.append(dict(zip(fields, p)))
        st.dataframe(pd.DataFrame(data), )


    # TODO: Add a search bar
    st.subheader("Prompts Dataset")
    st.markdown("Serch, edit, and manage prompts here")
    search_term = st.text_input(label="Search bar", placeholder="Please input the keyword", label_visibility="hidden")
    if search_term:
        display_cursor.execute(f"SELECT * FROM prompts "
                               f"WHERE title LIKE '%{search_term}%' OR prompt LIKE '%{search_term}%' "
                               f"ORDER BY created_at DESC")
    # update the prompt list
    else:
        display_cursor.execute("SELECT * FROM prompts ORDER BY created_at DESC")  # Default sort by created date
    prompts = display_cursor.fetchall()

    # TODO: Add favorite button
    for p in prompts:
        heart = ""
        if p[4]:
            heart = "❤️"
        with st.expander(f"{p[1]} {heart}"):
            # TODO: Add a edit function
            st.code(f"Prompt: {p[2]}")
            st.code(f"Template: {p[3]}")
            st.code(f"Created at: {p[-2]}")
            st.code(f"Updated at: {p[-1]}")
            _, buttons = st.columns(2)
            with buttons:
                col1, col2, col3 = st.columns((1.5, 1, 1))
                with col1:
                    fill_popover = st.popover("Fill Template")
                    with fill_popover:
                        template = p[3]
                        placeholders = re.findall(r'\{(.*?)}', template)
                        values = {}
                        if placeholders:
                            for placeholder in placeholders:
                                value = st.text_input(f"Value for {placeholder}", key=f"{placeholder}_{p[0]}")
                                values[placeholder] = value
                            render_button = st.button("Render Prompt", key=f"render_{p[0]}")
                            if render_button:
                                rendered_prompt = template.format(**values)
                                st.text_area("Rendered Prompt", value=rendered_prompt, height=150)
                                st.button("Copy to Clipboard", on_click=lambda: pyperclip.copy(rendered_prompt))

                with col2:
                    edit_popover = st.popover("Edit")
                    with edit_popover:
                        st.markdown("Edit Prompt")
                        title = st.text_input("Prompt Title:", key=f"title_{p[0]}", value=p[1])
                        prompt_content = st.text_area("Prompt", key=f"prompt_{p[0]}", height=100, value=p[2])
                        template = st.text_input("Template:", key=f"template_{p[0]}", value=p[3])
                        is_favorite = st.checkbox("Favorite", key=f"favorite_{p[0]}", value=p[4])
                        confirm = st.button("Confirm", key=f"confirm_{p[0]}")

                        if confirm:
                            if not title or not prompt_content:
                                st.error('Please fill in both the title and prompt fields.')
                                return
                            display_cursor.execute(
                                "UPDATE prompts SET title=%s, prompt=%s, template=%s, is_favorite=%s, updated_at=%s "
                                "WHERE id=%s",
                                (title, prompt_content, template, is_favorite, datetime.datetime.now(), p[0]))
                            connection.commit()
                            st.rerun()
                with col3:
                    if st.button("Delete", key=f"delete_{p[0]}"):
                        display_cursor.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                        connection.commit()
                        st.rerun()


if __name__ == "__main__":
    st.title("PromptBase")
    st.markdown("A simple app to store and retrieve prompts")
    st.subheader("Add New Prompt")

    connection, cursor = setup_database()

    new_prompt = prompt_form()
    if new_prompt:
        try:
            cursor.execute(
                "INSERT INTO prompts (title, prompt, template, is_favorite) VALUES (%s, %s, %s, %s)",
                (new_prompt.title, new_prompt.prompt, new_prompt.template, new_prompt.is_favorite)
            )
            connection.commit()
            st.success("Prompt added successfully!")
        except psycopg2.Error as e:
            st.error(f"Database error: {e}")

    display_prompts(cursor)
    connection.close()

