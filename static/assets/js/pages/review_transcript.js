function onclickFunction(transcript_file_name){

    console.log(transcript_file_name)
    $.ajax(
        {
            type : "GET",
            url : "/api/v1/profile/play_subject_recording/",
            data : {
                transcript_file_name : transcript_file_name
            },
            success: function (data){
                var audio = document.querySelectorAll("#interview_recording")[0];
                audio.load();
                audio.src = data['recording_dir'];
                const hidden_id = document.querySelectorAll("#hidden_id_field")[0];
                hidden_id.innerHTML = data['subject_id']
            }
        }
    );
    console.log(transcript_file_name)
    $.ajax(
        {
            type: "GET",
            url : "/static/transcript/"+ transcript_file_name.split('/').pop(),
            dataType : "text",
            success: function (data){
                var audio = document.querySelectorAll("#interview_recording")[0];
                var content = "";
                data.split("\n").slice(1, -1).forEach(
                    function(row) {
                        if (!row) {return;}
                        content += "<tr>";
                        var idx = 0;
                        row.split(",", 4).forEach(function(cell) {
                            if (idx == 4){
                                return;
                            } else if (idx == 0 || idx == 1) {
                                content += "<td><a href='javascript:' onclick='snapshot(this)'>" + cell + "</a></td>";
                            } else {
                                content += "<td contenteditable='true'>" + cell + "</td>";
                            }
                            idx += 1;
                        });
                        content += "<td><span class='play feather icon-play-circle'></span></td>";
                        content += "<td><span class='table-remove feather icon-x'></span></td>";
                        content += "<td><span class='table-add feather icon-plus'></span></td>";
                        content += "<td><span class='table-up feather icon-arrow-up'></span></td>";
                        content += "<td><span class='table-down feather icon-arrow-down'></span></td>";
                        content += "</tr>";
                    });
                    document.getElementById("patient_record").innerHTML = content;
                    $('.table-remove').click(function () {
                        $(this).parents('tr').detach();
                    });
                    $('.table-add').click(function () {
                        var $clone = $('#table').find('tr.hide').clone(true).removeClass('hide');
                        $(this).parents('tr').after($clone);
                    });
                    $('.table-down').click(function () {
                        var $row = $(this).parents('tr');
                        $row.next().after($row.get(0));
                    });
                    $('.table-up').click(function () {
                          var $row = $(this).parents('tr');
                          if ($row.index() === 0) return; // Don't go above the header
                          $row.prev().before($row.get(0));
                    });
                    $('.play').click(function () {
                        var table_row = $(this).parents("tr")[0].innerHTML;
                        var time_slot = table_row.match(/(\d)+/g);

                        var startTime = time_slot[0]/1000;
                        var endTime = time_slot[1]/1000;
                        audio.currentTime = startTime;
                        audio.play();
                        audio.ontimeupdate =  (event) => {
                            if (audio.currentTime > endTime) {
                                audio.pause();
                                $("#interview_recording").addClass('audiopause').removeClass('audioplay');
                            }
                        };
                    });
            }
        }
    );
    return false;
};

// https://stackoverflow.com/questions/15547198/export-html-table-to-csv
// Quick and simple export target #table_id into a csv
function download_table_as_csv(table_id, separator=',') {
    // Select rows from table_id
    var rows = document.querySelectorAll('table#' + table_id + ' tr');
    // Construct csv
    var csv = [];
    for (var i = 1; i < rows.length - 1; i++) {
        var row = [], cols = rows[i].querySelectorAll('td');
//        console.log(rows[i].querySelectorAll('select')[0]);
        for (var j = 0; j < cols.length; j++) {
            // Clean innertext to remove multiple spaces and jumpline (break csv)
            var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            // Escape double-quote with double-double-quote
//            data = data.replace(/"/g, '""');
            // Push escaped string
//            console.log(data);
            if (!data) {continue;}
            row.push(data);
        }
        csv.push(row.join(separator));
    }
    var csv_string = csv.join('\n');
    var formFile = new FormData();
    formFile.append("patient_id", document.getElementById("hidden_id_field").innerHTML);
    formFile.append("content", csv_string);

    $.ajax({
        type : "POST",
        url : '/api/v1/files/save/csv',
        data : formFile,
        dataType: "json",
        cache: false,
        processData: false,
        contentType: false,
        success : function(data){
            window.alert(data.msg);
        },
    });
}

$("#save").click(function(e) {
    download_table_as_csv('table');
});

$("#download").click(function(e) {
    var patient_id = document.getElementById("hidden_id_field").innerHTML;
    var csv_path = "/static/transcript/transcript_S" + patient_id + ".csv";
    e.preventDefault();  //stop the browser from following
    window.location.href = csv_path;
});