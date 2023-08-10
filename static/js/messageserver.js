$(document).ready(function () {
    let refreshing = true;
    let message_length = $("#message_length").val();
    let rid = $("#rid").val();
    //console.log(rid);
    var notificationSound = new Audio('/static/audio/notification.mp3');

    function refreshPage() {
        if (refreshing) {
            // 发起 GET 请求
            $.get(`/status/message_length/${rid}`, function (data) {
                // 把data.length 转换为整数
                let serverLength = data.length;
                //console.log("请求发起成功!")
                if (parseInt(serverLength) !== parseInt(message_length)) {
                    //console.log(serverLength, message_length)
                    notificationSound.play()
                    setTimeout(() => {
                        location.reload();
                    }, 1500);

                } else {
                    //console.log(serverLength, message_length)
                }
            });
        }
    }

    // 自动刷新页面，每隔两秒执行一次
    setInterval(refreshPage, 3000);

    // 监听文本框聚焦事件，设置refreshing为false
    $('#text').focus(function () {
        refreshing = false;
    });

    // 监听文本框失焦事件，设置refreshing为true
    $('#text').blur(function () {
        refreshing = true;
    });
});
