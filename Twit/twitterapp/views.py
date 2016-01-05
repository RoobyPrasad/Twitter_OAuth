import logging
import urlparse
import urllib
import simplejson
import oauth2 as oauth

from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from decorators import jsonify
from TwitterAuth.constants import REQUEST_TOKEN_URL, AUTHORIZE_URL, ACCESS_TOKEN_URL
from twitterapp.models import UserProfile


consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_SECRET_KEY)
client = oauth.Client(consumer)
log = logging.getLogger('console')


def twitter_login(request):

    # Get a request token from Twitter
    response, content = client.request(REQUEST_TOKEN_URL, "GET")
    log.debug('TWITTER REQUEST TOKEN RESPONSE : {}, CONTENT:{}'.format(response, content))
    if response['status'] != '200':
        raise Exception("Invalid response from Twitter")

    # Store request token in session for later use
    request.session['request_token'] = dict(urlparse.parse_qsl(content))

    # Redirect user to authentication url
    url = '{}?oauth_token={}'.format(AUTHORIZE_URL, request.session['request_token']['oauth_token'])
    return HttpResponseRedirect(url)


def login_authentication(request):
    log.info('TWITTER CALL BACK PARAMS : {}'.format(request.GET))
    # Create new client using request token in the session
    token = oauth.Token(request.session['request_token']['oauth_token'],
                        request.session['request_token']['oauth_token_secret'],
                        )
    token.set_verifier(request.GET['oauth_verifier'])

    client = oauth.Client(consumer, token)

    # Request authorized access token from twitter
    response, content = client.request(ACCESS_TOKEN_URL, "GET")
    log.debug('TWITTER ACCESS TOKEN RESPONSE : {}, CONTENT:{}'.format(response, content))
    if response['status'] != '200':
        raise Exception("Invalid response from Twitter")

    access_token = dict(urlparse.parse_qsl(content))
    # Create new user if it is not existing
    try:
        user = User.objects.get(username=access_token['screen_name'])
    except User.DoesNotExist:
        user = User.objects.create_user(access_token['screen_name'],
                                        '{}@twitter.com'.format(access_token['screen_name']),
                                        access_token['oauth_token_secret'])

        # Save permanent token & secret for future purpose
        profile = UserProfile()
        profile.user = user
        profile.oauth_token = access_token['oauth_token']
        profile.oauth_secret = access_token['oauth_token_secret']
        profile.save()

    if user.userprofile.oauth_secret != access_token['oauth_token_secret']:
        user.set_password(access_token['oauth_token_secret'])
        user.save()

        user_prof = UserProfile.objects.get(user=user)
        user_prof.oauth_token = access_token['oauth_token']
        user_prof.oauth_secret = access_token['oauth_token_secret']
        user_prof.save()
    # Authenticate & login using django's built-in function
    user = authenticate(username=access_token['screen_name'],
                        password=access_token['oauth_token_secret'])
    login(request, user)
    return HttpResponseRedirect('/')


@login_required
def twitter_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
@csrf_exempt
@jsonify
def tweet_message(request):
    twitter_user = request.user.userprofile

    if not twitter_user.oauth_token:
        return HttpResponseRedirect('/')

    access_token = twitter_user.oauth_token
    access_token_secret = twitter_user.oauth_secret
    token = oauth.Token(access_token, access_token_secret)
    client = oauth.Client(consumer, token)

    data = {'status': request.POST.get('tweet')}
    request_uri = 'https://api.twitter.com/1.1/statuses/update.json'
    response, content = client.request(request_uri, 'POST', urllib.urlencode(data))
    log.info('TWITTER MESSAGE POST RESPONSE: {}, CONTENT: {}'.format(response, content))
    if response['status'] != '200':
        return {}, 400
    return {}, 200


@login_required
@jsonify
def recent_tweets(request):
    twitter_user = request.user.userprofile

    if not twitter_user.oauth_token:
        return HttpResponseRedirect('/')

    access_token = twitter_user.oauth_token
    access_token_secret = twitter_user.oauth_secret
    token = oauth.Token(access_token, access_token_secret)
    client = oauth.Client(consumer, token)

    request_uri = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    response, content = client.request(request_uri, 'GET')
    if response['status'] != '200':
        return {}, 400
    return simplejson.loads(content), 200
