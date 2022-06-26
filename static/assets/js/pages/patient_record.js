'use strict';
$(document).ready(function() {
    document.getElementById("patient_id").onchange = function () {
        var patient_id = document.getElementById("patient_id").value;

        var audio = document.querySelectorAll("#interview_recording")[0];
        audio.load();
        // TODO: if the patient ID is below 100, we cannot retrieve the corresponding audio file & transcript
        // TODO: e.g., /static/audio/S36.mp3 != /static/audio/S036.mp3
        audio.src = "/static/audio/S" + patient_id + ".mp3";
        var csv_path = "/static/transcript/transcript_S" + patient_id + ".csv";

        $.ajax({
            type: "GET",
            url: csv_path,
            dataType: "text",
            success: function(data) {
                var content = "";

//                console.log(data.split("\n"));
                data.split("\n").slice(1, -1).forEach(
                    function(row) {
                        if (!row) {return;}
                        content += "<tr>";
                        var idx = 0;
//                        console.log(row.split(",").slice(4).join());
                        row.split(",", 4).forEach(function(cell) {
                            if (idx == 4){
                                return;
                            } else if (idx == 0 || idx == 1) {
                                content += "<td><a href='javascript:' onclick='snapshot(this)'>" + cell + "</a></td>";
                            } else {
                                content += "<td contenteditable='true'>" + cell + "</td>";
                            }
//                            console.log(idx);
//                            if (idx == 4){
//                                console.log(cell);
//                                if (cell == 'Doctor'){
//                                    content += "<td class = 'select'><select><option value=“doctor” selected>Doctor</option><option value='patient'>Patient</option></select></td>"
//                                } else {
//                                    content += "<td class = 'select'><select><option value=“doctor”>Doctor</option><option value='patient' selected>Patient</option></select></td>"
//                                }
//                            } else {
//                                content += "<td contenteditable='true'>" + cell + "</td>" ;
//                            }
                            idx += 1;
                        });

                        content += "<td><span class='play feather icon-play-circle'></span></td>";
                        content += "<td><span class='table-remove feather icon-x'></span></td>";
                        content += "<td><span class='table-add feather icon-plus'></span></td>";
                        content += "<td><span class='table-up feather icon-arrow-up'></span></td>";
                        content += "<td><span class='table-down feather icon-arrow-down'></span></td>";
                        content += "</tr>";
//                        console.log(content)
                });
                document.getElementById("patient_record").innerHTML = content;

                // Copy Ninja
                // https://codepen.io/ampourgh/pen/ELJZae
                $('.table-remove').click(function () {
                    $(this).parents('tr').detach();
                });

                $('.table-add').click(function () {
                    var $clone = $('#table').find('tr.hide').clone(true).removeClass('hide');
                    $(this).parents('tr').after($clone);
                });

                $('.table-down').click(function () {
                    var $row = $(this).parents('tr');
//                    console.log($row)
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
//                    console.log(audio.currentTime)
                    audio.play();
                    audio.ontimeupdate =  (event) => {
                        if (audio.currentTime > endTime) {
                            audio.pause();
                            $("#interview_recording").addClass('audiopause').removeClass('audioplay');
                        }
                    };
                });
            }
        });
    };

    $("#save").click(function(e) {
        download_table_as_csv('table');
    });

    $("#download").click(function(e) {
        var patient_id = document.getElementById("patient_id").value;

        var csv_path = "/static/transcript/transcript_S" + patient_id + ".csv";
        e.preventDefault();  //stop the browser from following
        window.location.href = csv_path;
    });
});

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
    formFile.append("patient_id", document.getElementById("patient_id").value);
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

//    // Download it
//    var link = document.createElement('a');
//    link.style.display = 'none';
//    link.setAttribute('target', '_blank');
//    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
//    link.setAttribute('download', filename);
//    document.body.appendChild(link);
//    link.click();
//    document.body.removeChild(link);
}

function snapshot(obj) {
    var audio = document.querySelectorAll("#interview_recording")[0];
    obj.innerHTML = parseInt(audio.currentTime * 1000, 10);
}
