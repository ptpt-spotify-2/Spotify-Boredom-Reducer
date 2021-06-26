$('#submit').click(function(){

    const json_request = {'query_type': $('#query_type option:selected').val(), 'query_text': $('#query_text').val()};

    $.ajax({
        url: '/get_songs/',
        type: 'GET',
        headers: {'Content-Type': 'application/json'},
        data: json_request,
        success: function(data) {

            // alert('Everything works. Now make it work better.');

            $('#song1 a').attr('href', data['song1']['song_preview_url']);
            $('#song2 a').attr('href', data['song2']['song_preview_url']);
            $('#song3 a').attr('href', data['song3']['song_preview_url']);
            $('#song4 a').attr('href', data['song4']['song_preview_url']);
            $('#song5 a').attr('href', data['song5']['song_preview_url']);

            $('#song1 img').attr('src', data['song1']['album_image']);
            $('#song2 img').attr('src', data['song2']['album_image']);
            $('#song3 img').attr('src', data['song3']['album_image']);
            $('#song4 img').attr('src', data['song4']['album_image']);
            $('#song5 img').attr('src', data['song5']['album_image']);

            $('#song1 .artist_name').text(data['song1']['artist_name']);
            $('#song2 .artist_name').text(data['song2']['artist_name']);
            $('#song3 .artist_name').text(data['song3']['artist_name']);
            $('#song4 .artist_name').text(data['song4']['artist_name']);
            $('#song5 .artist_name').text(data['song5']['artist_name']);

            $('#song1 .song_name').text(data['song1']['song_name']);
            $('#song2 .song_name').text(data['song2']['song_name']);
            $('#song3 .song_name').text(data['song3']['song_name']);
            $('#song4 .song_name').text(data['song4']['song_name']);
            $('#song5 .song_name').text(data['song5']['song_name']);

            $('#song').attr('src', data['song2']['song_preview_url']);
            $('#player')[0].load()
            $('#player')[0].pause()

            $('#suggested_songs').css('display', 'grid')
            $('#player').toggle(true);
        }
    });
});
$('#clear_form').click(function(){
    $('#suggested_songs').toggle(false);
    $('#query_type option:selected').val('track');
    $('#query_text').val('');
    $('#song').attr('src', '');
    $('#player').stop();
    $('#player')[0].load();
});

$('p.songs').bind('click', function(){
    let id = $(this).attr('id')
    id = '#' + id + ' a'
    $('#song').attr('src', $(id).attr('href'));
    $('p.songs').css('background', '#EFF5F6');
    $('#player').stop();
    $('#player')[0].load()
    $('#player').toggle(true);
    $('#suggested_songs').toggle(true);
    $('#player')[0].play();
    $(this).css('background', 'lightblue');
})