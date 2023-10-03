// export inline question to excel
const inlineQuestionForm = document.getElementById("inline-question-filter-form")
const inlineQuestionExportButton = document.getElementById("export-inline-question-to-excel")

exportStatsFn(inlineQuestionExportButton, `${window.location.href}export-inline-question-stats`)

