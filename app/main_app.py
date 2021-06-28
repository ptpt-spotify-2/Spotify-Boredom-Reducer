"""Application to make Spotify song suggestions based on a song the user inputs."""
from flask import Flask, render_template, jsonify, request
import API_requests


def run_app():
    """
    Function in which the main app resides.
    :return: No return value
    """
    app = Flask(__name__)
    req_handler = API_requests

    @app.route('/')
    def landing():
        """
        Main route for the application. Functions as the landing
        or homepage.
        :return: jinja template containing the web form.
        """
        return render_template('landing.html')

    @app.route('/get_songs/', methods=['GET'])
    def get_songs():
        """
        This is the route containing the functionality of the application.
        The webform data is collected via jquery and sent to this endpoint
        via GET request. This triggers the application to fetch the most
        similar song entered by the user from Spotify. That song's features
        are then extracted and used by a clustering algorithm, KNN, to find
        similar songs, 5 of which are returned.

        :return: json obj containing songs suggested by the machine learning
        model.
        """

        # This is the code to save the data from the web form.
        # q_type is the type of object the user is looking for,
        # track/song, artist, playlist, album.
        # subject is the text entered by the user into the text field.
        q_type = request.args.get('query_type')
        subject = request.args.get('query_text')

        # This line searches for the song via the Spotify api using
        # the library spotipy.
        initial_song_query = req_handler.song_search(q_type, subject)

        # This line gets a python dictionary to pass to the model for
        # conversion to a pandas dataframe.
        model_input_df = req_handler.get_model_input({
            'id': initial_song_query['track_id'], 'popularity': initial_song_query['popularity']})

        # This line transforms the data and gets the model prediction
        suggested_song_indices = req_handler.model_prediction(model_input_df)

        # This line interprets the model prediction and returns the pandas dataframe
        # indices of the selected songs.
        predicted_track_id_list = req_handler.get_tracks_model(suggested_song_indices)['tracks']

        # This line gets the song information required to populate the song
        # preview section of the web application fron-end.
        track_items = req_handler.get_query_id(predicted_track_id_list, 'track')

        # Prep the list for returned song data
        songs_dict = dict()
        song_num = ['song1', 'song2', 'song3', 'song4', 'song5']

        # Creates a dictionary to return as a json object for
        # populating the song preview.
        for num, info in zip(song_num, track_items):
            songs_dict[num] = dict()
            songs_dict[num]['album_name'] = info[0]
            songs_dict[num]['album_image'] = info[1]
            songs_dict[num]['artist_name'] = info[2]
            songs_dict[num]['song_name'] = info[3]
            songs_dict[num]['item_id'] = info[4]
            songs_dict[num]['song_preview_url'] = info[5]

        # Return the json object with each song having
        # it's own dictionary of features.
        return jsonify(songs_dict)

    if __name__ == '__main__':
        app.run()
