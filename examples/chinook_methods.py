from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import inspect

from agents.utils import get_engine_for_chinook_db


def get_db_table_names():
    """Get list of all table names in the database."""
    engine = get_engine_for_chinook_db()
    db = SQLDatabase(engine)
    return db.get_usable_table_names()


def get_detailed_table_info():
    """Get detailed information for each table including schema, keys, and sample data."""
    engine = get_engine_for_chinook_db()
    db = SQLDatabase(engine)
    inspector = inspect(engine)
    table_names = db.get_usable_table_names()

    detailed_info = {}

    for table_name in table_names:
        table_info = {
            "columns": [],
            "primary_key": None,
            "foreign_keys": [],
            "sample_data": [],
        }

        # Get table schema using SQLAlchemy inspector
        try:
            columns = inspector.get_columns(table_name)
            for column in columns:
                table_info["columns"].append(
                    {
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column.get("nullable", "unknown"),
                    }
                )

            # Get primary key
            pk = inspector.get_pk_constraint(table_name)
            if pk["constrained_columns"]:
                table_info["primary_key"] = pk["constrained_columns"]

            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                table_info["foreign_keys"].append(
                    {
                        "columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"],
                    }
                )

        except Exception as e:
            table_info["error"] = str(e)

        # Get sample data (first 3 rows)
        try:
            sample_query = f"SELECT * FROM {table_name} LIMIT 3"
            sample_result = db.run(sample_query)
            table_info["sample_data"] = sample_result
        except Exception as e:
            table_info["sample_data_error"] = str(e)

        detailed_info[table_name] = table_info

    return detailed_info


def get_schema_overview():
    """Get a concise overview of all table schemas."""
    engine = get_engine_for_chinook_db()
    db = SQLDatabase(engine)
    inspector = inspect(engine)
    table_names = db.get_usable_table_names()

    schema_overview = {}

    for table_name in table_names:
        try:
            columns = inspector.get_columns(table_name)
            schema_overview[table_name] = [
                {"name": col["name"], "type": str(col["type"])} for col in columns
            ]
        except Exception as e:
            schema_overview[table_name] = {"error": str(e)}

    return schema_overview


# Example usage
if __name__ == "__main__":
    print("=== Basic Table Names ===")
    table_names = get_db_table_names()
    print(table_names)
    print()

    print("=== Detailed Table Information ===")
    detailed_info = get_detailed_table_info()
    for table_name, info in detailed_info.items():
        print(f"\n--- Table: {table_name} ---")

        if "error" in info:
            print(f"Error: {info['error']}")
        else:
            print("Columns:")
            for col in info["columns"]:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")

            if info["primary_key"]:
                print(f"  Primary Key: {info['primary_key']}")

            if info["foreign_keys"]:
                print("  Foreign Keys:")
                for fk in info["foreign_keys"]:
                    print(
                        f"    {fk['columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                    )

        if "sample_data_error" in info:
            print(f"Sample data error: {info['sample_data_error']}")
        else:
            print(f"Sample data: {info['sample_data']}")

        print("-" * 50)

    print("\n=== Database Schema Overview ===")
    schema_overview = get_schema_overview()
    for table_name, columns in schema_overview.items():
        print(f"\n{table_name}:")
        if isinstance(columns, list):
            for column in columns:
                print(f"  {column['name']}: {column['type']}")
        else:
            print(f"  Error: {columns['error']}")
