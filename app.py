import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TMDB_API_KEY = ["YOUR_TMDB_API_KEY"]  # Replace with your actual TMDB API key

# Retry temporary connection errors
session = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    try:
        response = session.get(
            url,
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US"
            },
            timeout=15
        )

        if response.status_code == 401:
            st.error("TMDB authentication failed. Check your API key.")
            return None

        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

        return None

    except requests.exceptions.RequestException as error:
        print(f"Error fetching poster for {movie_id}: {error}")
        return None






def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        recommended_movie_id = movies.iloc[i[0]]["movie_id"]
        recommended_movie_title = movies.iloc[i[0]]["title"]
        # we will fetch the poster usind the  api and then we will append the title of the movie to the recommended_movies list
        recommended_movies.append(recommended_movie_title)
        recommended_movies_posters.append(fetch_poster(recommended_movie_id))

    return recommended_movies, recommended_movies_posters
    

movies_list = pickle.load(open('movies.pkl', 'rb'))

# Extract movie IDs and titles
movies_id = movies_list['movie_id'].values
movie_titles = movies_list['title'].values

# Create DataFrame with both columns
movies = pd.DataFrame({
    "movie_id": movies_list["movie_id"].values,
    "title": movies_list["title"].values
})

similarity = pickle.load(open('similarity.pkl', 'rb'))


st.title("Movies Recommendation System")
selected_movie_name = st.selectbox(
    "Select a movie:",
        movies["title"].values  
)



if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    st.subheader("Recommended Movies")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
             st.text(names[0])
             if posters[0] is not None:
               st.image(posters[0], use_column_width=True)
             else:
               st.write("Poster unavailable")
        
    with col2:
             st.text(names[1])
             if posters[1] is not None:
               st.image(posters[1], use_column_width=True)
             else:
               st.write("Poster unavailable")       
        
    with col3:
             st.text(names[2])
             if posters[2] is not None:
               st.image(posters[2], use_column_width=True)
             else:
               st.write("Poster unavailable")

    with col4:
             st.text(names[3])
             if posters[3] is not None:
               st.image(posters[3], use_column_width=True)
             else:
               st.write("Poster unavailable")     
    
    with col5:
             st.text(names[4])
             if posters[4] is not None:
               st.image(posters[4], use_column_width=True)
             else:
               st.write("Poster unavailable")     

    url = "https://api.themoviedb.org/3/configuration"

    try:
      response = requests.get(url, timeout=15)
      print("Status code:", response.status_code)
      print(response.text[:500])
    except requests.RequestException as e:
      print("Connection failed:", e)
