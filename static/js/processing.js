$(document).ready(function () {
    // 定义变量来存储当前 processing 状态
    let currentProcessing = 0;
    const notificationSound = new Audio('/static/audio/5c891af7b99bf4663.mp3');

    // 发起初始请求
    $.get("/status/processing", function (data) {
        currentProcessing = data.processing;
        // 设置定时器，每隔三秒发送请求
        setInterval(function () {
            $.get("/status/processing", function (data) {
                //console.log(data.processing)
                if (data.processing > currentProcessing) {
                    // 工单变多时
                    //console.log('检测到工单变多了')
                    notificationSound.play()
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else if (data.processing < currentProcessing) {
                    // 工单变少时
                    //console.log('检测到工单变少了')
                    currentProcessing = data.processing;
                    location.reload();
                }
            });
        }, 3000);
    });
});