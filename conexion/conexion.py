import os
import psycopg2
from psycopg2.extras import RealDictCursor


def obtener_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "farmacia_saludplus"),
        user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD")
    )


def obtener_cursor(conexion):
    return conexion.cursor(cursor_factory=RealDictCursor)
