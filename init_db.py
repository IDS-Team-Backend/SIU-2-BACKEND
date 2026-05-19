import db

def init_database():
    try:
        # 1. Conectamos al servidor (sin DB) para crear la base de datos
        conn = db.get_server_connection()
        cursor = conn.cursor()
        
        with open("schema.sql", "r") as f:
            sql_commands = f.read().split(';')
        
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("Base de datos y tablas creadas exitosamente.")

    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    init_database()