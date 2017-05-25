var Timer = React.createClass({
    render: function() {
        return (
            <p>
                Прошло времени (чч:мм:сс): {this.props.duration}.
            </p>
        )
    }
});

var FinishButton = React.createClass({
    render: function() {
        return (
            <span>
                <a href={finish_link} className="btn btn-default active" role="button">Завершить</a>
            </span>
        )
    }
});

var ContinueButton = React.createClass({
    render: function() {
        return (
            <a href={continue_link} className="btn btn-default active" role="button">Продолжить</a>
        )
    }
});

var StartButton = React.createClass({
    render: function() {
        return (
            <a href={start_link} className="btn btn-default active" role="button">Начать</a>
        )
    }
});

var StopButton = React.createClass({
    render: function() {
        return (
            <a href={stop_link} className="btn btn-default active" role="button">Остановить</a>
        )
    }
});

var TaskPanel = React.createClass({
    render: function() {
        if (user_is_authenticated == 1)
        {
            switch(task_status) {
                case 'RUNNING':
                    return (
                        <div>
                            <Timer duration={this.props.duration}/>
                            <StopButton />
                            <FinishButton />
                        </div>
                    );
                case 'IDLE':
                    if ((linked_task && linked_task_finished) || (!linked_task))
                    {
                        return (
                            <div>
                                <StartButton />
                            </div>
                        )
                    }
                    else if (linked_task && !linked_task_finished)
                    {
                        return (
                            <span>У задачи есть связанная задача (см. ссылку ниже). Выполните, пожалуйста, сначала её.</span>
                        )
                    }
                case 'STOPPED':
                    return (
                        <div>
                            <Timer duration={this.props.duration}/>
                            <ContinueButton />
                            <FinishButton />
                        </div>
                    );
                case 'FINISHED':
                    if (dependant_task)
                    {
                        return (
                        <div>
                            <Timer duration={this.props.duration}/>
                            <p>Поздравляем, вы завершили задание!
                            Вам открылось задание:</p>
                            <a href={dependant_task_link}>{dependant_task_code}: {dependant_task_title}</a>
                        </div>
                        )
                    }
                    else
                    {
                        return (
                        <div>
                            <Timer duration={this.props.duration}/>
                            Поздравляем, вы завершили задание!
                        </div>
                        )
                    }
            }
        }
        else
        {
            return (<p>Вы должны авторизоваться перед тем, как начать задачу.</p>);
        }
    }
});

var duration_inc = moment.duration(duration);
if (task_status == 'RUNNING')
{
    var now = moment.utc();
    var past_moment = 0;
    // если задача стартована, но duration нулевой (в базе джанго) - у нас таймер начнется с нуля
    // но мы должны брать не ноль, а текущий момент и сравнивать его с временем старта или продолжения:
    if (duration == '0:00:00')
    {
        if ((start_time && !comeback_time))
        {
            past_moment = moment.utc(start_time);
        }
        else if (start_time && comeback_time)
        {
            if(start_time > comeback_time)
            {
                past_moment = moment.utc(start_time);
            }
            else
            {
                past_moment = moment.utc(comeback_time);
            }
        }
        duration_inc.add(now-past_moment);
    }
    else
    {
        console.log("Duration is not null");
    }
    function tick() {
        duration_inc.add(1, 's');
        var formatted_duration = moment.utc(duration_inc.as('milliseconds')).format('HH:mm:ss');
        ReactDOM.render(<TaskPanel duration={formatted_duration}/>, document.getElementById('task_panel')
        );
    }
    setInterval(tick, 1000);
}
else
{
    var formatted_duration = moment.utc(duration_inc.as('milliseconds')).format('HH:mm:ss');
    ReactDOM.render(
        <TaskPanel duration={formatted_duration}/>, document.getElementById('task_panel')
    );
}


