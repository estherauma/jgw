(function ($) {
  $(function () {
    var logsTable = $("#um-logs-table");
    if (!logsTable.length || typeof $.fn.DataTable !== "function") return;

    logsTable.DataTable({
      pageLength: 10,
      lengthChange: false,
      order: [[1, "desc"]],
      language: {
        emptyTable: "No activity logs found.",
      },
    });
  });
})(jQuery);
