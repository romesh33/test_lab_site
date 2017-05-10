window.ee = new EventEmitter();
// читаем в локальную переменную messages объекты, полученные из джанго в виде json и преобразованные в js объекты
// в глобальном js скрипте (в теле event.html):
// messages is a list of messages without ID:
//var messages = messages_obj;
// messages_dict is a dictionary with keys = message ids and values = dictionaries {from, text, time}:
var messages_dict = messages_dict_obj;
var users = users_obj;
var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var path = ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname;
//var user_is_authenticated = user_is_authenticated;
console.log("Opened web socket with path: " + path);
console.log("Users: " + users);
// создаем сокет:
var chatsock = new ReconnectingWebSocket(path);

// регистрируем функцию по обработке события "получение сообщения" в веб-сокете:
chatsock.onmessage = function(message)
{
    console.log("Message received by web socket");
    // так как данные в объекте message сериализованы в json, парсим его для получения объекта js:
    var data = JSON.parse(message.data);
    if (data.message_text != null)
    {
        var message_id = data.id;
        console.log("new_nessage_id = " + message_id);
        var sender = data.sender;
        console.log("sender=" + sender);
        var text = data.message_text;
        console.log("text of receivd message=" + text);
        var time = data.time;
        console.log("time=" + time);
        var received_message = {"id": message_id, "from": sender, "text": text, "time": time};
        //console.log("received_message = " + received_message);
        //messages.push(received_message);
        window.ee.emit('Message.add', received_message);
        //console.log("Messages length: " + messages.length);
    }
    else
    {
        console.log("Were are here!");
        if (data.user_connected != null)
        {
            var username = data.user_connected;
            console.log("User " + username + " is connected");
            window.ee.emit('User.add', username);
        }
        else if (data.user_disconnected != null)
        {
            var username = data.user_disconnected;
            console.log("User " + username + " is disconnected");
            window.ee.emit('User.remove', username);
        }
        else if (data.action != null)
        {
            var deleted_message_id = data.id;
            console.log("Hey hey hey!!! Someone deleted message with id + " + deleted_message_id + " in the chat..");
            window.ee.emit('Message.delete', deleted_message_id);
        }
        // сюда мы должны попасть, если посылаем сообщение из функции consumers, которая посылает сообщение в ответ на
        // подключение вебсокета:
        //console.log("message length is zero... it can be because user is connected, in this case no messsage data exists...");
        //TODO: need to add handler when message is deleted 
    }
};

var SendMessageBar = React.createClass({
    handleButtonClick: function()
    {
        var text = this.refs.messageTextInput.value;
        if (text.length > 0)
        {
            //alert(text);
        }
        else
        {
            //alert("Message text is empty");
        }
        this.props.onButtonClick(text);
    },
    render: function()
    {
        return (
            <div className="bordered">
                <input placeholder='введите сообщение' ref='messageTextInput'/>
            <button onClick={this.handleButtonClick}>Отправить</button>
            </div>
        )
    }
});

var DeleteMessageButton = React.createClass({
    handleDeleteButtonClick: function() {
        var message_id = this.props.messageId;
        this.props.onButtonClick(message_id);
    },
    render: function()
    {
        var message_creator = this.props.creator;
        //user_name
        //console.log(message_creator, user_name, user_is_authenticated);
        if ((user_name == message_creator) && (user_is_authenticated == 1))
        {
            return (
                <button onClick={this.handleDeleteButtonClick}>x</button>
            )
        }
        else
        {
            return (
                <span></span>
            );
        }
    }
});

var Message = React.createClass({
    render: function()
    {
        return (
            <div className="bordered">
                <span>{this.props.time}: {this.props.user}: {this.props.text}</span>
                <DeleteMessageButton onButtonClick={this.props.onMessageDelete} messageId={this.props.id} creator={this.props.user}/>
            </div>
        )
    }
});
      
var MessageTable = React.createClass({
    render: function() {
        var messages = [];
        var messDelFunction = this.props.onMessageDelete;
        var messages_dict = this.props.messages;
        $.each(messages_dict, function(key, message) {
            //console.log("TEXT= " + message.text);
            //console.log("KEY= " + key);
            messages.push(<Message text={message.text} time={message.time} user={message.from}
                key={key} onMessageDelete={messDelFunction} id={key}/>);
        });
        return (
            <div>
                {messages}
            </div>
        )
    }
});
        
var Chat = React.createClass({
    getInitialState: function() {
        return {
            messages: messages_dict
        };
    },
    componentDidMount: function() {
        var self = this;
        window.ee.addListener('Message.add', function(received_message) {
            //messages.push(received_message);
            //todo: now when new message is sent, it has id like 300. If there are only 50 messages in props,
            //rest of indexes are filled with nulls :( need to fix this
            var id = received_message['id'];
            var from = received_message['from'];
            var text = received_message['text'];
            var time = received_message['time'];
            var messages_temp = self.state.messages;
            console.log(id,from,text,time);
            messages_temp[id] = {from: from, text: text, time: time};
            self.setState({messages: messages_temp});
        });
        window.ee.addListener('Message.delete', function(deleted_message_id) {
            var messages_temp = self.state.messages;
            delete messages_temp[deleted_message_id];
            self.setState({messages: messages_temp});
        });
    },
    componentWillUnmount: function() {
        window.ee.removeListener('Message.add');
        window.ee.removeListener('Message.delete');
    },
    handleMessageSend : function(text) {
        console.log("Message was sent to web socket with text: " + text);
        chatsock.send(JSON.stringify(text));
    },
    handleMessageDelete : function(message_id) {
        //console.log("Chat: Message with id: " + message_id + " will be deleted");
        var messages_temp = this.state.messages;
        delete messages_temp[message_id];
        this.setState({messages: messages_temp});
        var delete_message_text = {id: message_id, action: 'delete_message'};
        console.log("Sending delete message to socket:" + delete_message_text);
        chatsock.send(JSON.stringify(delete_message_text));
    },
    render: function() {
        // variable user_is_authenticated is taken from global variables from event's html page:
        if (user_is_authenticated == 1)
        {
            return (
                <div>
                    <div className="chat_app" id="chat">
                        <h1>This is chat!</h1>
                        <MessageTable messages={this.state.messages} onMessageDelete={this.handleMessageDelete}/>
                        {/* This is comment */}
                    </div>
                    <SendMessageBar onButtonClick={this.handleMessageSend}/>
                </div>
            )
        }
        else
        {
            return (
                <div>
                    <div className="chat_app" id="chat">
                        <h1>This is chat!</h1>
                        <MessageTable messages={this.state.messages} onMessageDelete={this.handleMessageDelete}/>
                        {/* This is comment */}
                    </div>
                </div>
            )
        }
    }
});

var SingleUser = React.createClass({
    render: function() {
        return (
            <span>{this.props.name} </span>
        )
    }
});

var UsersList = React.createClass({
    getInitialState: function() {
        return {
            users: users,
        };
    },
    componentDidMount: function() {
        var self = this;
        window.ee.addListener('User.add', function(username) {
            var more_users = self.state.users;
            // if user doesn't exist in the list (it's possible when Refreshing the page and in other unknown cases)
            // - add it to array of users:
            if (more_users.indexOf(username) == -1)
            {
                console.log("1 - Didn't find the user in the list and added it");
                more_users.push(username);
            }
            else
            // if user was found in the list:
            {
                console.log("2 - Found the user in the list and didn't add it");
            }
            self.setState({users: more_users});
            console.log("Listener noticed that user " + username + " was connected");
        });
        window.ee.addListener('User.remove', function(username) {
            var less_users = self.state.users;
            var index = users.indexOf(username);
            if (index != -1)
            {
                //if user was found in the list of online users - delete it:
                less_users.splice(index, 1);
            }
            else
            {
                // otherwise - do nothing:
                console.log("User " + username + " wasn't found in the list of online users");
            }
            console.log("Listener noticed that user " + username + " was disconnected");
            //users.push(username);
            self.setState({users: less_users});
        });
    },
    componentWillUnmount: function() {
        window.ee.removeListener('User.add');
        window.ee.removeListener('User.remove');
    },
    render: function() {
        var users = [];
        this.state.users.forEach(function(user, index) {
            users.push(<SingleUser name={user} key={index} />);
        });
        return (
            <div>
                {users}
            </div>
        )
    }
});

ReactDOM.render(<Chat />, document.getElementById('new_chat'));
ReactDOM.render(<UsersList />, document.getElementById('user_list'));

// this function does autoscrolling to the bottom of the chat. I'm not sure how it works - just copied example from SO :)
// http://stackoverflow.com/questions/25505778/automatically-scroll-down-chat-div
// TODO: to understand how it works
setInterval(function () {
    $("#chat").animate({
        scrollTop: $("#chat")[0].scrollHeight}, -500);
}, 1000);