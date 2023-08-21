// export messaging question to excel
const messagingQuestionForm = document.getElementById("messaging-question-filter-form")
const messagingQuestionExportButton = document.getElementById("export-messaging-question-to-excel")

messagingQuestionExportButton.addEventListener("click",function() {
    const url = `${window.location.href}export-messaging-question-stats`
    exportStatsData(url, messagingQuestionForm)
})