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
        const endDate = $('#endDate').val();
        // pass request to server with these as query params
        $.ajax({
            url: '/dashboard/summeryberry',
            type: 'GET',
            data: {
                'startDate': startDate,
                'endDate': endDate
            },
            success: function (data) {
                $('#summerberry-dash').DataTable().clear().destroy();
                $('#summerberry-dash').DataTable({
                    data: data,
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
            }
        });
    });
});
