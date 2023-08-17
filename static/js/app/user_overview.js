// export messaging question to excel
const userOverviewForm = document.getElementById("user-overview-question-filter-form")
const userOverviewExportButton = document.getElementById("export-user-overview-to-excel")

userOverviewExportButton.addEventListener("click",function() {
    const url = `${window.location.href}export_stats`
    exportStatsData(url, userOverviewForm)
})