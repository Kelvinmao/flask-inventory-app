$(document).ready(
    function(){
        $.when(
            $.ajax(
                {
                    type:'GET',
                    url:'/api/v1/stats/subjects',
                    success: function(data){
                        document.getElementById("total_samples").innerHTML = '<i class=\"feather icon-arrow-up text-c-green f-30 m-r-10\"></i>' + data['stats']['total_subjects']
                        document.getElementById("new_cases").innerHTML = '<i class=\"feather icon-arrow-up text-c-green f-30 m-r-10\"></i>' + data['stats']['new_cases']
                    }
                }
            ),

            $.ajax(
                {
                    type:'GET',
                    url:'/api/v1/stats/subjectsInfo',
                    success:function(data){
                        var fields = ['full_name', 'created_at', 'age', 'score', 'id']
                        var tbody = document.querySelector('tbody');

                        for (var i = 0; i < data['result'].length; i++) {
                            var tr = document.createElement('tr')
                            tr.classList.add('unread')
                            tr.setAttribute('id', 'subject_' + i)
                            tbody.appendChild(tr);
                            var td_ava= document.createElement('td')
                            tr.appendChild(td_ava)
                            var img = document.createElement('img')
                            img.classList.add('rounded-circle')
                            if (data['result'][i]['gender'] == '\u7537')
                                img.src = "/static/assets/images/user/avatar-2.jpg"
                            else
                                img.src = "/static/assets/images/user/avatar-1.jpg"
                            img.alt = 'activity-user'
                            img.style = 'width:40px;'
                            td_ava.appendChild(img)

                            for (var j = 0; j < fields.length; j++) {
                                if (fields[j] == 'full_name'){
                                    var td_name = document.createElement('td')
                                    td_name.setAttribute('id', 'name_'+i)
                                    tr.appendChild(td_name)
                                    var h_name = document.createElement('a')
                                    h_name.classList.add('mb-1')
                                    h_name.setAttribute('id', 'name_'+i)
                                    h_name.setAttribute('href', '/api/v1/profile/subject_info?full_name='+data['result'][i][fields[j]])
                                    h_name.innerHTML = data['result'][i][fields[j]]
                                    td_name.appendChild(h_name)

                                    var p_ques = document.createElement('p')
                                    p_ques.classList.add('m-0')
                                    p_ques.innerHTML = data['result'][i]['survey_type'] + ' ' + data['result'][i]['score'] + '分'
                                    td_name.appendChild(p_ques)
                                }
                                if (fields[j] == 'created_at') {
                                    var td_date = document.createElement('td')
                                    td_date.setAttribute('id', 'date_'+i)
                                    tr.appendChild(td_date)
                                    var h_date = document.createElement('h6')
                                    h_date.classList.add('text_muted')
                                    h_date.setAttribute('id', 'date_'+i)

                                    var i_tmp = document.createElement('i')

//                                    i_tmp.classList.add('fas', 'fa-circle', 'text-c-green', 'f-10', 'm-r-15')
//                                    h_date.appendChild(i_tmp)
//                                     console.log(new Date(data['result'][i]['created_at']).toLocaleDateString())
                                    // console.log(DateTime.fromFormat(data['result'][i]['created_at'], "yyyy-MM-dd HH:mm:ss").toDate())
                                    h_date.innerHTML = '<i class="fas fa-circle text-c-green f-10 m-r-15"></i>' +
                                                    new Date(data['result'][i]['created_at']).toLocaleDateString()
                                    td_date.appendChild(h_date)
                                }


                            }

                            var td_check_video_audio = document.createElement('td')
                            td_check_video_audio.setAttribute('id', 'subject_'+i)
                            tr.appendChild(td_check_video_audio)

                            var a_recording = document.createElement('a')
                            var a_video = document.createElement('a')
                            a_recording.classList.add('label', 'theme-bg2', 'text-white', 'f-12')
                            a_video.classList.add('label', 'theme-bg', 'text-white', 'f-12')
                            if (data['result'][i]['recording_dir']){
                                a_recording.setAttribute('href', data['result'][i]['recording_dir'].split('/').slice(-3, ).join('/'))
                                a_recording.innerHTML = 'Audio'
                                td_check_video_audio.appendChild(a_recording)
                            }

                            if (data['result'][i]['video_dir']){
                                a_video.setAttribute('href', data['result'][i]['video_dir'].split('/').slice(-3, ).join('/'))
                                a_video.innerHTML = 'Video'
                                td_check_video_audio.appendChild(a_video)
                            }
                        }
                    }
                }
            )
        )
    }
)

//<tr class="unread">
//                                                    <td><img class="rounded-circle" style="width:40px;" src="/static/assets/images/user/avatar-2.jpg" alt="activity-user"></td>
//                                                    <td>
//                                                        <h6 class="mb-1">Albert Andersen</h6>
//                                                        <p class="m-0">Lorem Ipsum is simply dummy…</p>
//                                                    </td>
//                                                    <td>
//                                                        <h6 class="text-muted"><i class="fas fa-circle text-c-green f-10 m-r-15"></i>21 July 12:56</h6>
//                                                    </td>
//                                                    <td><a href="#!" class="label theme-bg2 text-white f-12">Reject</a><a href="#!" class="label theme-bg text-white f-12">Approve</a></td>
//                                                </tr>