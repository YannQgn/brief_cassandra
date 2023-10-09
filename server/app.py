from fastapi import FastAPI, HTTPException
from cassandra.cluster import Cluster
import numpy as np
import uvicorn

app = FastAPI()
cassandra_host = '172.22.0.2'
cluster = Cluster([cassandra_host])
keyspace = 'resto'

@app.on_event("startup")
async def startup_event():
    try:
        app.state.cluster = cluster
        app.state.session = cluster.connect(keyspace)
    except Exception as e:
        print(f"Erreur de connexion Cassandra : {str(e)}")
        app.state.session = None

@app.on_event("shutdown")
async def shutdown_event():
    if app.state.session:
        app.state.session.shutdown()

@app.get("/restaurant/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    if not app.state.session:
        return {"message": "Erreur de connexion à Cassandra"}
    query = f"SELECT * FROM restaurant WHERE id = {restaurant_id}"
    result = app.state.session.execute(query)
    restaurant_data = result.one()
    if restaurant_data:
        return restaurant_data
    else:
        return {"message": "Restaurant non trouvé"}

@app.get("/cuisine-types")
def get_cuisine_types():
    if not app.state.session:
        return {"message": "Erreur de connexion à Cassandra"}
    query = "SELECT cuisinetype FROM restaurant"
    result = app.state.session.execute(query)
    cuisine_types = [row.cuisinetype for row in result]
    if cuisine_types:
        return cuisine_types
    else:
        return {"message": "Aucun type de cuisine trouvé"}

@app.get("/restaurants-by-cuisine/{cuisine_type}")
def get_restaurants_by_cuisine(cuisine_type: str):
    if not app.state.session:
        return {"message": "Erreur de connexion à Cassandra"}
    query = f"SELECT * FROM restaurant WHERE cuisinetype = '{cuisine_type}'"
    result = app.state.session.execute(query)
    restaurants = []
    for row in result:
        restaurant_dict = {
            "id": row.id,
            "name": row.name,
            "cuisine_type": row.cuisinetype,
        }
        restaurants.append(restaurant_dict)
    if restaurants:
        return restaurants
    else:
        return {"message": "Aucun restaurant trouvé"}

@app.get("/first-five-restaurants")
def get_top_restaurants_by_grade_first_5():
    if not app.state.session:
        return {"message": "Erreur de connexion à Cassandra"}
    query = "SELECT * FROM restaurant LIMIT 5"
    result = app.state.session.execute(query)
    top_restaurants = []
    for row in result:
        restaurant_dict = {}
        for column, value in row._asdict().items():
            if isinstance(value, np.int64):
                restaurant_dict[column] = int(value)
            else:
                restaurant_dict[column] = value
        top_restaurants.append(restaurant_dict)
    if top_restaurants:
        return top_restaurants
    else:
        return {"message": "Aucun restaurant trouvé"}

@app.get("/restaurant-inspections/{restaurant_id}")
def get_inspections(restaurant_id: int):
    if not app.state.session:
        raise HTTPException(status_code=500, detail="Erreur de connexion à Cassandra")
    query = f"SELECT * FROM inspection WHERE idrestaurant = {restaurant_id}"
    result = app.state.session.execute(query)
    inspections = []
    for row in result:
        inspection_details = {
            "inspectiondate": row.inspectiondate,
            "criticalflag": row.criticalflag,
            "grade": row.grade,
            "score": row.score,
            "violationcode": row.violationcode,
            "violationdescription": row.violationdescription,
        }
        inspections.append(inspection_details)
    if inspections:
        return {"inspection_count": len(inspections), "inspections": inspections}
    else:
        raise HTTPException(status_code=404, detail="Restaurant non trouvé ou aucune inspection trouvée")

@app.get("/grade-types")
def get_grade_types():
    if not app.state.session:
        return {f"message": "Erreur de connexion à Cassandra"}
    query = "SELECT grade FROM inspection"
    result = app.state.session.execute(query)
    grade_types = [row.grade for row in result if row.grade is not None]
    if grade_types:
        return grade_types
    else:
        return {f"message": "Aucun type de grade trouvé"}

@app.get("/restaurants-by-grade/{grade}")
def get_restaurants_by_grade(grade: str):
    if not app.state.session:
        return {f"message": "Erreur de connexion à Cassandra"}
    query = f"SELECT * FROM inspection WHERE grade = '{grade}' LIMIT 10"
    result = app.state.session.execute(query)
    restaurants = []
    for row in result:
        # récup l'id du restaurant à partir de la colonne "idrestaurant" de la table d'inspection
        restaurant_id = row.idrestaurant
        restaurant_query = f"SELECT * FROM restaurant WHERE id = {restaurant_id}"
        restaurant_result = app.state.session.execute(restaurant_query)
        restaurant_data = restaurant_result.one()
        if restaurant_data:
            restaurant_dict = {
                "id": restaurant_data.id,
                "name": restaurant_data.name,
                "cuisine_type": restaurant_data.cuisinetype,
                "grade": row.grade,
            }
            restaurants.append(restaurant_dict)
    if restaurants:
        return restaurants
    else:
        return {f"message": "Aucun restaurant trouvé pour ce type de grade"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8502)