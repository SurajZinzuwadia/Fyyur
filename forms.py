from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, URL, Length, Optional
from enums import States, Genres


class ShowForm(FlaskForm):
    artist_id = StringField("artist_id", [DataRequired()])
    venue_id = StringField("venue_id", [DataRequired()])
    start_time = DateTimeField("start_time", [DataRequired()], default=datetime.today())


class VenueForm(FlaskForm):
    name = StringField("name", [DataRequired(), Length(1, 120)])
    city = StringField("city", [DataRequired(), Length(1, 120)])
    state = SelectField("state", [DataRequired()], choices=States.choices(),)
    address = StringField("address", [DataRequired(), Length(1, 120)])
    phone = StringField("phone", [Length(10, 15), Optional()])
    image_link = StringField("image_link", [Length(1, 500), URL(), Optional()])
    genres = SelectMultipleField(
        "genres",
        [DataRequired()],
        choices=Genres.choices(),
    )
    facebook_link = StringField("facebook_link", [URL(), Optional()])


class ArtistForm(FlaskForm):
    name = StringField("name", [DataRequired(), Length(1, 120)])
    city = StringField("city", [DataRequired(), Length(1, 120)])
    state = SelectField("state", [DataRequired()], choices=States.choices(),)
    phone = StringField(
        "phone",
        [Length(10, 15), Optional()],
    )
    image_link = StringField("image_link", [Length(1, 500), URL(), Optional()])
    genres = SelectMultipleField("genres", [DataRequired()], choices=Genres.choices(),)
    facebook_link = StringField(
        "facebook_link",
        [Length(1, 120), URL(), Optional()],
    )
