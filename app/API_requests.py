# Handles all api requests and machine learning calls
import joblib
import json
import spotipy
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from urllib.parse import urlencode as url_enc

# Get the api keys from the environment.
spotify_client_id = os.environ['SPOTIFY_CLIENT']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']


# Authenticate the application and connect to the spotify api
auth = spotipy.SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
client = spotipy.Spotify(client_credentials_manager=auth)


def song_search(q_type, subject):
    """
    Connects to the spotify api and requests information based on query type.
    :param q_type: str
        This is the value of the "what are you looking for" field on the web form.
    :param subject: str
        This is the value of the text field containing the name of a the query object
        the user wishes to return, like album or playlist
    :return: dict
        dictionary containing song information required to look up the song via api
        request and get information required by the machine learning model.
    """

    # user input for use in api query
    q = subject.replace(' ', '%20')
    results = client.search(q, limit=1, type=q_type)

    # parse the api response
    if q_type == 'track' and results['tracks']['total'] != 0:
        # artist_name = results['tracks']['items'][0]['artists'][0]['name']
        # artist_id = results['tracks']['items'][0]['artists'][0]['id']
        # artist_uri = results['tracks']['items'][0]['artists'][0]['uri']
        # album_name = results['tracks']['items'][0]['album']['name']
        # album_image = results['tracks']['items'][0]['album']['images'][2]['url']
        # track_name = results['tracks']['items'][0]['name']
        track_id = results['tracks']['items'][0]['id']
        # track_preview_url = results['tracks']['items'][0]['preview_url']
        # track_uri = results['tracks']['items'][0]['uri']
        popularity = results['tracks']['items'][0]['popularity']

        # save the data into dictionary
        result_dict = {
            # 'artist_name': artist_name,
            # 'artist_id': artist_id,
            # 'artist_uri': artist_uri,
            # 'album_name': album_name,
            # 'album_image_url': album_image,
            # 'track_name': track_name,
            'track_id': track_id,
            # 'track_preview_url': track_preview_url,
            # 'track_uri': track_uri,
            'popularity': popularity
        }

        return result_dict


def get_query_id(query_results, query_type='track'):
    """
    get id(s) for query results. if query type is set to track also returns
    preview url.
    :param query_results: json object
    :param query_type: str
    :return: id_list
    """
    id_list = list()
    for item in query_results:

        album_name = item['album']['name']
        album_image = item['album']['images'][2]['url']
        artist_name = item['album']['artists'][0]['name']
        song_name = item["name"]
        item_id = item["id"]

        if query_type == query_type:
            preview = item["preview_url"]
            id_list.append((
                album_name, album_image, artist_name,
                song_name, item_id, preview
            ))
        else:
            id_list.append((
                album_name, album_image, artist_name,
                song_name, item_id
            ))

    return id_list


def get_model_input(track_item):
    """

    returns the features required for model input from a queried track item.

    :param track_item: spotify API queried item
        must include track id and  popularity
    :return: model_features: list()
    """

    features_list = list(['duration_ms',
                          'danceability', 'energy', 'key',
                          'loudness', 'mode', 'speechiness',
                          'acousticness', 'instrumentalness', 'liveness',
                          'valence', 'tempo'])

    track_id = track_item['id']
    popularity = track_item['popularity']

    track_features_query = client.audio_features(tracks=[track_id])
    track_features = track_features_query[0]

    features_dict = dict({"popularity": f"{popularity}"})

    for key in features_list:
        features_dict[f'{key}'] = track_features[f"{key}"]

        model_df = pd.DataFrame(features_dict, index=[0])
    if isinstance(model_df, pd.DataFrame):
        return model_df
    else:
        raise Exception('model_df not a dataframe or is not set')


def model_prediction(model_input):
    """
    :param model_input: Pandas Dataframe
    :return: Predicted Song indexes
    """

    scalable_features = ['duration_ms', 'popularity', 'tempo', 'key']
    scaling_transformer = Pipeline(steps=[('scaler', MinMaxScaler())])
    knn = joblib.load("Spotify-Boredom-Reducer/model/knn_best.joblib.gz")

    column_trans = ColumnTransformer(
        transformers=[
            ('scaled', scaling_transformer, scalable_features)],
        remainder='passthrough'
    )
    transformed_features = column_trans.fit_transform(model_input)

    neighbors = knn.kneighbors(transformed_features[0].reshape(1, -1), return_distance=False)[0]
    neighbors_list = neighbors.tolist()
    return neighbors_list


def get_tracks_model(model_output):
    """

    :param model_output: List
    :return: Spotify_api tracks
    """
    track_list = list()
    open_tracks = open("Spotify-Boredom-Reducer/csv/df_ids.json")
    track_ids = json.load(open_tracks)

    for key in model_output:
        track_list.append(track_ids[str(key)])

    track_items = client.tracks(track_list)
    return track_items
