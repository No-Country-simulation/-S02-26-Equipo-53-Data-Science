
import sys
import os

# Explicitly add the libs directory using absolute path
libs_path = r"e:\OSCAR\HACKATONES\data-science-grupo-26\libs"
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

print(f"DEBUG: sys.path[0] is {sys.path[0]}")

try:
    import psycopg2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import modules: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Database connection parameters
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_schema = os.getenv("DB_SCHEMA", "raw")

print(f"Connecting to {db_host}:{db_port} / {db_name} as {db_user} (Schema: {db_schema})")

try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_pass
    )
    
    cursor = conn.cursor()
    
    # Query to list tables in the schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s
    """, (db_schema,))
    
    tables = cursor.fetchall()
    
    if not tables:
        print(f"No tables found in schema '{db_schema}'. Checking 'public' schema just in case...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        if tables:
            print("Found tables in 'public' schema instead.")
            db_schema = 'public'
    
    for table in tables:
        table_name = table[0]
        print(f"\n[TABLE] {table_name}")
        
        # Query to list columns for the table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (db_schema, table_name))
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (Nullable: {col[2]})")
            
    conn.close()
    print("\nDone.")

except Exception as e:
    print(f"Database Error: {e}")
