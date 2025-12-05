from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, inspect, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
metadata = MetaData()

TABLE_NAME = "financial_records"

def sync_schema_and_insert(data: list[dict]):
    """
    1. Inspects keys in the new data.
    2. Checks existing DB columns.
    3. Alters table to add missing columns.
    4. Inserts data.
    """
    if not data:
        return {"status": "skipped", "reason": "No tabular data found"}

    # 1. Identify all unique keys in this batch
    incoming_keys = set()
    for record in data:
        incoming_keys.update(record.keys())

    inspector = inspect(engine)

    with engine.connect() as conn:
        # 2. Create table if it doesn't exist
        if not inspector.has_table(TABLE_NAME):
            cols = [Column('id', Integer, primary_key=True, autoincrement=True)]
            for key in incoming_keys:
                cols.append(Column(key, String, nullable=True))
            
            # extend_existing=True allows redefining the table object safely
            Table(TABLE_NAME, metadata, *cols, extend_existing=True)
            metadata.create_all(engine)
        else:
            # 3. Dynamic Schema Evolution (The "Industrial" Touch)
            existing_cols = {col['name'] for col in inspector.get_columns(TABLE_NAME)}
            new_cols = incoming_keys - existing_cols

            for col_name in new_cols:
                # SQLite supports ADD COLUMN. 
                # We use text() to safely execute raw SQL for schema alteration
                print(f"Migrating Schema: Adding column '{col_name}'")
                conn.execute(text(f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{col_name}" TEXT'))
            
            conn.commit()

        # 4. Insert Data
        # Re-reflect table to get updated schema
        meta = MetaData()
        table = Table(TABLE_NAME, meta, autoload_with=engine)
        
        conn.execute(table.insert(), data)
        conn.commit()

    return {"status": "success", "rows_inserted": len(data), "columns_detected": list(incoming_keys)}

def fetch_all_records():
    inspector = inspect(engine)
    if not inspector.has_table(TABLE_NAME):
        return []
    
    with engine.connect() as conn:
        # Return as list of dicts
        result = conn.execute(text(f"SELECT * FROM {TABLE_NAME}"))
        return [dict(row._mapping) for row in result]