
import sys
import os
import psycopg2
from dotenv import load_dotenv

# Add libs to path
libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
sys.path.insert(0, libs_path)

load_dotenv()

# Check current environment variables
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_SCHEMA:", os.getenv("DB_SCHEMA", "public"))

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    
    schema = os.getenv("DB_SCHEMA", "raw")
    print(f"\n--- Tables in schema '{schema}' ---")
    
    with conn.cursor() as cursor:
        query_tables = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
        cursor.execute(query_tables, (schema,))
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            query_columns = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """
            cursor.execute(query_columns, (schema, table_name))
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
    conn.close()

except Exception as e:
    print(f"Error: {e}")
