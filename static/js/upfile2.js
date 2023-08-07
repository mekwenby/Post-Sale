$(document).ready(function () {
    const fileSelectDiv = $('#file-select-div');
    const fileInput = $('#file-input');

    const imagesSelectDiv = $('#images-select-div');
    const imagesInput = $('#images-input');

    fileSelectDiv.on('click', function () {
        fileInput.click();
    });

    imagesSelectDiv.on('click', function () {
        imagesInput.click();
    })


    fileInput.on('change', function () {
        const file = fileInput[0].files[0];
        if (file) {
            const allowedExtensions = ['.png', '.jpg', '.jpeg', '.zip', '.rar', '.pdf', '.txt', '.doc', '.docx', '.xls', '.xlsx', '.xlsm'];
            const fileExtension = file.name.split('.').pop().toLowerCase();

            if ($.inArray(`.${fileExtension}`, allowedExtensions) !== -1) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('rid', $('#rid').val()); // 添加rid的值到formData中
                formData.append('up_name', $('#up_name').val()); // 添加rid的值到formData中

                // 使用jQuery的ajax方法将文件发送到后端
                $.ajax({
                    url: '/upload_test',
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function (response) {
                        alert(response);
                        // 刷新
                        location.reload()


                        $('#file_list').append(tableRow);
                    },
                    error: function () {
                        alert('文件上传失败');
                    }
                });
            } else {
                alert("只能上传png,jpg,jpeg,zip,rar,pdf,txt,doc,docx,xls,xlsx,xlsm 格式的文件");
            }
        }
    });

});
