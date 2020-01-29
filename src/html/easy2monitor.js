$(document).ready(function () {
    $.get(global["api_endpoint"], function (data, status) {
        $('#json-records').text(JSON.stringify(data, null, 4))
        set_status(data)
        $.dynatableSetup({
            // your global default options here
            dataset: {
                perPageDefault: 50,
                perPageOptions: [10, 20, 50, 100],
                sorts: { 'status': -1 },
            }
        });

        $('#example').dynatable({
            dataset: {
                records: (data)
            }
        });

    });
    setInterval(update_data, 5000);

});

var update_data = function () {
    $.get(global["api_endpoint"], function (data, status) {
        $('#json-records').text(JSON.stringify(data, null, 4))
        data = set_status(data)
        var dynatable = $('#example').data('dynatable');
        dynatable.settings.dataset.originalRecords = data;
        dynatable.process();
    });
}

var set_status = function (data) {
    for (row in data) {
         if (data[row]["uptime_percentage"]) {
             data[row]["uptime_percentage"] = data[row]["uptime_percentage"].toFixed(10) + "%"
         }

        if (data[row]["result"]) {
            data[row]["status"] = '<div class="led-green"></div>'
        } else {
            if (data[row]["last_successfull"] == null) {
                data[row]["last_successfull"] = "Nie"

                data[row]["status"] = '<div class="led-yellow"></div>'
            } else {
                data[row]["status"] = '<div class="led-red"></div>'
            }
        }
        if (data[row]["last_failure"] == null) {
            data[row]["last_failure"] = "Nie"
        }
    }
    return data
}