$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
    
    //chatsock.onmessage = function(message) {var data = JSON.parse(message.data);var chat = $("#chat");var ele = $('<ul></ul>');ele.append($("<li></li>").text(data.text));chat.append(ele)};

    chatsock.onmessage = function(message)
    {
        var data = JSON.parse(message.data);
        var chat = $("#chat");
        //var ele = $('<ul></ul>');
        chat.append($("<li></li>").text(data.creation_time + ": " + data.from_user + " ->" + data.to_user + ": "  + data.message_text));
        //chat.append(ele);
    };


    $("#chatform").on("submit", function(event)
    {
        var message = {
            message: $('#id_text').val(),
        }
        chatsock.send(JSON.stringify(message));
        //$("#message").val('').focus();
        return false;
    });
});