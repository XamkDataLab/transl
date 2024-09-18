import streamlit as st
import pandas as pd
import json

def load_json_to_df(file_path):
    try:
        return pd.read_json(file_path)
    except ValueError as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

json_file_1 = 'translation1.json'
json_file_2 = 'translation2.json'

df_1 = load_json_to_df(json_file_1)
df_2 = load_json_to_df(json_file_2)

if 'ratings_translation1' not in st.session_state:
    st.session_state['ratings_translation1'] = []

if 'ratings_translation2' not in st.session_state:
    st.session_state['ratings_translation2'] = []

if 'selected_translation' not in st.session_state:
    st.session_state['selected_translation'] = None

if 'page_number' not in st.session_state:
    st.session_state['page_number'] = 0

st.title("Translation Data Display")

abstracts_per_page = 5

if st.button('Show Translation 1'):
    st.session_state['selected_translation'] = 'translation1'
    st.session_state['page_number'] = 0  

if st.button('Show Translation 2'):
    st.session_state['selected_translation'] = 'translation2'
    st.session_state['page_number'] = 0  

def display_abstracts(dataframe, translation_key):
    start_idx = st.session_state['page_number'] * abstracts_per_page
    end_idx = start_idx + abstracts_per_page
    subset_df = dataframe.iloc[start_idx:end_idx]

    current_ratings = (st.session_state['ratings_translation1'] 
                       if translation_key == 'rating_1' 
                       else st.session_state['ratings_translation2'])
    
    for idx, row in subset_df.iterrows():
        with st.container():
            col1, col2 = st.columns(2)
            col1.write(f"**Original (Abstract):**\n{row['abstract']}")
            col2.write(f"**Translated Abstract:**\n{row['translated_abstract']}")

        rating = st.radio(
            f"Rate Translation {start_idx + idx + 1} (1 = Worst, 5 = Best)",
            options=[None, 1, 2, 3, 4, 5],
            index=0,  
            key=f"{translation_key}_{start_idx + idx}"
        )

        if rating is not None:
            if len(current_ratings) <= start_idx + idx:
                current_ratings.append({'index': start_idx + idx, 'rating': rating})
            else:
                current_ratings[start_idx + idx]['rating'] = rating

if st.session_state['selected_translation'] == 'translation1' and df_1 is not None:
    st.subheader("Translation 1 Data")
    display_abstracts(df_1, 'rating_1')

elif st.session_state['selected_translation'] == 'translation2' and df_2 is not None:
    st.subheader("Translation 2 Data")
    display_abstracts(df_2, 'rating_2')

if st.session_state['selected_translation'] is not None:
    num_abstracts = len(df_1) if st.session_state['selected_translation'] == 'translation1' else len(df_2)
    max_page = (num_abstracts - 1) // abstracts_per_page

    col1, col2 = st.columns(2)
    if col1.button('Previous') and st.session_state['page_number'] > 0:
        st.session_state['page_number'] -= 1

    if col2.button('Next') and st.session_state['page_number'] < max_page:
        st.session_state['page_number'] += 1

if st.session_state['selected_translation']:
    ratings = (st.session_state['ratings_translation1'] 
               if st.session_state['selected_translation'] == 'translation1' 
               else st.session_state['ratings_translation2'])

    valid_ratings = [r for r in ratings if r.get('rating') is not None]

    ratings_json = json.dumps(valid_ratings, indent=4)

    if st.button('Save Ratings'):
        with open('ratings.json', 'w') as f:
            f.write(ratings_json)
        st.success('Ratings have been saved to "ratings.json".')

    st.download_button(
        label="Download Ratings as JSON",
        data=ratings_json,
        file_name='ratings.json',
        mime='application/json'
    )
