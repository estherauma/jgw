(function () {
  var PRIMARY_ROLE_GROUPS = [
    '58_admin',
    'org_group_admin',
    'org_admin',
    'org_staff',
  ];

  function getCheckboxInputs(container) {
    return Array.from(container.querySelectorAll('input[name="groups"]'));
  }

  function getSelectInput(container) {
    return container.querySelector('select[name="groups"], #id_groups');
  }

  function refreshCustomSelectForField(field) {
    if (!field || !window.refreshUmSelect) {
      return;
    }
    var root = field.closest('[data-um-select]');
    if (root) {
      window.refreshUmSelect(root);
    }
  }

  function getCheckboxGroupName(input) {
    var label = input.closest('label');
    if (!label) {
      return input.value;
    }
    return label.textContent.trim();
  }

  function getOptionGroupName(option) {
    return (option.text || option.value || '').trim();
  }


  function normalizeSelectedRoleNames(selectedNames) {
    var primarySelected = PRIMARY_ROLE_GROUPS.filter(function (roleName) {
      return selectedNames.has(roleName);
    });
    if (primarySelected.length <= 1) {
      return primarySelected[0] || null;
    }
    var chosenRole = primarySelected[0];
    primarySelected.slice(1).forEach(function (roleName) {
      selectedNames.delete(roleName);
    });
    return chosenRole;
  }

  function refreshCheckboxes(container) {
    var inputs = getCheckboxInputs(container);
    if (!inputs.length) {
      return false;
    }
    var selectedNames = new Set(
      inputs.filter(function (input) {
        return input.checked;
      }).map(function (input) {
        return getCheckboxGroupName(input);
      })
    );
    var activePrimaryRole = normalizeSelectedRoleNames(selectedNames);

    inputs.forEach(function (input) {
      var roleName = getCheckboxGroupName(input);
      var isPrimary = PRIMARY_ROLE_GROUPS.indexOf(roleName) !== -1;
      var shouldBeChecked = selectedNames.has(roleName);
      if (input.checked !== shouldBeChecked) {
        input.checked = shouldBeChecked;
      }
      if (!isPrimary) {
        input.disabled = false;
        var nonRoleLabel = input.closest('label');
        if (nonRoleLabel) {
          nonRoleLabel.style.display = '';
        }
        return;
      }
      input.disabled = Boolean(activePrimaryRole && roleName !== activePrimaryRole);
      var label = input.closest('label');
      if (label) {
        label.style.display = '';
      }
    });
    return true;
  }

  function refreshSelect(container) {
    var select = getSelectInput(container);
    if (!select) {
      return false;
    }
    var selectedNames = new Set(
      Array.from(select.selectedOptions).map(function (option) {
        return getOptionGroupName(option);
      })
    );
    var activePrimaryRole = normalizeSelectedRoleNames(selectedNames);

    Array.from(select.options).forEach(function (option) {
      var roleName = getOptionGroupName(option);
      var isPrimary = PRIMARY_ROLE_GROUPS.indexOf(roleName) !== -1;
      var shouldBeSelected = selectedNames.has(roleName);
      option.selected = shouldBeSelected;
      if (!isPrimary) {
        option.disabled = false;
        return;
      }
      option.disabled = Boolean(activePrimaryRole && roleName !== activePrimaryRole);
    });
    refreshCustomSelectForField(select);
    return true;
  }

  function initPrimaryRoleGroupSelector(container) {
    if (!container) {
      return null;
    }

    function refresh() {
      if (refreshCheckboxes(container)) {
        return;
      }
      refreshSelect(container);
    }

    container.addEventListener('change', function (event) {
      var target = event.target;
      if (!target) {
        return;
      }
      if (target.name === 'groups' || target.id === 'id_groups') {
        refresh();
      }
    });

    refresh();
    return { refresh: refresh };
  }

  window.initPrimaryRoleGroupSelector = initPrimaryRoleGroupSelector;

  document.addEventListener('DOMContentLoaded', function () {
    var adminGroupsField = document.getElementById('id_groups');
    if (!adminGroupsField) {
      return;
    }
    initPrimaryRoleGroupSelector(adminGroupsField.form || document);
  });
})();
