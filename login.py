from flask import Flask, request, redirect, url_for, session, g, flash, \
     render_template
from flask_oauth import OAuth
 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
 

SECRET_KEY = 'Ko4SiOdrzo8g2XZoqahV0i5TWfQOCOhQVYFomqDvcLRCP7ZD0F'
DEBUG = True
 

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
 
twitter = oauth.remote_app('twitter',
   
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key='KC0QULnQzelIs6UsV1vuiaHhN',
    consumer_secret='5aZgs0VMXKmWX1H2cUVucHI5ffSC3yeQWz15IgwFuUj9X'
)
 
 
@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')
 
@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
 
    access_token = access_token[0]
 
    return render_template('index.html')
 
@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))
 
 
@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))
 
 
@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)
 
    access_token = resp['oauth_token']
    session['access_token'] = access_token
    session['screen_name'] = resp['screen_name']
 
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    
 
    return redirect(url_for('index'))
 
 
if __name__ == '__main__':
    app.run()
