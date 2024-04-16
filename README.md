# Promptbase
## Overview
A webapp to store and quickly access my favorite ChatGPT prompts✨.

View my web app at: https://510lab3-jxf9ne4fp9atv6uyg56zsd.streamlit.app/

Contains 3 parts: 
- An Input Box for new prompts.
- Prompts' List for filter(by time) and sort (is/not favorite).
- Prompts Dataset for serch, edit, and manage prompts here. Also choose a Template to render a new prompt.

## Getting Started
1. Signup for supabase
2. Create a new project database and connect to github repo
3. Design a Prompt class for data model
4. Create a streamlit app
```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run the app
streamlit run app.py
```

## Lessons Learned
- The code can be divided into 3 parts: 
    1. __Database Setup__  
```setup_database()```: establishes a connection to the PostgreSQL database using a connection string retrieved from environment variables. It creates a cursor and sets up a table named prompts if it doesn't exist already. The table has columns for ID, title, prompt content, favorite status, and timestamps. It returns the connection and cursor for further use.
    2. __Streamlit Forms and Interface__  
```prompt_form()```: creates a form in Streamlit to submit new prompts. It handles input for the prompt’s title, content, and favorite status. It checks if the title and prompt fields are filled before returning a new Prompt object with the entered data.
    3. __Main Execution Block__
```if __name__ == "__main__"```:
Sets up the Streamlit page with a title and subheader.
Calls setup_database() to prepare the database.
Handles new prompt submissions. If a new prompt is returned from prompt_form(), it's inserted into the database. Any database errors are caught and displayed.  
Calls display_prompts() to show existing prompts.
Closes the database connection after operations are complete.

- Remember to install the pyperclip both via ```pip install``` and in ```requirements.txt```
- Have a new learning about the "templete": use ``` { }``` to realize reuse of a established prompts, and the ```{ }``` can be auto recognized.
- Not forget to set secret
    ``` 
    - Click the three dots, in “settings” you can find “secret”  
    - Basically copy the content of .env into the secrets section of streamlit cloud  
    - Adding “ “ around the url portion
```

## Question
- Why the popover can't be closed in streamlit?
- The development in streamlit seems highly relied on the established features, and seems not so flexible.
## Todo
- Make the UI more intuitive.