$('#submit').click(function(){

    const json_request = {'query_type': $('#query_type option:selected').val(), 'query_text': $('#query_text').val()}

    $.ajax({
        url: '/get_songs/',
        type: 'GET',
        headers: {'Content-Type': 'application/json'},
        data: json_request,
        success: function(data){
            alert('Everything works. Now make it work better. ' + data['artist_name'])
        }
    })
})