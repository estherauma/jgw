function messagingQestionDestinationTable(destinationData) {
    const data = destinationData["data"]
    const labels = destinationData["labels"]
    var tableHead = $('#messaging_question_destination_table thead');
    tableHead.empty()

    var headerRow = $('<tr></tr>');
    headerRow.append($('<th></th>').text('Origin'));
    headerRow.append($('<th></th>').text('Responses'));
    tableHead.append(headerRow);

    var tableBody = $('#messaging_question_destination_table tbody');
    tableBody.empty()

    if (data.length === 0) {
        const tableRow = $('<tr></tr>');
        tableRow.append($('<td></td>').text('No data available').attr('colspan', '2').css('text-align', 'center'));
        tableBody.append(tableRow);
    } else {
        $.each(labels, function (index, label) {
            var tableRow = $('<tr></tr>');
            tableRow.append($(`<td><div class="py-2 d-flex justify-contents-center" style="color: ${COLORS.navyBlue}">${label}</div></td>`));
            tableRow.append($(`<td><div class="py-2 d-flex justify-contents-center" style="color: ${COLORS.navyBlue}">${data[index]}</div></td>`));
            tableBody.append(tableRow);
        });
    }
}