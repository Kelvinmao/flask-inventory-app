$(document).ready(function() {
    $("#upload").click(function(){
        var fileObj = document.getElementById("video_upload").files[0];
        var name = document.getElementById("full_name").value;
        var gender = document.getElementById("gender").value;
        var age = document.getElementById("age").value;
        var visit_date = document.getElementById("created_at").value;
        var survey_type = document.getElementById("survey_type").value;
        var score = document.getElementById("score").value;

        var path = document.getElementById("video_upload").value;

        var file_name_list = path.split('\\')
        var file_name = file_name_list[file_name_list.length-1]

        var formProfile = new FormData();

        formProfile.append("video_file", fileObj);

        formProfile.append("video_file", true)
        formProfile.append("full_name", name);
        formProfile.append("gender", gender);
        formProfile.append("age", age);
        formProfile.append("visit_date", visit_date);
        formProfile.append("survey_type", survey_type);
        formProfile.append("score", score);
        formProfile.append("file_name", file_name)

        $.when(
            $.ajax({
                type : "POST",
                url : '/api/v1/files/videos',
                data : formProfile,
                dataType: "json",
                cache: false,
                processData: false,
                contentType: false,
                success : function(data){
                    if (data['state'] == 'SUCCESS')
                        window.alert("已成功上传视频");
                    else if(data['state'] == 'EXIST')
                        window.alert('视频文件已存在：'+ data['msg'])
                    else
                        window.alert("视频添加失败： "+data['msg'])
                },
            }),
        )
    })
})

function extractFunction(patient_id){
    $.ajax(
        {
            type : "POST",
            url : ""
        }
    )
}