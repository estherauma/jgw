// export inline question to excel
const inlineQuestionForm = document.getElementById("inline-question-filter-form")
const inlineQuestionExportButton = document.getElementById("export-inline-question-to-excel")

inlineQuestionExportButton.addEventListener("click",function() {
    const url = `${window.location.href}export_inline_question_stats`
    exportStatsData(url, inlineQuestionForm)
})