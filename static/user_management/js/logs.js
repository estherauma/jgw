$(document).ready(function () {
  $("#um-logs-table").DataTable({
    order: [[1, "desc"]],
    pageLength: 10,
    lengthMenu: [10, 25, 50, 100],
    language: {
      search: "Search logs:",
      emptyTable: "No activity logs found.",
      info: "_START_-_END_ of _TOTAL_ row(s) shown.",
      infoEmpty: "0 of 0 row(s) shown.",
    },
  });
});
