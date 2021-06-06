"""Forms for makeup app."""

from  flask_wtf import  FlaskForm
from  wtforms import  StringField,IntegerField,SelectField,TextAreaField,BooleanField
from wtforms.validators import InputRequired,Length,NumberRange,URL,Optional

class AddProductForm(FlaskForm):
    """Form for adding products."""

    brand = StringField(
         "Brand Name",
         validators=[InputRequired()],
    ) 

    name = SelectField(
       "Product",
         choices=[("Mascara","mascara"),("Lipstick","lipstick"),("Foundation","foundation"),("NailColor","nailcolor")],
        
    )

    photo_url = StringField(
        "Photo URL",
        validators = [Optional(), URL()],

    )
    price = IntegerField(
        "Price",
        validators=[Optional(),NumberRange(min=0,max=50)],
    )

    review = TextAreaField(
        "Comments",
        validators=[Optional(),Length(min=10)],
    )

class  EditProductForm(FlaskForm):
     """Form for editing an existing product."""

     photo_url=StringField(
        "Photo URL",
        validators= [Optional(),URL()],
      )

     review = TextAreaField(
        "Comments",
        validators=[Optional(),Length(min=10)],
        )

     available = BooleanField("Available?")
