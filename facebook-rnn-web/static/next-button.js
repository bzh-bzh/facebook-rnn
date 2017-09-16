$(function() {
    var dots = 0;
    function type() {
        if(dots < 3) {
            $('#loading-indicator').append('.');
            dots++;
        } else {
            $('#loading-indicator').html('');
            dots = 0;
        }
    }
    function cleanUpLoading(interval) {
        clearInterval(interval)
        $('#loading-indicator').html('');
        dots = 0;
    }
    $('a#next').bind('click', function() {
        var loadingInterval = setInterval(type, 80);
        $.ajax({
            dataType: "json",
            url: $SCRIPT_ROOT + '/next',
            cache: false,
            success: function(data) {
                cleanUpLoading(loadingInterval);
                $("#message").slideUp('fast').promise().done( function() { $("#message").html('<b>Benjamin:</b> ' +data.update.autoLink()).slideDown('fast'); });
                },
            error: function(jqXHR, textStatus, errorThrown) {
                cleanUpLoading(loadingInterval);
                $("#message").slideUp('fast').promise().done( function() { $("#message").html('\<span style=\"color: red\"\>' +
                '\There\'s an error\. Try checking your internet; if not, come back later.\<\/span\>').slideDown('fast'); });
                }
        });
    });
});