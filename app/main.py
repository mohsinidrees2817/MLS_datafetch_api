from fastapi import FastAPI, Depends, HTTPException, Body
from typing import List
import pandas as pd
from pydantic import BaseModel
from .database import get_db_connection
from .models import PropertyQuery, PropertyResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI application is running"}

    
class QueryRequest(BaseModel):
    where_clause: str

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return {"status": "success", "message": "Database connection is successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/query_properties/")
def query_properties(query_request: QueryRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = f'''
        SELECT 
            Id, ArchitecturalStyle, StructureType, subType, BedroomCount, BathroomCount, ListPrice, Address_City, ParkingTotal, YearBuilt, LivingAreaSquareFeet
        FROM [dbo].[Properties] 
        WHERE {query_request.where_clause}
    '''

    cursor.execute(sql)
    dataset = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    print(f"Columns: {columns}")
    # print(f"Dataset: {dataset}")
    
    if not dataset:
        return {
            "message": "No properties found with the given criteria",
            "properties": []}
    else:
        selected_columns = ['Id', 'ArchitecturalStyle', 'StructureType', 'subType', 'BedroomCount', 'BathroomCount', 'ListPrice', 'Address_City', 'ParkingTotal', 'YearBuilt', 'LivingAreaSquareFeet']
        
        # Create a list of dictionaries with selected columns
        properties = []
        for row in dataset:
            property_dict = {}
            for idx, column in enumerate(selected_columns):
                property_dict[column] = row[idx]
            properties.append(property_dict)
        
        return {
            "message": "Properties found with the given criteria",
            "properties": properties
        }
    
