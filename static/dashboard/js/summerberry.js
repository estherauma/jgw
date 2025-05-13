$(document).ready(function () {
    let columns = [
        { data: 'name', title: 'Worker Name' },
        { data: 'number', title: 'Worker Number' },
        { data: 'startDate', title: 'Start Date' },
        { data: 'registrationDate', title: 'Registration Date' },
        {
            data: 'completedRegistration',
            title: 'Registration',
            render: function (data, type, row) {
                if (data == 1) {
                    return ' <span class="badge bg-success">Yes</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },
        {
            data: 'completedInduction',
            title: 'Induction',
            render: function (data, type, row) {
                if (data == "Completed") {
                    return ' <span class="badge bg-success">Completed</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },
        {
            data: 'contractSigned',
            title: 'Contract Signed',
            render: function (data, type, row) {
                if (data == 1) {
                    return ' <span class="badge bg-success">Yes</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },
        {
            data: 'workerDirectiveSigned',
            title: 'Worker Directive Signed',
            render: function (data, type, row) {
                if (data == 'Yes') {
                    return ' <span class="badge bg-success">Yes</span>';
                } else if (data == 'No') {
                    return '<span class="badge bg-danger">No</span>';
                } else {
                    return '<span class="badge bg-warning">None</span>';
                }
            }
        },
        {
            data: 'hygieneSigned',
            title: 'Hygiene',
            render: function (data, type, row) {
                if (data == 1) {
                    return ' <span class="badge bg-success">Yes</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },
        {
            data: 'medicalSigned',
            title: 'Medical',
            render: function (data, type, row) {
                if (data == 1) {
                    return ' <span class="badge bg-success">Yes</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },
        {
            data: 'hasAllergies',
            title: 'Has allergies',
            render: function (data, type, row) {
                if (data == 1) {
                    return ' <span class="badge bg-success">Yes</span>';
                } else if (data == null || data == undefined) {
                    return ' <span class="badge bg-warning">Not specified</span>';
                } else {
                    return '<span class="badge bg-danger">No</span>';
                }
            }
        },

    ]
    $('#summerberry-dash').DataTable({
        ajax: '/summerberry-data',
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
        columns: columns,
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
            url: '/summerberry-data',
            type: 'GET',
            data: {
                'startDate': startDate,
                'endDate': endDate
            },
            success: function (response) {
                $('#summerberry-dash').DataTable().clear().destroy();
                $('#summerberry-dash').DataTable({
                    data: response.data,
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
                    columns: columns,
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
