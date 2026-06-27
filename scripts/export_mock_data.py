import sqlite3
import os
from pathlib import Path

def export_db():
    db_path = Path("database/ai_panel.db")
    sql_path = Path("database/mock_data.sql")
    
    if not db_path.exists():
        print(f"Error: Database {db_path} not found.")
        return
        
    con = sqlite3.connect(db_path)
    
    with open(sql_path, 'w', encoding='utf-8') as f:
        for line in con.iterdump():
            f.write('%s\n' % line)
            
    con.close()
    print(f"Successfully exported database to {sql_path}")
    print("This file contains the schema and all high-quality mock data (rooms, experts, transcripts) for submission.")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    export_db()
