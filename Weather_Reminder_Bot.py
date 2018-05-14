

import keys
import twitter
import requests
import json
import time
import datetime

def main():

    # In this first section, we'll gather the current weather forcast data and determine the correct message to send out.

    # Since our twitter bot is only concerned about reminding NYC residents of the current weather conditions,
    # we call the Open Weather Map api here. If we wanted to remind other Twitter users, we could move this function
    #to where we are examining individual tweets, and replace the hard coded latitude and longitude with the location
    # data from the tweet itself.

    latitude  = 40.75
    longitude = -73.92

    data = requests.get('http://api.openweathermap.org/data/2.5/forecast?',
                         params = { 'lon':longitude , 'lat':latitude , 'APPID':keys.openweather_key  , 'units':'imperial'})

    weather_data = json.loads(data.text)
    temp = weather_data['list'][1]['main']['temp']
    condition_code = weather_data['list'][1]['weather'][0]['id']

    # Here we choose which message we are going to send, based on the weather forcast info we recieved above.
    if condition_code < 300:
        message = "If you're going to the park, you might want to reconsider. It looks like thunderstorms are forcasted later!"
    elif condition_code < 600:
        message = "If you're going to the park, make sure you bring an umbrella! The weather report calls for rain later."
    elif condition_code < 700:
        message = "If you're going to the park, make sure you're bundled up! The weather report calls for rain later."
    elif condition_code == 800:
        if temp < 45:
            message = "If you're going to the park, make sure and bundle up. It's going to be cold! The weather report calls for clear skys with a temperature of {0} °F later.".format(int(round(temp)))
        elif temp < 60:
            message = "If you're going to the park, you might want to bring a jacket. Looks like it will be a little chilly later. The weather report calls for clear skys with a temperature of {0} °F later.".format(int(round(temp)))
        else:
            message = "If you're going to the park, make sure to bring sunglasses! The weather report calls for clear skys with a temperature of {0} °F later.".format(int(round(temp)))
    elif 800 < condition_code <810:
        if temp < 45:
            message = "If you're going to the park, make sure and bundle up. It's going to be cold! The weather report calls for cloudy skys with a temperature of {0} °F later.".format(int(round(temp)))
        elif temp < 60:
            message = "If you're going to the park, you might want to bring a jacket. Looks like it will be a little chilly later. The weather report calls for cloudy skys with a temperature of {0} °F later.".format(int(round(temp)))
        else:
            message = "If you're going to the park, make sure to bring sunglasses! The weather report calls for cloudy skys with a temperature of {0} °F later.".format(int(round(temp)))

    elif condition_code == 701 or 721 or 741:
        message = "If you're going to the park, it may not be the best photo op! The weather report calls for fog and low visibilty, with a temperature of {0} °F later.".format(int(round(temp)))
    else:
        message = "If you're going to the park, you may want to bring a facemask. The weather report indicates a lot of particulate matter in the air."

    print(message)


    # In this next section, we use the twitter API to search for out trigger phrase, and then send out weather remider tweets
    # to the targeted users.

    twitter_api = twitter.Api(keys.twitter_consumer_key,
                      keys.twitter_consumer_secret,
                      keys.twitter_access_key,
                      keys.twitter_access_secret)

    # We set up all of the parameters for our search here.
    range = "8mi"
    search_params = [latitude, longitude, range]
    search_term = "I can't wait to go to the park tomorrow!"

    search = twitter_api.GetSearch(term = search_term, geocode = search_params, result_type = "recent")

    # We will loop this program every 10 minutes to avoid sending too many API calls, so we want to avoid replying to the
    # same tweet twice. In the below section, we determine if the tweet was created in the last ten minutes, and then only
    # reply to those tweets.

    # This creates a datetime object with the current date and UTC time
    current_time = datetime.datetime.utcnow()
    # This adds the UTC timezone to the datetime object we created above in order to make it an aware datetime object,
    # so that we can compare the tweet time to the current time.
    # Apparently we specifically have to add the timezone, even though we asked for the UTC time...
    current_time = current_time.replace(tzinfo=datetime.timezone.utc)

    # This creates adds to a log file, detailing when we searched twitter, and how many tweets we found.
    with open('Weather_Bot_Log.txt', 'a') as the_file:
        the_file.write('Searching for tweets at {0}. Found {1} tweets. \n'.format(current_time, len(search)))

    # This section goes through each tweet we found in our above search and determines if it was created in the last
    # ten minutes.If it was, we reply to it with our weather reminder.
    for line in search:
        try:
            created_at = datetime.datetime.strptime(line.created_at, '%a %b %d %H:%M:%S %z %Y')
            time_difference = current_time - created_at
            time_difference_in_minutes = time_difference / datetime.timedelta(minutes=1)
            if time_difference_in_minutes < 10:
                # Since we've determined that this tweet is recent, we reply to it directly here.
                status = twitter_api.PostUpdate(message, in_reply_to_status_id = line.id, auto_populate_reply_metadata = True )
                # And add a line to our log file.
                with open('Weather_Bot_Log.txt', 'a') as the_file:
                    the_file.write('Sent a message to {0} in reply to tweet id: {1}. The message was: {2} \n'.format(
                    line.user.screen_name, line.id, message))
            else:
                # If the tweet is old, we don't send anything, but we do add it to our log.
                with open('Weather_Bot_Log.txt', 'a') as the_file:
                    the_file.write('Attempted to send a message to {0} in reply to tweet id: {1}, but realized the tweet was old. \n'.format(
                    line.user.screen_name, line.id, message))
        except:
            # If something goes wrong, we add it to the log. (Tweets with strange characters can raise errors.)
            with open('Weather_Bot_Log.txt', 'a') as the_file:
                the_file.write("Something went wrong \n")
            continue


    print ("Main function completed at approximately:", current_time)

    # After replying, we wait 10 minutes.
    time.sleep(600)


while True:
    main()
