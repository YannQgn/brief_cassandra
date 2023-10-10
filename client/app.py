import pandas as pd
import streamlit as st
import requests

def get_restaurant_info(restaurant_id):
    response = requests.get(f"http://fastapi-app:8502/restaurant/{restaurant_id}")
    if response.status_code == 200:
        restaurant_data = response.json()
        st.write(restaurant_data)
    else:
        st.write("Restaurant non trouvé")

def search_restaurants_by_cuisine(cuisine_type):
    try:
        response = requests.get(f"http://fastapi-app:8502/restaurants-by-cuisine/{cuisine_type}")
        if response.status_code == 200:
            restaurants = response.json()
            if restaurants:
                st.write(restaurants)
            else:
                st.write("Aucun restaurant trouvé")
        else:
            st.write("Erreur lors de la récupération des données")
    except requests.exceptions.ConnectionError:
        st.write("Erreur de connexion à l'API FastAPI")

response = requests.get("http://fastapi-app:8502/cuisine-types")
if response.status_code == 200:
    cuisine_type_list = list(set(response.json())) # pas de doublon
    cuisine_type_list.sort() # ordre alphabétique
else:
    cuisine_type_list = []

def get_inspections_and_count(restaurant_id_inspection):
    response = requests.get(f"http://fastapi-app:8502/restaurant-inspections/{restaurant_id_inspection}")
    if response.status_code == 200:
        inspection_data = response.json()
        inspection_count = inspection_data["inspection_count"]
        inspections = inspection_data["inspections"]

        st.write(f"Nombre d'inspections : {inspection_count}")

        if inspections:
            st.write("Détails des inspections :")
            for inspection in inspections:
                st.write(inspection)
        else:
            st.write("Aucune inspection trouvée")
    else:
        st.write("Restaurant non trouvé ou aucune inspection trouvée")

def get_top_restaurants_by_grade(grade):
    response = requests.get(f"http://fastapi-app:8502/restaurants-by-grade/{grade}")
    if response.status_code == 200:
        restaurant_names = response.json()
        if restaurant_names:
            st.write(f"Noms des 10 premiers restaurants avec le grade '{grade}':")
            for name in restaurant_names:
                st.write(name)
        else:
            st.write(f"Aucun restaurant trouvé avec le grade '{grade}'")
    else:
        st.write("Erreur lors de la récupération des données")

response_grade = requests.get("http://fastapi-app:8502/grade-types")

if response_grade.status_code == 200:
    grade_type_list = list(set(response_grade.json()))
    grade_type_list.sort()
else:
    grade_type_list = []

st.title("Restaurant API")

st.markdown("Les 5 premiers restaurants")
response = requests.get(f"http://fastapi-app:8502/first-five-restaurants")
if response.status_code == 200:
    first_five_restaurants = response.json()
    if first_five_restaurants:
            df = pd.DataFrame(first_five_restaurants, columns=["id", "borough", "buildingnum", "cuisinetype", "name", "phone", "street", "zipcode"])
            st.table(df)
    else:
        st.write("Aucun restaurant trouvé")
else:
    st.write("Erreur lors de la récupération des données")

restaurant_id = st.text_input("Entrez l'ID du restaurant :")
if st.button("Obtenir informations du restaurant"):
    get_restaurant_info(restaurant_id)

cuisine_types = st.selectbox("Sélectionnez le type de cuisine :", cuisine_type_list)
if st.button("Rechercher par type de cuisine"):
    search_restaurants_by_cuisine(cuisine_types)

st.title("Obtenir le Nombre d'Inspections")

restaurant_id_inspection = st.text_input("Entrez l'ID du restaurant pour les inspections :")
if st.button("Obtenir le nombre d'inspections"):
    get_inspections_and_count(restaurant_id_inspection)

selected_grade = st.selectbox("Sélectionnez le type de grade :", grade_type_list)
if st.button("Obtenir les noms des restaurants par grade"):
    get_top_restaurants_by_grade(selected_grade)