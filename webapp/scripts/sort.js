function setImage(url) {
    $('#mainImg').off("load");
    $('#mainImg').fadeTo(350, 0, function() {
        $('#mainImg').attr('src', url);
    });
    $('#mainImg').load(function() {
        $('#mainImg').fadeTo(350, 1, function() {
            updateTickers();
        });      // fade in new
    });
}

function updateTickers() {
    $('#index').text('Index: ' + ind);
    $('#remain').text('Remain: ' + (total - ind));
    $('#session').text('Session: ' + session);
    $('#category').text(currentimage.tagged);
    $('#creator').text(currentimage.creator);
}

function authenticate() {
    urlParams = new URLSearchParams(window.location.search)
    folder = urlParams.get('folder');
    urlRoot = 'https://s3-us-west-2.amazonaws.com/' + folder + '/'
    var pass = prompt('Authenticate:')
    $.get(authapi + '/authenticate/' + pass, function(data) {
        apiroot = data[0];
        $.get(apiroot + '/folders', function(data) {
            $.each(data, function(index, value) {
                if (value['folder-name'] == folder) {
                    ind = value['index']
                    session = value['session']
                    total = value['total']
                }
            });
            $.get(apiroot + '/image/' + folder + '-' + ind, function (data) {
                currentimage = data
                setImage(urlRoot + data.filename)
            })
        })
    })
}

function tapTag() {
    imgTagPayload = {
        "folder-image": currentimage['folder-image'],
        "tag": currentimage.taptag
    }
    $.ajax({
        type: "POST",
        dataType: "json",
        url: apiroot + '/image/tap',
        contentType: 'application/json',
        data: JSON.stringify(imgTagPayload),
        success: function(response){
            $('#actionbox').html('<p>' + currentimage.taptag + '</p>');
            $('#actionbox').css('background-color', '#f7b03c');
            $('#actionbox').fadeTo(250, 0.7).delay(1000).fadeTo(250, 0);
        }
    })
}

function changeImage(arg) {
    console.log(arg)
    var tag = ''
    var tagtext = ''
    var popcolor = ''
    switch(arg) {
        case 'up':
            tag = currentimage.uptag
            tagtext = currentimage.uptag
            popcolor = '#5991ae'
            break
        case 'down':
            tag = currentimage.downtag
            tagtext = currentimage.downtag
            popcolor = '#e54e00'
            break
        case 'skip':
            tag = 'skipped'
            tagtext = 'skipped'
            popcolor = '#464746'
            break
        case 'back':
            tag = null
            tagtext = 'back'
            popcolor = '#464746'
            break
    }
    console.log(tag)
    if (tag != null) {
        imgTagPayload = {
                "folder-image": currentimage['folder-image'],
                "tag": tag
            }
        showPopover(tagtext, popcolor)
        ind += 1
        session += 1
        $.get(apiroot + '/image/' + folder + '-' + ind, function (data) {
            currentimage = data
            setImage(urlRoot + data.filename)
        })
        $.ajax({
            type: "POST",
            dataType: "json",
            url: apiroot + '/image/tag',
            contentType: 'application/json',
            data: JSON.stringify(imgTagPayload),
            success: function(response){
                indexPayload = {
                    "folder": folder,
                    "index": ind,
                    "session": session
                }
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: apiroot + '/folders/setindex',
                    contentType: 'application/json',
                    data: JSON.stringify(indexPayload)
                })
            }
        })
    }
    else if (tag == null) {
        showPopover(tagtext, popcolor)
        ind -= 1
        session -= 1
        indexPayload = {
            "folder": folder,
            "index": ind,
            "session": session
        }
        $.get(apiroot + '/image/' + folder + '-' + ind, function (data) {
            currentimage = data
            setImage(urlRoot + data.filename)
        })
        $.ajax({
            type: "POST",
            dataType: "json",
            url: apiroot + '/folders/setindex',
            contentType: 'application/json',
            data: JSON.stringify(indexPayload)
        })
    }
}

function resetSession() {
    session = 0
    indexPayload = {
        "folder": folder,
        "index": ind,
        "session": session
    }
    $.ajax({
        type: "POST",
        dataType: "json",
        url: apiroot + '/folders/setindex',
        contentType: 'application/json',
        data: JSON.stringify(indexPayload),
        success: function(response) {
            updateTickers();
        }
    })
}

function showPopover(tagtext, popcolor) {
    $('#tapbox').html('<p>' + tagtext + '</p>');
    $('#tapbox').css('background-color', popcolor);
    $('#tapbox').fadeTo(250, 0.7).delay(1000).fadeTo(250, 0);
}

authenticate();

$( document ).ready(function() {
    $(".floatbox").fadeTo(0,0);
    upact = 'up';
    downact = 'down'
    leftact = 'skip';
    rightact = 'back';

    $('#session').click(function() {
        resetSession();
    })

    // the gear VR's touchpad is logically flipped from UDLR on a screen
    // if we detect Samsung Internet, flip axes for input
    if ((navigator.userAgent.indexOf('SamsungBrowser') != -1)) {
        upaction = downact;
        downaction = upact;
        leftaction = rightact;
        rightaction = leftact;
        // cataction = dogact;
        // eastaction = westact;
        // ukaction = anarchy;
        console.log('detected Gear VR');
    }
    else {
        upaction = upact;
        downaction = downact;
        leftaction = leftact;
        rightaction = rightact;
    }

    $( ".ui-page" ).swipe( {
        swipeLeft:function(event, direction, distance, duration, fingerCount) {
            changeImage(leftaction);
            if (screenfull.enabled) {
               screenfull.request();
            };
        },
        swipeUp:function(event, direction, distance, duration, fingerCount) {
            changeImage(upaction);
            if (screenfull.enabled) {
               screenfull.request();
            };
        },
        swipeDown:function(event, direction, distance, duration, fingerCount) {
            changeImage(downaction);
            if (screenfull.enabled) {
               screenfull.request();
            };
        },
        swipeRight:function(event, direction, distance, duration, fingerCount) {
            changeImage(rightaction);
            if (screenfull.enabled) {
               screenfull.request();
            };
        },
    });
    $( document ).keydown(function(e) {
        switch(e.which) {
            case 37:
            case 22:
                changeImage(rightaction);
                break;
            case 38:
            case 19:
                changeImage(upaction);
                break;
            case 39:
            case 21:
                changeImage(leftaction);
                break;
            case 20:
            case 40:
                changeImage(downaction);
                break;
            case 32:
            case 35:
            case 102:
            case 103:
                tapTag();
                break;
        }
        e.preventDefault();
    });
    $(".ui-page").dblclick(function() {
        tapTag();
    });
});