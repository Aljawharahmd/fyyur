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
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO 1: connect to a local postgresql database
migration = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)

    shows = db.relationship('Show', backref='venue', lazy=True)
    # TODO 2: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)

    shows = db.relationship('Show', backref='artist', lazy=True)  
    # TODO 3: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)      
    start_time = db.Column(db.DateTime, nullable=True)
    # TODO 4: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO 5: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  current_date = format_datetime(datetime.now())

  venues = Venue.query().distinct().all()
  data = []
  num_upcoming_shows = 0

  current_date = format_datetime(datetime.now())

  for venue in venues:
    shows = Show.query.filter_by(venue_id=venue.id).all()
    if shows.start_time > current_date:
      num_upcoming_shows +=1
      
    data = [{
      "city": venue.city,
      "state": venue.state,
      "venues": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
      }]
    }]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO 6: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  search_result = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all

  response={
    "count": search_result.count(),
    "data": search_result
  }
  for venue in search_result:
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      })

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO 7: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  shows = Show.query.join(Artist).filter_by(venue_id=venue_id).first()
  
  current_date = format_datetime(datetime.now())

  data ={}
  upcoming_shows = []
  past_shows = []
  
  for show in shows:
      show_data = [{
        "artist_id": 4,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(show.start_time)
        }]
      if shows.start_time < current_date:
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)

  data={ 
    "id": venue.id,
    "name": venue.name,
    #"genres": venue.genres.split(','),
    "genres": ','.split(venue.genres.getlist()),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO 8: insert form data as a new Venue record in the db, instead
  # TODO 9: modify data to be the data object returned from db insertion

  create_venue = Venue()
  create_venue.name = request.form.get('name')
  create_venue.city = request.form.get('city')
  create_venue.state = request.form.get('state')
  create_venue.address = request.form.get('address')
  create_venue.phone = request.form.get('phone')
  create_venue.genres = ''.join(request.form.getlist('genres'))
  create_venue.facebook_link = request.form.get('facebook_link')
  create_venue.image_link = request.form.get('image_link')
  create_venue.website = request.form.get('website_link')
  create_venue.seeking_talent = request.form.get('seeking_talent')
  create_venue.seeking_description = request.form.get('seeking_description')

  try:
    db.session.add(create_venue)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')

  # TODO 10: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO 11: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    venue.delete()

    db.session.commit()
    flash('Venue ' + venue_name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted.')

  finally:
    db.session.close()

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO 12: replace with real data returned from querying the database
  
  data = []
  artists = Artist.query.all()

  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO 13: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  search_result = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all

  response={
    "count": search_result.count(),
    "data": []
  }
  for artist in search_result:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      })
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO 14: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  shows = Show.query.join(Venue).filter_by(artist_id=artist_id).first()
  
  data ={}
  past_shows = []
  upcoming_shows = []

  current_date = format_datetime(datetime.now())

  for show in shows:
      show_data = [{
        "artist_id": 4,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(show.start_time)
        }]
      if shows.start_time < current_date:
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)

  data={ 
    "id": artist.id,
    "name": artist.name,
    #"genres": artist.genres.split(','),
    "genres": ','.split(artist.genres.getlist()),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # TODO 15: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO 16: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)

  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.get('genres')
  artist.genres = ''.join(request.form.getlist('genres'))
  artist.facebook_link = request.form.get('facebook_link')
  artist.image_link = request.form.get('image_link')
  artist.website = request.form.get('website')
  artist.seeking_talent = request.form.get('seeking_talent')
  artist.seeking_description = request.form.get('seeking_description')
  
  try:
    db.session.commit()
    flash('Artist ' + request.form.get('name') + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # TODO 17: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO 18: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = ''.join(request.form.getlist('genres'))
  venue.facebook_link = request.form.get('facebook_link')
  venue.image_link = request.form.get('image_link')
  venue.website = request.form.get('website_link')
  venue.seeking_talent = request.form.get('seeking_talent')
  venue.seeking_description = request.form.get('seeking_description')

  try:
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  
  # TODO 19: insert form data as a new Venue record in the db, instead
  # TODO 20: modify data to be the data object returned from db insertion

  create_artist = Artist()
  create_artist.name = request.form.get('name')
  create_artist.city = request.form.get('city')
  create_artist.state = request.form.get('state')
  create_artist.phone = request.form.get('phone')
  create_artist.genres = ''.join(request.form.getlist('genres'))
  create_artist.facebook_link = request.form.get('facebook_link')
  create_artist.image_link = request.form.get('image_link')
  create_artist.website = request.form.get('website')
  create_artist.seeking_talent = request.form.get('seeking_talent')
  create_artist.seeking_description = request.form.get('seeking_description')

  try:
    db.session.add(create_artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  
  # TODO 21: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO 22: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.join(Venue).join(Artist).filter_by().all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  # called to create new shows in the db, upon submitting new show listing form
  # TODO 23: insert form data as a new Show record in the db, instead

  create_show = Show()
  create_show.artist_id = request.form.get('artist_id')
  create_show.venue_id = request.form.get('venue_id')
  create_show.start_time = format_datetime(request.form.get('start_time'))
  
  try:
    db.session.add(create_show)
    db.session.commit()
    
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  # TODO 24: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

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
