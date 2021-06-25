import joblib
import json
import spotipy
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd


spotify_client_id = os.environ['SPOTIFY_CLIENT']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

auth = spotipy.SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
client = spotipy.Spotify(client_credentials_manager=auth)


def song_search(q_type, subject):

    q = subject.replace(' ', '%20')
    results = client.search(q, limit=1, type=q_type)

    if q_type == 'track':
        artist_name = results['tracks']['items'][0]['artists'][0]['name']
        artist_id = results['tracks']['items'][0]['artists'][0]['id']
        artist_uri = results['tracks']['items'][0]['artists'][0]['uri']
        track_name = results['tracks']['items'][0]['name']
        track_id = results['tracks']['items'][0]['id']
        track_preview_url = results['tracks']['items'][0]['preview_url']
        track_uri = results['tracks']['items'][0]['uri']
        popularity = results['tracks']['items'][0]['popularity']

        result_dict = {
            'artist_name': artist_name,
            'artist_id': artist_id,
            'artist_uri': artist_uri,
            'track_name': track_name,
            'track_id': track_id,
            'track_preview_url': track_preview_url,
            'track_uri': track_uri,
            'popularity': popularity
        }

        return result_dict


def get_query_id(query_results, query_type=None):
    """
    get id(s) for query results. if query type is set to track also returns
    preview url.
    :param query_results: json object
    :param query_type: str
    :return: id_list
    """
    id_list = list()
    for item in query_results:
        name = item["name"]
        item_id = item["id"]
        if query_type == "track":
            preview = item["preview_url"]
            id_list.append((name, item_id, preview))
        else:
            id_list.append((name, item_id))

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

    return model_df


def model_prediction(model_input):
    """
    :param model_input: Pandas Dataframe
    :return: Predicted Song indexes
    """

    scalable_features = ['duration_ms', 'popularity', 'tempo', 'key']
    scaling_transformer = Pipeline(steps=[('scaler', MinMaxScaler())])
    knn = joblib.load("../model/knn_best.joblib.gz")

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
    open_tracks = open("../csv/df_ids.json")
    track_ids = json.load(open_tracks)

    for key in model_output:
        track_list.append(track_ids[str(key)])

    track_items = client.tracks(track_list)
    return track_items
