"""Forms for makeup app."""

from  flask_wtf import  FlaskForm
from  wtforms import  StringField,IntegerField,SelectField,TextAreaField,BooleanField,PasswordField
from wtforms.validators import InputRequired,Length,NumberRange,URL,Optional,DataRequired, Email



class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    """Form for editing user profile."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('Bio')
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
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
