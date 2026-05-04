# Importing all required Modules
import os
import logging  # Using for logging to see error in details at the time of debugging
import pyodbc
import struct# ODBC Module which help to connect with DB
from fastapi import FastAPI, HTTPException  # FAST Framework Module which help to create WEB UI for endpoints
# Connection Library/Module to make connection , get the token , run the SQL queries etc.
from msal import ConfidentialClientApplication

# Tagging for easy readbility & categorize functions according to thier actions
tags_metadata = [
    {"name": "Azure SQL DB", "description": "Get data from Azure SQL DB and Post data to Azure SQL DB"},
    {"name": "Get token", "description": "Get token from Service principle"}
]

# Input to the Application title setting to the App
app = FastAPI(title="Data Education Holdings LLC - Azure SQL DB Data API", openapi_tags=tags_metadata)

@app.get("/")
def root():
    return {"message": "Azure SQL DB Data API is running. Visit /docs for endpoints."}


# Load environment variables from .env file using docker.yaml file
SURYA_ID = os.getenv("SURYA_ID")  # Secret value from Azure App secret, you could see docker.yaml file
TENANT_ID = os.getenv("TENANT_ID")  # TENANT_ID from Azure App secret, you could see docker.yaml file
CLIENT_ID = os.getenv("CLIENT_ID")  # CLIENT_ID from Azure App secret, you could see docker.yaml file
DATABASE_URL = os.getenv("DATABASE_URL")  # you could see docker.yaml file for more info
ODBC_DRIVER = "{ODBC Driver 18 for SQL Server}"  # you could see docker.yaml file for more info

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# First step to see whether your Fast API App is working or not from WEB UI
@app.get("/hello", tags=["Azure SQL DB"])
async def get_hello():
    return {"Greeting": "Hello world"}


# Getting token AUTH Token from Azure Graph API to access azure resources
@app.get("/get_access_token", tags=["Get token"])
def get_access_token():
    try:
        authority_url = f"https://login.microsoftonline.com/{TENANT_ID}"
        app = ConfidentialClientApplication(
            CLIENT_ID, authority=authority_url, client_credential=SURYA_ID
        )

        token_response = app.acquire_token_for_client(scopes=["https://database.windows.net/.default"])

        if "access_token" in token_response:
            return token_response['access_token']
        else:
            raise HTTPException(status_code=401, detail="Could not obtain access token")

    except Exception as e:
        logger.error(f"Error while getting access token: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not obtain access token")


# Making DB connection using token & UID , password
def get_db_conn():
    token = get_access_token()

    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    connection_string = (
        f"Driver={ODBC_DRIVER};"
        f"Server=tcp:{DATABASE_URL},1433;"
        f"Database=free-sql-db-3748480;"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(connection_string, attrs_before={
        1256: token_struct
    })
    return conn



# Once connection established then staring running your SQL on Azure SQL DB.
@app.get("/get_data", tags=["Azure SQL DB"])
def get_database_data():
    try:
        conn = get_db_conn()

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM happy_customer_score")
        result = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]
        return {"data": data}

    except Exception as e:
        logger.error(f"Error while fetching data from database: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch data from database")


# Function to post data to the database and this simple way to insert data one by one.
@app.post("/post_data", tags=["Azure SQL DB"])
def post_data_to_database():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        # Define your SQL query to insert data into the table
        sql_query = ("INSERT INTO happy_customer_score VALUES ('hcs_physical','physical','STO090','Denmark',90);"
                     "INSERT INTO happy_customer_score VALUES ('hcs_physical','physical','STO088','India',90);"
                     "INSERT INTO happy_customer_score VALUES ('hcs_physical','physical','STO089','USA',90);")

        # Execute the SQL query for each data item
        cursor.execute(sql_query)

        # Commit the transaction
        conn.commit()

        return {"message": "Data posted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post data to the database: {str(e)}")


#TODO
# You have to write & test below two function with proper updated & deletion code.

# Function to Update/Patch data in the database
@app.post("/update_data", tags=["Azure SQL DB"])
def update_data_in_database():
    try:
        print("Please write the Python code for updating Data in DB table")

        return {"message": "Data updated/patched successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Update/Patch data in the database: {str(e)}")


# Function to Delete data from the database
@app.post("/delete_data", tags=["Azure SQL DB"])
def delete_data_from_database():
    try:
        print("Please write the Python code for deleting Data from DB table")

        return {"message": "Data Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Delete data from the database: {str(e)}")