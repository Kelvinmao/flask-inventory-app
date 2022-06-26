$(document).ready(function() {
    $("#upload").click(function(){
        const formProfile = new FormData();
        const fileObj = document.getElementById("audio_upload").files[0];
        const name = document.getElementById("full_name").value;
        const gender = document.getElementById("gender").value;
        const age = document.getElementById("age").value;
        const visit_date = document.getElementById("created_at").value;
        const survey_type = document.getElementById("survey_type").value;
        const score = document.getElementById("score").value;

        const path = document.getElementById("audio_upload").value;
        const file_name_list = path.split('\\');
        const file_name = file_name_list[file_name_list.length - 1];
        const form = document.getElementById("patient_form")

        formProfile.append("audio_file", fileObj);
        formProfile.append("full_name", name);
        formProfile.append("gender", gender);
        formProfile.append("age", age);
        formProfile.append("created_at", visit_date);
        formProfile.append("survey_type", survey_type);
        formProfile.append("score", score);
        formProfile.append("recording_dir", file_name)

        $.ajax({
            type : "POST",
            url : '/api/v1/files/audios',
            data : formProfile,
            dataType: "json",
            cache: false,
            processData: false,
            contentType: false,
            success : function(data){
                if (data['state'] == 'SUCCESS')
                    window.alert("添加成功");
                else if (data['state'] == 'EXIST')
                    window.alert("该病例已存在");
                else if (data['state'] == 'RECORDING_EXIST')
                    window.alert("录音文件已存在："+ data['msg'])
                else
                    window.alert("未知错误" + data['msg'])
            },
        })
    })
})
