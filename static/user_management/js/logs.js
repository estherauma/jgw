$(document).ready(function () {
  $("#um-logs-table").DataTable({
    order: [[0, "desc"]],
    pageLength: 10,
    lengthMenu: [10, 25, 50, 100],
    language: {
      search: "Search Logs:",
      emptyTable: "No activity logs found.",
      info: "_START_-_END_ of _TOTAL_ row(s) shown.",
      infoEmpty: "0 of 0 row(s) shown.",
    },
  });

  $("#um-logs-table").on("click", ".um-log-details-btn", function () {
    const logId = $(this).data("log-id");
    const containerBefore = $("#log-before-fields").empty();
    const containerAfter = $("#log-after-fields").empty();

    $("#modal-cards-row").addClass("d-none");
    $("#modal-loader").removeClass("d-none");
    $("#log-details-modal").modal("show");

    $.get(`/user-management/user-activities/${logId}/`, function (data) {
      $("#modal-loader").addClass("d-none");
      $("#modal-cards-row").removeClass("d-none");

      if (!data.ok) {
        containerBefore.html('<div class="text-danger">Failed to load log details.</div>');
        return;
      }

      const template = document.getElementById("field-row-template");
      const fields = Object.keys(data.before);

      if (!fields.length) {
        containerBefore.html('<div class="text-muted">No historic modifications saved.</div>');
        containerAfter.html('<div class="text-muted">No historic modifications saved.</div>');
        return;
      }

      fields.forEach(field => {
        const valBefore = data.before[field];
        const valAfter = data.after[field];

        const rowBefore = $(template.content.cloneNode(true));
        rowBefore.find(".um-detail-label").text(field);
        rowBefore.find(".target-val").text(valBefore);
        containerBefore.append(rowBefore);

        const rowAfter = $(template.content.cloneNode(true));
        rowAfter.find(".um-detail-label").text(field);
        rowAfter.find(".target-val").text(valAfter);

        if (valBefore !== valAfter) {
          rowAfter.find(".target-val").addClass("fw-bold");
        }
        containerAfter.append(rowAfter);
      });
    }).fail(function () {
      $("#modal-loader").addClass("d-none");
      $("#modal-cards-row").removeClass("d-none");
      containerBefore.html('<div class="text-danger">Failed to load log details.</div>');
      containerAfter.html('<div class="text-danger">Failed to load log details.</div>');
    });
  });

  $(document).on("click", ".um-modal-close-btn", function () {
    $("#log-details-modal").modal("hide");
  });

  $(document).on("hidden.bs.modal", "#log-details-modal", function () {
    $("#log-before-fields").empty();
    $("#log-after-fields").empty();
  });
});