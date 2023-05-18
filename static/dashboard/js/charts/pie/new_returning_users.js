function newUsersAndReturningUsersChart(newUsersAndReturningUsersData) {
    const labels = newUsersAndReturningUsersData["labels"]
    const  data = newUsersAndReturningUsersData["data"]
    var ctx = document.getElementById('new-and-returning-users-chart').getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'New Users Vs Returning Users',
                data: data,
                backgroundColor: [COLORS.skyBlue, COLORS.appleGreen],
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}