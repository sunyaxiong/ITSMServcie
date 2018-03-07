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

$(document).ready(function () {
        var order_id = $("#order_id").html();
        console.log(123123)
        console.log(order_id)
        $.ajax({
            type:"GET",
            url:"http://127.0.0.1:8000/itsm/cloud/order_get/",
            data:{"order_id": order_id},
            success: function (ret) {
                console.log(order_id);
                console.log(ret["status"])
                $("#order_status").html(ret["status"])
            }
        })
})

