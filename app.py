from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from models import Usuario
from forms.producto_form import ProductoForm
from conexion.conexion import obtener_conexion, obtener_cursor


app = Flask(__name__)
app.config["SECRET_KEY"] = "tu_clave_secreta"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================
# CARGAR USUARIO
# =========================

@login_manager.user_loader
def cargar_usuario(user_id):

    conexion = obtener_conexion()
    cursor = obtener_cursor(conexion)

    cursor.execute(
        "SELECT * FROM usuarios WHERE id = %s",
        (user_id,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    if usuario:
        return Usuario(
            usuario["id"],
            usuario["nombre"],
            usuario["correo"],
            usuario["password"]
        )

    return None


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = obtener_cursor(conexion)

        cursor.execute(
            "SELECT * FROM usuarios WHERE correo = %s",
            (correo,)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and usuario["password"] == password:

            usuario_obj = Usuario(
                usuario["id"],
                usuario["nombre"],
                usuario["correo"],
                usuario["password"]
            )

            login_user(usuario_obj)

            return redirect(url_for("inicio"))

        return render_template(
            "login.html",
            error="Correo o contraseña incorrectos"
        )

    return render_template("login.html")


# =========================
# DATOS DE LA FARMACIA
# =========================

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
    cursor = obtener_cursor(conexion)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM productos
    """)

    cantidad_productos = cursor.fetchone()["total"]

    cursor.close()
    conexion.close()

    resumen = {
        "productos": cantidad_productos,
        "clientes": len(clientes_demo),
        "ventas_hoy": sum(
            factura["total"]
            for factura in facturas_demo
        )
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

    # =========================
    # CARGAR CATEGORÍAS
    # =========================

    conexion = obtener_conexion()
    cursor = obtener_cursor(conexion)

    cursor.execute("""
        SELECT id, nombre
        FROM categorias
        ORDER BY nombre
    """)

    categorias = cursor.fetchall()

    # =========================
    # CARGAR PROVEEDORES
    # =========================

    cursor.execute("""
        SELECT id, nombre
        FROM proveedores
        ORDER BY nombre
    """)

    proveedores = cursor.fetchall()

    cursor.close()
    conexion.close()

    # =========================
    # CREAR OPCIONES DEL FORMULARIO
    # =========================

    form.categoria.choices = [
        (categoria["id"], categoria["nombre"])
        for categoria in categorias
    ]

    form.proveedor.choices = [
        (proveedor["id"], proveedor["nombre"])
        for proveedor in proveedores
    ]

    # =========================
    # AGREGAR PRODUCTO
    # =========================

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = obtener_cursor(conexion)

        cursor.execute("""
            INSERT INTO productos
            (
                nombre,
                precio,
                stock,
                categoria_id,
                proveedor_id
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            form.nombre.data,
            form.precio.data,
            form.stock.data,
            form.categoria.data,
            form.proveedor.data
        ))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for("productos"))

    # =========================
    # CONSULTAR PRODUCTOS CON JOIN
    # =========================

    conexion = obtener_conexion()
    cursor = obtener_cursor(conexion)

    cursor.execute("""
        SELECT
            p.id,
            p.nombre,
            p.precio,
            p.stock,
            c.nombre AS categoria,
            pr.nombre AS proveedor
        FROM productos p
        LEFT JOIN categorias c
            ON p.categoria_id = c.id
        LEFT JOIN proveedores pr
            ON p.proveedor_id = pr.id
        ORDER BY p.id
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
    cursor = obtener_cursor(conexion)

    # =========================
    # BUSCAR PRODUCTO
    # =========================

    cursor.execute(
        "SELECT * FROM productos WHERE id = %s",
        (id,)
    )

    producto = cursor.fetchone()

    if producto is None:

        cursor.close()
        conexion.close()

        return redirect(url_for("productos"))

    # =========================
    # GUARDAR CAMBIOS
    # =========================

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        cursor.execute("""
            UPDATE productos
            SET
                nombre = %s,
                precio = %s,
                stock = %s
            WHERE id = %s
        """, (
            nombre,
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
    cursor = obtener_cursor(conexion)

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

    conexion = obtener_conexion()
    cursor = obtener_cursor(conexion)

    cursor.execute("""
        SELECT
            id,
            nombre,
            cedula,
            telefono,
            correo,
            activo
        FROM clientes
        ORDER BY id
    """)

    clientes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "clientes.html",
        clientes=clientes
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
            factura["total"]
            for factura in facturas_demo
        ),
        "productos_vendidos": 67,
    }

    return render_template(
        "facturacion.html",
        facturas=facturas_demo,
        resumen=resumen
    )


# =========================
# CERRAR SESIÓN
# =========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# =========================
# EJECUTAR APLICACIÓN
# =========================

if __name__ == "__main__":
    app.run(debug=True)