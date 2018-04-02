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

function event_upgrade() {

    var username=$('#upgradeUsername').val();
    var event_id=$("#event_id").val();

    $.ajax({
        type: "GET",
        url: "/itsm/events/event_upgrade/",
        data: {
            "username": username,
            "event_id": event_id
        },
        success: function (ret) {
            // console.log(ret)
            window.location.href=window.location.pathname;
        }
    })
}

function issue_upgrade() {

    var username=$('#upgradeUsername').val();
    var issue_id=$("#issue_id").val();

    $.ajax({
        type: "GET",
        url: "/itsm/issue/upgrade/",
        data: {
            "username": username,
            "issue_id": issue_id
        },
        success: function (ret) {
            // console.log(ret)
            window.location.href=window.location.pathname;
        }
    })
}

function change_reject() {

    var change_id=$("#id").val();

    $.ajax({
        type: "GET",
        url: "/itsm/change/reject/",
        data: {
            "id": change_id
        },
        success: function (ret) {
            // console.log(ret)
            window.location.href=window.location.pathname;
        }
    })
}


$(document).ready(function () {
        var order_id = $("#order_id").html();
        $.ajax({
            type:"GET",
            url:"/itsm/cloud/order_get/",
            data:{"order_id": order_id},
            success: function (ret) {
                $("#order_status").html(ret["status"])
            }
        })
})

