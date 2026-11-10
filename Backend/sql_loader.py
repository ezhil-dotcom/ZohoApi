import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    conn_str = (
        f"DRIVER={{{os.getenv('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def _clean(name: str) -> str:
    # square brackets make odd column names safe; strip any bracket inside the name
    return "[" + str(name).replace("]", "").replace("[", "") + "]"


def push_rows(table_name: str, rows: list, replace: bool = False, id_column: str = "ID"):
    if not rows:
        return {"received": 0, "inserted": 0, "skipped": 0}
    print("push function starts")

    columns = list(rows[0].keys())
    print("Columns:", len(columns), "| has ID:", id_column in columns)
    if id_column not in columns:
        raise Exception(f"'{id_column}' not found in Zoho data. Columns: {columns}")

    col_defs = ", ".join(f"{_clean(c)} NVARCHAR(MAX) NULL" for c in columns)
    col_names = ", ".join(_clean(c) for c in columns)
    placeholders = ", ".join("?" for _ in columns)
    table = _clean(table_name)
    id_col = _clean(id_column)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.fast_executemany = True

        # create the table the first time
        cur.execute(
            f"IF OBJECT_ID(N'{table_name}', N'U') IS NULL "
            f"CREATE TABLE {table} ({col_defs})"
        )

        existing_ids = set()
        if replace:
            # full reload: empty the table first
            cur.execute(f"TRUNCATE TABLE {table}")
        else:
            # IDs already in SQL
            cur.execute(f"SELECT {id_col} FROM {table}")
            existing_ids = {str(r[0]) for r in cur.fetchall() if r[0] is not None}

        # keep only rows whose ID is new
        new_rows = []
        seen = set()
        for r in rows:
            rid = r.get(id_column)
            if rid in (None, ""):
                continue                     # no ID, can't be matched, skip
            rid = str(rid)
            if rid in existing_ids or rid in seen:
                continue                     # already in SQL, or repeated in this export
            seen.add(rid)
            new_rows.append(r)

        values = [
            tuple(None if r.get(c) in (None, "") else str(r.get(c)) for c in columns)
            for r in new_rows
        ]

        if values:
            cur.executemany(
                f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", values
            )
        conn.commit()

        print(f"Received {len(rows)} | already in SQL {len(existing_ids)} | inserted {len(values)}")
        return {
            "received": len(rows),
            "inserted": len(values),
            "skipped": len(rows) - len(values),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()