const whatMattersToWorkersForm = document.getElementById("what-matters-to-workers-filter-form")
const whatMattersToWorkersExportButton = document.getElementById("export-what-matters-to-workers-to-excel")

whatMattersToWorkersExportButton.addEventListener("click",function() {
    const url = `${window.location.href}export-what-matters-stats/`
    exportStatsData(url, whatMattersToWorkersForm)
})