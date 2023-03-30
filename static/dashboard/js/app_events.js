function plotChat(labels, values) {
    new Chart(document.getElementById("_" + "{{key}}").getContext("2d"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: values,
        },
        options: {
            barValueSpacing: 50,
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        },
    });
}