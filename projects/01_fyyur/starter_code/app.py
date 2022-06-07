#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from pytz import timezone
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# import migrate from flask migrate
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.sql import func  # to set default datetime later

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    talent_search = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), nullable=False)

    # Shows relationship column
    show = db.relationship('Show', backref='show_venue',
                           lazy=True, cascade='all, delete')

    def __repr__(self) -> str:
        return f'<Venue {self.id}, {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120), nullable=True)
    venue_search = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), nullable=True)

    # Shows relationship Column
    show = db.relationship('Show', backref='show_artist',
                           lazy=True, cascade='all, delete')

    def __repr__(self) -> str:
        return f'<Artist {self.id}, {self.name}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_date = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self) -> str:
        return f'<Show {self.id}, artist: {self.venue_id}, location: {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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


# venue list page
@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    venue_qs = Venue.query
    loc_set = set()

    for venue in venue_qs:
        loc_set.add((venue.city, venue.state))

    for loc in loc_set:
        data_item = {
            'city': loc[0],
            'state': loc[1],
            'venues': [],
        }
        loc_qs = venue_qs.filter_by(city=loc[0]).filter_by(state=loc[1]).all()
        print(loc_qs)
        for venue_loc in loc_qs:

            data_item['venues'].append({
                'id': venue_loc.id,
                'name': venue_loc.name,
                'num_upcoming_shows': Show.query
                .filter(Show.venue_id == venue_loc.id)
                .filter(Show.event_date > datetime.now())
                .count()
            })
        data.append(data_item)

    return render_template('pages/venues.html', areas=data)


# venue search result page
@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_keyword = request.form.get('search_term', None)
    qs = Venue.query.filter(Venue.name.ilike(f'%{search_keyword}%'))

    data = []
    for result in qs.all():
        data.append({
            'id': result.id,
            'name': result.name,
            'num_upcoming_shows': Show.query
            .filter(Show.venue_id == result.id)
            .filter(Show.event_date > datetime.now())
            .count()
        })

    response = {
        "count": qs.count(),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# venue details page
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {}

    venue_qs = Venue.query.filter_by(id=venue_id)
    venue = venue_qs.first()

    if not venue:  # if page does not exist rediirect to venue list
        return redirect(url_for('venues'))

    show_artist_qs = db.session.query(Show, Artist).join(Artist).\
        filter(Show.venue_id == venue.id)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(", ") if venue.genres else '',
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "seeking_talent": venue.talent_search,
        "seeking_description": venue.seeking_description,
        # about shows
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": show_artist_qs.filter(Show.event_date < datetime.now()).count(),
        "upcoming_shows_count": show_artist_qs.filter(Show.event_date > datetime.now()).count(),
    }

    for show, artist in show_artist_qs.filter(Show.event_date < datetime.now()).all():
        data['past_shows'].append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": f'{show.event_date}'
        })

    for show, artist in show_artist_qs.filter(Show.event_date > datetime.now()).all():
        data['upcoming_shows'].append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": f'{show.event_date}'
        })

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    try:
        data = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=", ".join(form.genres.data),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            talent_search=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(data)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        print(form.errors)
        db.session.rollback()

        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form.get('name') + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')


# NB: modified url route a bit
@app.route('/venues/<venue_id>/del', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        loc = Venue.query.get(venue_id)
        db.session.delete(loc)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    # implemented on venues details page /venues/<venue_id>;
    if error:
        abort(400)
        return jsonify({'successful?': False})
    else:
        return jsonify({'successful?': True})


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_keyword = request.form.get('search_term', None)

    qs = Artist.query.filter(Artist.name.ilike(f'%{search_keyword}%'))

    data = []
    for artist in qs.all():

        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': Show.query
            .filter(Show.artist_id == artist.id)
            .filter(Show.event_date > datetime.now())
            .count()
        })
        print(data)

    response = {
        "count": qs.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = {}

    artist_qs = Artist.query.filter_by(id=artist_id)
    artist = artist_qs.first()

    if not artist:  # if page does not exist rediirect to artist list
        return redirect(url_for('artists'))

    show_venue_qs = db.session.query(Show, Venue).join(Venue).\
        filter(Show.artist_id == artist.id)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(", ") if artist.genres else '',
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.venue_search,
        "seeking_description": artist.description,
        # about shows
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": show_venue_qs.filter(Show.event_date < datetime.now()).count(),
        "upcoming_shows_count": show_venue_qs.filter(Show.event_date > datetime.now()).count(),
    }

    for show, venue in show_venue_qs.filter(Show.event_date < datetime.now()).all():
        data['past_shows'].append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": f'{show.event_date}'
        })

    for show, venue in show_venue_qs.filter(Show.event_date > datetime.now()).all():
        data['upcoming_shows'].append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": f'{show.event_date}'
        })

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)  # auto pre populate field

    # TODO: populate form with fields from artist with ID <artist_id>

    # manually prepopulating field sue to difference in field name and form name
    form.genres.data = artist.genres.split(", ") if artist.genres else ''
    form.seeking_venue.data = artist.venue_search
    form.seeking_description.data = artist.description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.genres = ", ".join(form.genres.data)
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.venue_search = form.seeking_venue.data
        artist.description = form.seeking_description.data
        artist.image_link = form.image_link.data

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
