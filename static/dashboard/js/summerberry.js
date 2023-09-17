$(document).ready(function () {
    $('#summerberry-dash').DataTable({
        columnDefs: [
            {
                targets: [3],
                orderData: [0, 1],
            },
            {
                targets: [3],
                orderData: [1, 0],
            }
        ],
        dom: 'Bfrtipl',
        buttons: [
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    });

    $('#startDate, #endDate').change(function () {
        const startDate = $('#startDate').val();
        let endDate = $('#endDate').val();
        // if enddate is null or empty, set it to today
        if (!endDate) {
            endDate = new Date().toISOString().slice(0, 10);
            $('#endDate').val(endDate);
        }

        // ensure start date is before end date
        if (startDate > endDate) {
            // set end date to start date
            $('#endDate').val(startDate);
            endDate = startDate;
        }
        // pass request to server with these as query params
        $.ajax({
            url: '/summerberry-dashboard',
            type: 'GET',
            data: {
                'startDate': startDate,
                'endDate': endDate
            },
            success: function (response) {
                // console.log(response)
                // $('#summerberry-dash').DataTable().clear().destroy();
                // $('#summerberry-dash').DataTable({
                //     data: response,
                //     // columnDefs: [
                //     //     {
                //     //         targets: [3],
                //     //         orderData: [0, 1],
                //     //     },
                //     //     {
                //     //         targets: [3],
                //     //         orderData: [1, 0],
                //     //     }
                //     // ],
                //     dom: 'Bfrtipl',
                //     buttons: [
                //         'excelHtml5',
                //         'csvHtml5',
                //         'pdfHtml5'
                //     ]
                // });
            }
        });
    });
});
