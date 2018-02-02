/**
 * Created by syx on 1/24/18.
 */

function all_conf() {
             $.ajax({
                 type: "POST",
                 url: "http://127.0.0.1:8000/itsm/config_overview/",
                 data: {},
                 success: function(ret) {
                     $('#result0').html(ret[0])
                     $('#result1').html(ret[1])
                     $('#result2').html(ret[2])
                     $('#result3').html(ret[3])

                     console.log(ret)
                 }
             })
         };

function input_enable() {
    $("input").removeAttr("disabled");
    $("select").removeAttr("disabled");
    console.log(123123)
}
