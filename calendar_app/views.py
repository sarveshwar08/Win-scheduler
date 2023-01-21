from django.shortcuts import render, redirect
import requests
import os

#rest framework imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

#google-api-python-client imports
import google.oauth2.credentials
import google_auth_oauthlib.flow

#google api discovery service to get help with the google apis
import googleapiclient.discovery

#scopes that this application can view on the behalf of the user
scopes =  ['https://www.googleapis.com/auth/userinfo.email', 
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid',
            'https://www.googleapis.com/auth/calendar']

#from google developer console
API_service = 'calendar'
API_version = 'v3'




#home page view
@api_view(['GET'])
def home_view(request):
    return render(request, 'calendar_app/home.html')




#initializes oauth
@api_view(['GET'])
def GoogleCalendarInitView(request):

    #flow object created using the client secret file
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret_.json',scopes = scopes)
    flow.redirect_uri = 'http://127.0.0.1:8000/rest/v1/calendar/redirect/'

    #access_type set to offline so tat refresh tokens can be exchanged for new access token even when the user is not on the app
    authorization_url, state = flow.authorization_url(access_type='offline')

    #set the state in the session object to maintain security with the authorization server
    request.session['state'] = state

    return redirect(authorization_url)
        



@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    events_list = []
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret_.json', scopes = scopes, state = state)
    flow.redirect_uri = 'http://127.0.0.1:8000/rest/v1/calendar/redirect/'
    auth_response = request.get_full_path()

    #fetching access and refresh tokens from the authorization server
    flow.fetch_token(authorization_response=auth_response)


    credentials = flow.credentials
    request.session['credentials'] = {
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'scopes': credentials.scopes
    }

    # print(request.session)
    try:
        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])
    except Exception:
        return redirect('/')
    
    calendar_api = googleapiclient.discovery.build(
        API_service, API_version, credentials=credentials)
    
    # Getting the user's calendar list, of which first entry (in "items" key) is the calendar linked to user's email
    calendars = calendar_api.calendarList().list().execute()
    if not calendars['items']:
        return Response({
            "error" : "Calendars not present"        
        })
    else:
        # getting the calendar id linked to user's email
        calendar_id = calendars['items'][0]['id']
        # getting the events of aforementioned calendar
        events  = calendar_api.events().list(calendarId=calendar_id).execute()

    #generating the event list to send as a response
    if not events['items']:
        return Response({"message": "Events not present"})
    else:
        for event in events['items']:
            events_list.append(event)
            return Response({"events": events_list})
    return Response(
        {"error": "something went wrong"}
        )



#added the delete session view for logout purposes of the app
@api_view(['GET'])
def Delete_session_view(request):
    request.session.flush()
    return redirect('/')


    









