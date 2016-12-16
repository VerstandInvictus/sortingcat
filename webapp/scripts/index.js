//authapi is declared in config.js and represents the publicly exposed API
//the second, non-exposed API's URL is only returned once the proper
//password is given as the key.

function authenticate() {
    var pass = prompt('Authenticate:')
    $.get(authapi + '/authenticate/' + pass, function(data) {
        apiroot = data[0];
        $.get(apiroot + '/folders', function(data) {
            $.each(data, function(index, value) {
                $('#selections').append('<p class=submit> ' +
                value['folder-name'] + '</p>')
            })
            $('.submit').click(function() {
                window.location.href = 'sort.html?folder=' + this.textContent.substring(1, this.textContent.length);
            })
        })
    })
}

authenticate();