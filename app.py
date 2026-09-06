from flask import Flask, render_template, request, redirect, url_for
from forms.producto_form import ProductoForm
import sqlite3
import os
app = Flask(__name__)
app.config["SECRET_KEY"] = "tu_clave_secreta"

farmacia = {
    "nombre": "Farmacia SaludPlus",
    "eslogan": "Tu salud, nuestra prioridad",
    "ciudad": "Puyo, Ecuador",
}

productos_demo = [
    {"nombre": "Paracetamol", "dosis": "500 mg", "categoria": "Analgésico", "presentacion": "Caja x 20 tabletas", "precio": 2.50, "stock": 50},
    {"nombre": "Ibuprofeno", "dosis": "400 mg", "categoria": "Antiinflamatorio", "presentacion": "Caja x 20 tabletas", "precio": 3.75, "stock": 35},
    {"nombre": "Vitamina C", "dosis": "500 mg", "categoria": "Vitaminas", "presentacion": "Frasco x 30 tabletas", "precio": 5.00, "stock": 25},
    {"nombre": "Alcohol", "dosis": "70%", "categoria": "Higiene", "presentacion": "Frasco 500 ml", "precio": 2.25, "stock": 40},
    {"nombre": "Jarabe para la tos", "dosis": "120 ml", "categoria": "Respiratorio", "presentacion": "Frasco 120 ml", "precio": 4.50, "stock": 8},
    {"nombre": "Suero fisiológico", "dosis": "0.9%", "categoria": "Primeros auxilios", "presentacion": "Frasco 100 ml", "precio": 1.80, "stock": 0},
]
# Configuración de la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "farmacia.db")


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_base_datos():
    conexion = obtener_conexion()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dosis TEXT NOT NULL,
            categoria TEXT NOT NULL,
            presentacion TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cantidad = conexion.execute(
        "SELECT COUNT(*) FROM productos"
    ).fetchone()[0]

    if cantidad == 0:
        for producto in productos_demo:
            conexion.execute("""
                INSERT INTO productos
                (nombre, dosis, categoria, presentacion, precio, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                producto["nombre"],
                producto["dosis"],
                producto["categoria"],
                producto["presentacion"],
                producto["precio"],
                producto["stock"]
            ))

    conexion.commit()
    conexion.close()


inicializar_base_datos()

clientes_demo = [
    {"nombre": "María González", "cedula": "0912345678", "telefono": "0991234567", "correo": "maria@email.com", "activo": True},
    {"nombre": "Juan Pérez", "cedula": "0923456789", "telefono": "0982345678", "correo": "juan@email.com", "activo": True},
    {"nombre": "Ana Rodríguez", "cedula": "0934567890", "telefono": "0973456789", "correo": "ana@email.com", "activo": True},
    {"nombre": "Carlos Mendoza", "cedula": "0945678901", "telefono": "0964567890", "correo": "carlos@email.com", "activo": False},
]

proveedores_demo = [
    {"nombre": "Distribuidora Farma Ecuador", "ruc": "0991234567001", "telefono": "0991112233", "correo": "ventas@farmaecuador.com", "producto": "Medicamentos", "activo": True},
    {"nombre": "Laboratorios Salud S.A.", "ruc": "0992345678001", "telefono": "0982223344", "correo": "contacto@salud.com", "producto": "Vitaminas", "activo": True},
    {"nombre": "Higiene y Cuidado Cía. Ltda.", "ruc": "0993456789001", "telefono": "0973334455", "correo": "ventas@higieneycuidado.com", "producto": "Higiene personal", "activo": True},
    {"nombre": "Farmacéutica Nacional", "ruc": "0994567890001", "telefono": "0964445566", "correo": "info@farmaceuticanacional.com", "producto": "Productos farmacéuticos", "activo": False},
]

facturas_demo = [
    {"numero": "001-001-000001", "cliente": "María González", "fecha": "16/08/2026", "subtotal": 25.00, "iva": 3.00, "total": 28.00, "pagada": True},
    {"numero": "001-001-000002", "cliente": "Juan Pérez", "fecha": "16/08/2026", "subtotal": 18.50, "iva": 2.22, "total": 20.72, "pagada": True},
    {"numero": "001-001-000003", "cliente": "Ana Rodríguez", "fecha": "15/08/2026", "subtotal": 42.00, "iva": 5.04, "total": 47.04, "pagada": True},
    {"numero": "001-001-000004", "cliente": "Carlos Mendoza", "fecha": "15/08/2026", "subtotal": 31.25, "iva": 3.75, "total": 35.00, "pagada": False},
]

# Página principal
@app.route("/")
def inicio():
    conexion = obtener_conexion()

    cantidad_productos = conexion.execute(
        "SELECT COUNT(*) FROM productos"
    ).fetchone()[0]

    conexion.close()

    resumen = {
        "productos": cantidad_productos,
        "clientes": len(clientes_demo),
        "ventas_hoy": sum(factura["total"] for factura in facturas_demo),
    }

    return render_template("index.html", farmacia=farmacia, resumen=resumen)


# Módulo Productos
@app.route("/productos", methods=["GET", "POST"])
def productos():
    form = ProductoForm()

    if form.validate_on_submit():
        conexion = obtener_conexion()

        conexion.execute("""
            INSERT INTO productos
            (nombre, dosis, categoria, presentacion, precio, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            form.nombre.data,
            form.dosis.data,
            form.categoria.data,
            form.presentacion.data,
            form.precio.data,
            form.stock.data
        ))

        conexion.commit()
        conexion.close()

        return redirect(url_for("productos"))

    conexion = obtener_conexion()

    productos = conexion.execute("""
        SELECT id, nombre, dosis, categoria, presentacion, precio, stock
        FROM productos
        ORDER BY id
    """).fetchall()

    conexion.close()

    return render_template(
        "productos.html",
        productos=productos,
        form=form
    )

# Módulo Clientes
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", clientes=clientes_demo)


# Módulo Proveedores
@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", proveedores=proveedores_demo)


# Módulo Facturación
@app.route("/facturacion")
def facturacion():
    resumen = {
        "cantidad": len(facturas_demo),
        "ventas": sum(factura["total"] for factura in facturas_demo),
        "productos_vendidos": 67,
    }
    return render_template("facturacion.html", facturas=facturas_demo, resumen=resumen)








if __name__ == "__main__":
    app.run(debug=True)
