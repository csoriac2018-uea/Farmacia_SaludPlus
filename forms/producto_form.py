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
        choices=[
            ("Medicamentos", "Medicamentos"),
            ("Vitaminas", "Vitaminas"),
            ("Higiene", "Higiene"),
            ("Primeros auxilios", "Primeros auxilios")
        ],
        validators=[DataRequired()]
    )

    dosis = StringField(
        "Dosis o presentación",
        validators=[DataRequired()]
    )

    presentacion = StringField(
        "Presentación",
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