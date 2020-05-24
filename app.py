#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm , Form
from forms import VenueForm, ArtistForm, ShowForm
from flask_migrate import Migrate
import sys
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from models import db, Artist, Venue, Show
from datetime import datetime,date
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# Add CSRFProtect Protection
csrf = CSRFProtect(app)


# ----------------------------------------------------------------------------#
# Inject data to the Database
# ----------------------------------------------------------------------------#
# Flask CLI command to inject fake data "flask inject-data"
@app.cli.command('inject-data')
def _inject_init_data():
      print("Start injecting data (artists, venues, shows) from 'data.py'")
      from data import artists, venues, shows
      import os

      os.system("color")

      try:
          for venue in venues:
              db.session.add(venue)
          print("\033[94mInjected {} venues\033[0m".format(len(venues)))
          for artist in artists:
              db.session.add(artist)
          print("\033[94mInjected {} artists\033[0m".format(len(artists)))
          for show in shows:
              db.session.add(show)
          print("\033[94mInjected {} shows\033[0m".format(len(shows)))
          db.session.commit()
          print("\033[92mData injection success.\033[0m")
      except Exception:
          print("\033[91m!Error during data injection.\033[0m")
          db.session.rollback()
          print("\033[93mData injection rolled back.\033[0m")
          print(sys.exc_info())
      finally:
          db.session.close()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format,locale='en_US')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # num_shows should be aggregated based on number of upcoming shows per venue.

    def _agregate_state_city(res):
        """ Take a response object, returns: [{"state":"","city":""}] """

        state_city = sorted(set((("state", venue.state), ("city", venue.city)) for venue in res))
        return [dict(t) for t in state_city]

    try:
        response = Venue.query.order_by(Venue.state, Venue.city).all()
        state_cities = _agregate_state_city(response)
        data = [
            {
                "city": st_city["city"],
                "state": st_city["state"],
                "venues": [
                    {
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": len(
                            list(filter(lambda x: x.start_time >= datetime.now(), venue.shows))
                        ),
                    }
                    for venue in response
                    if venue.state == st_city["state"] and venue.city == st_city["city"]
                ],
            }
            for st_city in state_cities
        ]
    except Exception:
        print(sys.exc_info())
    return render_template("pages/venues.html", areas=data)

@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "").strip()
    venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
    response = {
        "count": len(venues),
        "data": sorted(
            [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(
                        list(filter(lambda x: x.start_time >= datetime.now(), venue.shows))
                    ),
                }
                for venue in venues
            ],
            key=lambda x: x["name"],
        ),
    }
    return render_template("pages/search_venues.html", results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    past_shows, upcoming_shows = [], []
    for show in venue.shows:
        past_shows.append(show) if show.start_time < datetime.now() else upcoming_shows.append(show)
    venue.past_shows = [
        {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time),
        }
        for show in past_shows
    ]
    venue.upcoming_shows = [
        {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time),
        }
        for show in upcoming_shows
    ]
    venue.past_shows_count = len(past_shows)
    venue.upcoming_shows_count = len(upcoming_shows)
    venue.genres = venue.genres.split(",") if venue.genres else []
    return render_template("pages/show_venue.html", venue=venue.__dict__)
 
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)



def _hydrate_venue(form):
    return Venue(
        name=form.get("name"),
        city=form.get("city"),
        state=form.get("state"),
        address=form.get("address"),
        phone=form.get("phone"),
        genres=",".join(form.getlist("genres")),
        image_link=form.get("image_link"),
        facebook_link=form.get("facebook_link"),
        website=form.get("website"),
        seeking_talent=form.get("seeking_talent"),
        seeking_description=form.get("seeking_description"),
    )



@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if not form.validate():
        flash(form.errors)
        return redirect(url_for("create_venue_form"))
  error = False
  try:
    data = request.form
    venue = _hydrate_venue(data)
    db.session.add(venue)
    db.session.commit()
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
          flash("An error occured. Venue "+ data["name"] + "could not be listed.")
    else:
          flash("Venue " + data["name"] + "was successfully listed!")
  return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            db.session.delete(venue)
            db.session.commit()
        else:
            error = True
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash("An error occurred. the venue could not be removed.")
        else:
            flash("Venue was successfully removed!")
    return jsonify({"success": not error})





#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
      try:
          artists = Artist.query.order_by(Artist.name).all()
          artists = [artist.__dict__ for artist in artists]
      except Exception:
          print(sys.exc_info())
      return render_template("pages/artists.html", artists = artists)  


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "").strip()
    artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
    response = {
        "count": len(artists),
        "data": sorted(
            [
                {
                    "id": artist.id,
                    "name": artist.name,
                    "num_upcoming_shows": len(
                        list(filter(lambda x: x.start_time >= datetime.now(), artist.shows))
                    ),
                }
                for artist in artists
            ],
            key=lambda x: x["name"],
        ),
    }
    return render_template("pages/search_artists.html", results=response, search_term=search_term,)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    past_shows, upcoming_shows = [], []
    for show in artist.shows:
        past_shows.append(show) if show.start_time < datetime.now() else upcoming_shows.append(show)
    artist.past_shows = [
        {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time),
        }
        for show in past_shows
    ]
    artist.upcoming_shows = [
        {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time),
        }
        for show in upcoming_shows
    ]
    artist.past_shows_count = len(past_shows)
    artist.upcoming_shows_count = len(upcoming_shows)
    artist.genres = artist.genres.split(",")
    return render_template('pages/show_artist.html', artist=artist.__dict__)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
      artist = Artist.query.get_or_404(artist_id)
      artist.genres = artist.genres.split(",")
      form = ArtistForm(obj=artist)
      return render_template("forms/edit_artist.html", form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        data = request.form
        artist = Artist.query.get(artist_id)
        artist.name = data.get("name")
        artist.city = data.get("city")
        artist.state = data.get("state")
        artist.phone = data.get("phone")
        artist.genres = ",".join(data.getlist("genres"))
        artist.image_link = data.get("image_link")
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash("An error occurred. Artist " + data["name"] + " could not be updated.")
        else:
            flash("Artist " + data["name"] + " was successfully updated")
    return redirect(url_for("show_artist", artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
      venue = Venue.query.get_or_404(venue_id)
      venue.genres = venue.genres.split(",")
      form = VenueForm(obj=venue)
      return render_template("forms/edit_venue.html", form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        data = request.form
        venue = Venue.query.get(venue_id)
        venue.name = data.get("name")
        venue.city = data.get("city")
        venue.state = data.get("state")
        venue.address = data.get("address")
        venue.phone = data.get("phone")
        venue.genres = ",".join(data.getlist("genres"))
        venue.image_link = data.get("image_link")
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash("An error occurred. Venue " + data["name"] + " could not be updated.")
        else:
            flash("Venue " + data["name"] + " was successfully updated!")
    return redirect(url_for("show_venue", venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


def _hydrate_artist(form):
    return Artist(
        name=form.get("name"),
        city=form.get("city"),
        state=form.get("state"),
        phone=form.get("phone"),
        genres=",".join(form.getlist("genres")),
        image_link=form.get("image_link"),
        facebook_link=form.get("facebook_link"),
        website=form.get("website"),
        seeking_venue=form.get("seeking_venue"),
        seeking_description=form.get("seeking_description"),
    )


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if not form.validate():
        flash(form.errors)
        return redirect(url_for("create_artist_form"))
    error = False
    try:
        data = request.form
        artist = _hydrate_artist(data)
        db.session.add(artist)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash("An error occurred. Artist " + data["name"] + " could not be listed.")
        else:
            flash("Artist " + data["name"] + " was successfully listed!")
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      data = Show.query.all()
      shows = [
        {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "start_time": str(show.start_time),
        }
        for show in data
      ]
      return render_template("pages/shows.html", shows=shows)



@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


def _hydrte_show(form):
    return Show(
        venue_id=form.get("venue_id"),
        artist_id=form.get("artist_id"),
        start_time=form.get("start_time"),
    )


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
      error = False
      try:
        data = request.form
        show = _hydrte_show(data)
        db.session.add(show)
        db.session.commit()
      except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()
        if error:
              flash("An error occured. Show could not be listed")
        else:
              flash("Show was successfully listed!")
      return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
