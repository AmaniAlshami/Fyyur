#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json 
from threading import Thread
import dateutil.parser
import babel
from flask import (Flask, 
render_template,
 request, Response, 
 flash, redirect,
  url_for,jsonify)
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from flask_moment import Moment
from forms import *
from datetime import datetime
import sys
from  models import db
from flask_migrate import Migrate
from models import  Venue , Venue_genre , Artist ,Artist_genre ,Shows 





#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
db.app = app 
migrate = Migrate(app, db)

# [DONE] TODO: connect to a local postgresql database 


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
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
#  ---------------------------------------------------------------

@app.route('/venues')
def venues():
  #[DONE] TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html', areas= Venue.query.distinct(Venue.city,Venue.state),
   venues = Venue.query.all() )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # [DONE] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  results = Venue.query.filter(Venue.name.ilike(search)).all()
  count = Venue.query.filter(Venue.name.ilike(search)).count()

  return render_template('pages/search_venues.html',search_term=search_term,results=results,count=count)



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # [DONE] TODO: replace with real venue data from the venues table, using venue_id

  data = Venue.query.filter_by(id=venue_id).all()

  # To Show genres 
  gen_data = []
  get_genres = Venue_genre.query.with_entities(Venue_genre.genres).join(Venue,Venue_genre.venue_id==Venue.id).filter(Venue_genre.venue_id==venue_id).all()
  for g in range(len(get_genres)):
    gen_data.append(get_genres[g].genres)

 # To prsesnt upcoming and past shows
  artist_info = Artist.query.with_entities(Artist.id,Artist.name,Artist.image_link,Shows.start_time).join(Shows,Artist.id==Shows.artist_id).filter(Shows.venue_id==venue_id).all()
  now = datetime.now()
  upcoming_shows_count = 0
  upcoming_shows = []
  past_shows_count = 0
  past_shows = []
  for i in range(len(artist_info)):
    if now <= artist_info[i][3]:
        upcoming_shows_count+=1
        new = {
          "artist_id": artist_info[i][0] ,
          "artist_name": artist_info[i][1],
          "artist_image_link":artist_info[i][2] ,
          "start_time": artist_info[i][3]} 
        upcoming_shows.append(new)
    elif now > artist_info[i][3]:
          past_shows_count+=1
          new = {
          "artist_id": artist_info[i][0] ,
          "artist_name": artist_info[i][1],
          "artist_image_link":artist_info[i][2] ,
          "start_time": artist_info[i][3]}  
          past_shows.append(new)



  return render_template('pages/show_venue.html', venue=data[0],genres=gen_data,upcoming_shows_count=upcoming_shows_count,
  past_shows_count=past_shows_count,upcoming_shows=upcoming_shows,past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # [Done] TODO: insert form data as a new Venue record in the db, instead
  # [Done] TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
 
  try: 
      name = form.name.data
      city = form.city.data
      state =form.state.data
      address = form.address.data
      phone =form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      website_link =form.website_link.data
      seeking_description =form.seeking_description.data
      genres = form.genres.data
      seeking_talent = True if form.seeking_talent.data else False


    
      new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,
      image_link=image_link,facebook_link=facebook_link,website_link=website_link,
      description=seeking_description,looking_for_talent=seeking_talent)
      db.session.add(new_venue)
      db.session.commit()


      for gen in genres:
          new_genre = Venue_genre(venue_id=new_venue.id,genres=gen)
          db.session.add(new_genre)
          db.session.commit()

      error = False
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error : 
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    return render_template('pages/home.html')   
  elif not error:   
    flash('Venue ' + form.name.data + ' was successfully listed!') 
    return render_template('pages/home.html', form=form)   



  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # [DONE] TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      Venue_genre.query.filter_by(venue_id=venue_id).delete()
      db.session.commit()
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      error = False
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
    db.session.close()
  if error : 
    flash('An error occurred. Venue could not be deleted.')
    return redirect(url_for('show_venue', venue_id=venue_id))
  elif not error:    
    flash('Venue was successfully deleted!') 
    return jsonify({ 'success': True })      

  ## This method deletes the record but the redirect method dosen't work correctly

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # [DONE] TODO: replace with real data returned from querying the database 
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # [DONE] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  results = Artist.query.filter(Artist.name.ilike(search)).all()
  count = Artist.query.filter(Artist.name.ilike(search)).count()

  return render_template('pages/search_artists.html',search_term=search_term,results=results,count=count)

  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  # shows the artist page with the given artist_id
  # [DONE] TODO: replace with real artist data from the artist table, using artist_id

  data = Artist.query.filter_by(id=artist_id).all()

  # To show geners     
  gen_data = []
  get_genres = Artist_genre.query.with_entities(Artist_genre.genres).join(Artist,Artist_genre.artist_id==Artist.id).filter(Artist_genre.artist_id==artist_id).all()
  for g in range(len(get_genres)):
    gen_data.append(get_genres[g].genres)
  
  # filter and present upcoming and past shows
  Venues_info = Venue.query.with_entities(Venue.id,Venue.name,Venue.image_link,Shows.start_time).join(Shows,Venue.id==Shows.venue_id).filter(Shows.artist_id==artist_id).all()
  now = datetime.now()
  upcoming_shows_count = 0
  upcoming_shows = []
  past_shows_count = 0
  past_shows = []
  for i in range(len(Venues_info)):
    if now <= Venues_info[i][3]:
        upcoming_shows_count+=1
        new = {
          "venue_id": Venues_info[i][0] ,
          "venue_name": Venues_info[i][1],
          "venue_image_link":Venues_info[i][2] ,
          "start_time": Venues_info[i][3]} 
        upcoming_shows.append(new)
    elif now > Venues_info[i][3]:
         past_shows_count+=1
         new = {
          "venue_id": Venues_info[i][0] ,
          "venue_name": Venues_info[i][1],
          "venue_image_link":Venues_info[i][2] ,
          "start_time": Venues_info[i][3]} 
         past_shows.append(new)

  return render_template('pages/show_artist.html',artist=data[0],genres=gen_data,upcoming_shows_count=upcoming_shows_count,
  past_shows_count=past_shows_count,upcoming_shows=upcoming_shows,past_shows=past_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_info = Artist.query.filter_by(id=artist_id).all()[0]
  gen_data = []
  get_genres = Artist_genre.query.with_entities(Artist_genre.genres).join(Artist,Artist_genre.artist_id==Artist.id).filter(Artist_genre.artist_id==artist_id).all()
  for g in range(len(get_genres)):
    gen_data.append(get_genres[g].genres)

  state=form.state.default = artist_info.state
  seeking_venue=form.seeking_venue.default = artist_info.looking_for_venues
  genres=form.genres.default = gen_data
  form.process() 

  artist={
    "id": artist_info.id,
    "name": artist_info.name,
    "genres": genres,
    "city": artist_info.city,
    "state": state,
    "phone": artist_info.phone,
    "website": artist_info.website_link,
    "facebook_link": artist_info.facebook_link,
    "seeking_venue": seeking_venue,
    "seeking_description": artist_info.description,
    "image_link": artist_info.image_link
  }
  
  #[DONE] TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # [DONE]TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id=artist_id).all()[0]

  try:

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state =request.form['state']
    artist.phone =request.form['phone']
    artist.image_link =request.form['image_link']
    artist.facebook_link =request.form['facebook_link']
    artist.website_link =request.form['website_link']
    artist.description =request.form['seeking_description']
    seeking = True if request.form.get('seeking_venue') else False
    print(seeking)
    artist.looking_for_venues = seeking


   # is not the best way but it works good .
    Artist_genre.query.filter_by(artist_id=artist_id).delete()
    db.session.commit()
    genres = request.form.getlist('genres')
    for gen in genres:
          new_genre = Artist_genre(artist_id=artist_id,genres=gen)
          db.session.add(new_genre)
          db.session.commit()
      
    db.session.commit()

  except:
    db.session.rollback()
    print("REE")
  finally:
    db.session.close() 

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_info = Venue.query.filter_by(id=venue_id).all()[0]
  gen_data = []
  get_genres = Venue_genre.query.with_entities(Venue_genre.genres).join(Venue,Venue_genre.venue_id==Venue.id).filter(Venue_genre.venue_id==venue_id).all()
  for g in range(len(get_genres)):
    gen_data.append(get_genres[g].genres)

  state=form.state.default = venue_info.state
  seeking_talent=form.seeking_talent.default = venue_info.looking_for_talent
  genres=form.genres.default = gen_data
  form.process()  

  venue={
    "id": venue_info.id,
    "name": venue_info.name,
    "genres": genres,
    "address": venue_info.address,
    "city": venue_info.city,
    "state": state,
    "phone": venue_info.phone,
    "website_link": venue_info.website_link,
    "facebook_link": venue_info.facebook_link,
    "seeking_talent": seeking_talent,
    "seeking_description": venue_info.description,
    "image_link": venue_info.image_link }
 
  # [DONE] TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # [DONE] TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.filter_by(id=venue_id).all()[0]
   
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state =request.form['state']
    venue.phone =request.form['phone']
    venue.image_link =request.form['image_link']
    venue.facebook_link =request.form['facebook_link']
    venue.website_link =request.form['website_link']
    venue.description =request.form['seeking_description']
    venue.looking_for_talent = True if request.form.get('seeking_talent') else False


    Venue_genre.query.filter_by(venue_id=venue_id).delete()
    db.session.commit()

    genres = request.form.getlist('genres')
    for gen in genres:
          new_genre = Venue_genre(venue_id=venue_id,genres=gen)
          db.session.add(new_genre)
          db.session.commit()
      
    db.session.commit()

  except:
    db.session.rollback()
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
  # [DONE] TODO: insert form data as a new Venue record in the db, instead
  # [DONE] TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      name = form.name.data
      city = form.city.data
      state =form.state.data
      phone =form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      website_link =form.website_link.data
      seeking_description =form.seeking_description.data
      genres = form.genres.data
      seeking_venue = True if form.seeking_venue.data else False
      
    
      new_artist = Artist(name=name,city=city,state=state,phone=phone,
      image_link=image_link,facebook_link=facebook_link,website_link=website_link,
      looking_for_venues=seeking_venue,description=seeking_description)
      db.session.add(new_artist)
      db.session.commit()


      for gen in genres:
          new_genre = Artist_genre(artist_id=new_artist.id,genres=gen)
          db.session.add(new_genre)
          db.session.commit()

      error = False
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error : 
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    return render_template('pages/home.html')   
  elif not error:   
    flash('Artist ' + form.name.data + ' was successfully listed!') 
    return render_template('pages/home.html')   

      
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # [DONE] TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # [DONE]TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data1 = []
  shows = Shows.query.all()
  for i in range(len(shows)):
    artist =Artist.query.with_entities(Artist.id,Artist.name,Artist.image_link).join(Shows,Artist.id==Shows.artist_id).filter_by(id=shows[i].id).all()[0]
    venue =Venue.query.with_entities(Venue.id,Venue.name).join(Shows,Venue.id==Shows.venue_id).filter_by(id=shows[i].id).all()[0]
    new = {
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id":artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": shows[i].start_time
    }
    data1.append(new)
    print(data1)
  return render_template('pages/shows.html', shows=data1)#,artist_name=artist_name,venue_name=venue_name)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # [DONE] TODO: insert form data as a new Show record in the db, instead

  try:
    form = ShowForm(request.form)
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time =form.start_time.data
  
    new_show = Shows(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()

    error = False
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error : 
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')   
  elif not error:   
    flash('Show was successfully listed!')
    return render_template('pages/home.html')   

  # on successful db insert, flash success
 # flash('Show was successfully listed!')
  # [DONE] TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 # return render_template('pages/home.html')

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
