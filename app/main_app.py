from flask import Flask, render_template, jsonify, request
import API_requests


def run_app():
    app = Flask(__name__)
    req_handler = API_requests

    @app.route('/')
    def landing():

        return render_template('landing.html')

    @app.route('/get_songs/', methods=['GET'])
    def get_songs():

        q_type = request.args.get('query_type')
        subject = request.args.get('query_text')

        initial_song_query = req_handler.song_search(q_type, subject)

        model_input_df = req_handler.get_model_input({
            'id': initial_song_query['track_id'], 'popularity': initial_song_query['popularity']})

        suggested_song_indices = req_handler.model_prediction(model_input_df)

        predicted_track_id_list = req_handler.get_tracks_model(suggested_song_indices)['tracks']
        print(predicted_track_id_list)
        track_items = req_handler.get_query_id(predicted_track_id_list, 'track')

        songs_dict = dict()
        song_num = ['song1', 'song2', 'song3', 'song4', 'song5']

        for num, info in zip(song_num, track_items):
            songs_dict[num] = dict()
            songs_dict[num]['album_name'] = info[0]
            songs_dict[num]['album_image'] = info[1]
            songs_dict[num]['artist_name'] = info[2]
            songs_dict[num]['song_name'] = info[3]
            songs_dict[num]['item_id'] = info[4]
            songs_dict[num]['song_preview_url'] = info[5]

        print(songs_dict)
        return jsonify(songs_dict)

    if __name__ == '__main__':
        app.run()
