# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
# Initiate db SQLAlchemy object
# ----------------------------------------------------------------------------#

db = SQLAlchemy()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    # Foreign keys
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return "<Id: {}, Show on {} >".format(self.id, self.start_time)


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    # Relationships
    shows = db.relationship("Show", backref="venue", lazy=True)
    artists = db.relationship("Artist", secondary="shows", backref="venue", lazy=True)

    def __repr__(self):
        return "<Id: {}, Venue: {}, Shows: (past: {}, upcoming: {})>".format(self.id, self.name,)


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    # Relationships
    shows = db.relationship("Show", backref="artist", lazy=True)

    def _to_dict(self):
        return {
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
        }

    def __repr__(self):
        return "<Id: {}, Artist: {}>".format(self.id, self.name,)
