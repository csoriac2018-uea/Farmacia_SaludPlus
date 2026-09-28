from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ProductoForm(FlaskForm):

    nombre = StringField(
        "Nombre del producto",
        validators=[DataRequired()]
    )

    categoria = SelectField(
        "Categoría",
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    proveedor = SelectField(
        "Proveedor",
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    precio = FloatField(
        "Precio",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    submit = SubmitField("Guardar producto")