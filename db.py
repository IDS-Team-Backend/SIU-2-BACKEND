import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", 3306)

def get_connection(database_name=DB_NAME):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database_name,
        port=DB_PORT
    )

def get_server_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def execute_query(query, params=None, modifica_db=False, un_solo_valor=False):
    """
        Ejecuta una query SQL.

        Args:
            query (str): Sentencia SQL a ejecutar. Debe usar '(%s)' en las variables por seguridad

            params (tuple/list, optional): Valores para reemplazar los marcadores en la query.
                Por defecto es None.

            modifica_db (bool): Debe ser True para sentencias INSERT, UPDATE o DELETE.
                devuelve el ID del registro afectado.
                Si es False (default), se asume una consulta SELECT.

            un_solo_valor (bool): Si es True, devuelve solo el primer resultado (dict).
              Útil para búsquedas por ID o COUNT(*). 
                Solo aplica si modifica_db es False.

        Returns:
            list/dict/int/None: 
                - Si modifica_db=False: Una lista de diccionarios (un_solo_valor=False) o un solo 
                diccionario (un_solo_valor=True).
                - Si modifica_db=True: El ID de la última fila insertada (int).
                - None: Si no hay resultados.

        Raises:
            Exception: Si ocurre un error en la ejecución, realiza un rollback de la 
                conexión y relanza la excepción con detalles de la query y parámetros.
        """
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(query, params)

        if not modifica_db: 
            if un_solo_valor:
                return cur.fetchone()
            return cur.fetchall()
        
        # si la query es un insert o update hay que hacer commit() para que los cambios se guarden en la DB 
        conn.commit()
        if query.strip().upper().startswith("INSERT"):
            return cur.lastrowid
        else:
            return cur.rowcount
    except Exception as e:
        if conn: 
            conn.rollback() # si hay un error en un post o put hay que revertir los cambios hecho a la DB para evitar datos corruptos 
        e.message = f"Error al ejecutar la query: {str(e)}. Query: {query}, Params: {params}"
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()