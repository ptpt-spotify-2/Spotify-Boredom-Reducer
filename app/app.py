from flask import Flask, render_template, jsonify, request
import API_requests


app = Flask(__name__)
req_handler = API_requests


@app.route('/')
def landing():

    return render_template('landing.html')


@app.route('/get_songs/', methods=['GET'])
def get_songs():

    q_type = request.args.get('query_type')
    subject = request.args.get('query_text')


    song_query = req_handler.song_search(q_type, subject)

    model_input_df = req_handler.get_model_input({
      'id': song_query['track_id'], 'popularity': song_query['popularity']})

    suggested_song_indices = req_handler.model_prediction(model_input_df)

    predicted_track_id_list = req_handler.get_tracks_model(suggested_song_indices)['tracks']

    track_items = req_handler.get_query_id(predicted_track_id_list, 'track')
    print(track_items)
    return 'Holy Crapola Spotify!'

if __name__ == '__main__':
    app.run()
