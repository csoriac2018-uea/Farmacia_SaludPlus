from flask import Flask, render_template, request, redirect, url_for
from forms.producto_form import ProductoForm
from conexion.conexion import obtener_conexion

app = Flask(__name__)
app.config["SECRET_KEY"] = "tu_clave_secreta"


farmacia = {
    "nombre": "Farmacia SaludPlus",
    "eslogan": "Tu salud, nuestra prioridad",
    "ciudad": "Puyo, Ecuador",
}


# =========================
# DATOS DEMOSTRATIVOS
# =========================

clientes_demo = [
    {
        "nombre": "María González",
        "cedula": "0912345678",
        "telefono": "0991234567",
        "correo": "maria@email.com",
        "activo": True
    },
    {
        "nombre": "Juan Pérez",
        "cedula": "0923456789",
        "telefono": "0982345678",
        "correo": "juan@email.com",
        "activo": True
    },
    {
        "nombre": "Ana Rodríguez",
        "cedula": "0934567890",
        "telefono": "0973456789",
        "correo": "ana@email.com",
        "activo": True
    },
    {
        "nombre": "Carlos Mendoza",
        "cedula": "0945678901",
        "telefono": "0964567890",
        "correo": "carlos@email.com",
        "activo": False
    },
]


proveedores_demo = [
    {
        "nombre": "Distribuidora Farma Ecuador",
        "ruc": "0991234567001",
        "telefono": "0991112233",
        "correo": "ventas@farmaecuador.com",
        "producto": "Medicamentos",
        "activo": True
    },
    {
        "nombre": "Laboratorios Salud S.A.",
        "ruc": "0992345678001",
        "telefono": "0982223344",
        "correo": "contacto@salud.com",
        "producto": "Vitaminas",
        "activo": True
    },
    {
        "nombre": "Higiene y Cuidado Cía. Ltda.",
        "ruc": "0993456789001",
        "telefono": "0973334455",
        "correo": "ventas@higieneycuidado.com",
        "producto": "Higiene personal",
        "activo": True
    },
    {
        "nombre": "Farmacéutica Nacional",
        "ruc": "0994567890001",
        "telefono": "0964445566",
        "correo": "info@farmaceuticanacional.com",
        "producto": "Productos farmacéuticos",
        "activo": False
    },
]


facturas_demo = [
    {
        "numero": "001-001-000001",
        "cliente": "María González",
        "fecha": "16/08/2026",
        "subtotal": 25.00,
        "iva": 3.00,
        "total": 28.00,
        "pagada": True
    },
    {
        "numero": "001-001-000002",
        "cliente": "Juan Pérez",
        "fecha": "16/08/2026",
        "subtotal": 18.50,
        "iva": 2.22,
        "total": 20.72,
        "pagada": True
    },
    {
        "numero": "001-001-000003",
        "cliente": "Ana Rodríguez",
        "fecha": "15/08/2026",
        "subtotal": 42.00,
        "iva": 5.04,
        "total": 47.04,
        "pagada": True
    },
    {
        "numero": "001-001-000004",
        "cliente": "Carlos Mendoza",
        "fecha": "15/08/2026",
        "subtotal": 31.25,
        "iva": 3.75,
        "total": 35.00,
        "pagada": False
    },
]


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def inicio():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    cantidad_productos = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    resumen = {
        "productos": cantidad_productos,
        "clientes": len(clientes_demo),
        "ventas_hoy": sum(
            factura["total"] for factura in facturas_demo
        ),
    }

    return render_template(
        "index.html",
        farmacia=farmacia,
        resumen=resumen
    )


# =========================
# PRODUCTOS - LISTAR Y AGREGAR
# =========================

@app.route("/productos", methods=["GET", "POST"])
def productos():

    form = ProductoForm()

    # AGREGAR PRODUCTO
    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO productos
            (nombre, dosis, categoria, presentacion, precio, stock)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            form.nombre.data,
            form.dosis.data,
            form.categoria.data,
            form.presentacion.data,
            form.precio.data,
            form.stock.data
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for("productos"))

    # CONSULTAR PRODUCTOS
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nombre, dosis, categoria,
               presentacion, precio, stock
        FROM productos
        ORDER BY id
    """)

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "productos.html",
        productos=productos,
        form=form
    )


# =========================
# PRODUCTOS - MODIFICAR
# =========================

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Buscar producto
    cursor.execute(
        "SELECT * FROM productos WHERE id = %s",
        (id,)
    )

    producto = cursor.fetchone()

    if producto is None:
        cursor.close()
        conexion.close()
        return redirect(url_for("productos"))

    # Guardar cambios
    if request.method == "POST":

        nombre = request.form["nombre"]
        dosis = request.form["dosis"]
        categoria = request.form["categoria"]
        presentacion = request.form["presentacion"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        cursor.execute("""
            UPDATE productos
            SET nombre = %s,
                dosis = %s,
                categoria = %s,
                presentacion = %s,
                precio = %s,
                stock = %s
            WHERE id = %s
        """, (
            nombre,
            dosis,
            categoria,
            presentacion,
            precio,
            stock,
            id
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for("productos"))

    cursor.close()
    conexion.close()

    return render_template(
        "editar_producto.html",
        producto=producto
    )


# =========================
# PRODUCTOS - ELIMINAR
# =========================

@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id = %s",
        (id,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for("productos"))


# =========================
# CLIENTES
# =========================

@app.route("/clientes")
def clientes():

    return render_template(
        "clientes.html",
        clientes=clientes_demo
    )


# =========================
# PROVEEDORES
# =========================

@app.route("/proveedores")
def proveedores():

    return render_template(
        "proveedores.html",
        proveedores=proveedores_demo
    )


# =========================
# FACTURACIÓN
# =========================

@app.route("/facturacion")
def facturacion():

    resumen = {
        "cantidad": len(facturas_demo),
        "ventas": sum(
            factura["total"] for factura in facturas_demo
        ),
        "productos_vendidos": 67,
    }

    return render_template(
        "facturacion.html",
        facturas=facturas_demo,
        resumen=resumen
    )


# =========================
# EJECUTAR APLICACIÓN
# =========================

if __name__ == "__main__":
    app.run(debug=True)