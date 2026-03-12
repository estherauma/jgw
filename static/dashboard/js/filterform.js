/**
 * Client-side validation for GenericFilterForm (core/forms.py).
 * Used on: user overview, messaging question, inline question, what-matters-to-workers.
 * Validates before submit; prevents submit and shows errors when invalid.
 */
(function () {
    'use strict';

    var DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

    function isGenericFilterForm(form) {
        return form && (
            form.querySelector('input[name="start_date"]') ||
            form.querySelector('input[name="end_date"]')
        );
    }

    function getValue(form, name) {
        var el = form.querySelector('[name="' + name + '"]');
        if (!el) return null;
        if (el.type === 'checkbox') return el.checked;
        return (el.value || '').trim();
    }

    function parseDate(str) {
        if (!str || !DATE_REGEX.test(str)) return null;
        var d = new Date(str);
        return isNaN(d.getTime()) ? null : d;
    }

    function clearFieldError(form, fieldName) {
        var wrap = form.querySelector('.form-group [name="' + fieldName + '"]');
        if (wrap) wrap = wrap.closest('.form-group') || wrap.closest('.mb-3');
        if (wrap) {
            var err = wrap.querySelector('.filterform-error');
            if (err) err.remove();
            wrap.classList.remove('is-invalid');
        }
        var input = form.querySelector('[name="' + fieldName + '"]');
        if (input) input.classList.remove('is-invalid');
    }

    function showFieldError(form, fieldName, message) {
        clearFieldError(form, fieldName);
        var input = form.querySelector('[name="' + fieldName + '"]');
        if (!input) return;
        var wrap = input.closest('.form-group') || input.closest('.mb-3') || input.parentElement;
        input.classList.add('is-invalid');
        wrap.classList.add('is-invalid');
        var err = document.createElement('div');
        err.className = 'invalid-feedback filterform-error';
        err.textContent = message;
        wrap.appendChild(err);
    }

    function clearFormErrors(form) {
        ['start_date', 'end_date'].forEach(function (name) {
            clearFieldError(form, name);
        });
        var alert = form.querySelector('.filterform-alert');
        if (alert) alert.remove();
    }

    function validateFilterForm(form) {
        clearFormErrors(form);

        var startVal = getValue(form, 'start_date');
        var endVal = getValue(form, 'end_date');
        var errors = [];

        if (startVal || endVal) {
            if (startVal && !DATE_REGEX.test(startVal)) {
                errors.push({ field: 'start_date', message: 'Please enter a valid start date (YYYY-MM-DD).' });
            }
            if (endVal && !DATE_REGEX.test(endVal)) {
                errors.push({ field: 'end_date', message: 'Please enter a valid end date (YYYY-MM-DD).' });
            }
            if (errors.length === 0 && startVal && endVal) {
                var startDate = parseDate(startVal);
                var endDate = parseDate(endVal);
                if (!startDate) {
                    errors.push({ field: 'start_date', message: 'Please enter a valid start date.' });
                }
                if (!endDate) {
                    errors.push({ field: 'end_date', message: 'Please enter a valid end date.' });
                }
                if (startDate && endDate && startDate > endDate) {
                    var msg = 'End date cannot be earlier than start date.';
                    errors.push({ field: 'end_date', message: msg });
                }
            }
        }

        if (errors.length > 0) {
            errors.forEach(function (e) {
                showFieldError(form, e.field, e.message);
            });
            var firstInput = form.querySelector('.is-invalid');
            if (firstInput) {
                firstInput.focus();
            }
            var summary = document.createElement('div');
            summary.className = 'alert alert-danger filterform-alert mt-2';
            summary.setAttribute('role', 'alert');
            summary.textContent = 'Please correct the errors below before submitting.';
            form.insertBefore(summary, form.firstChild);
            return false;
        }
        return true;
    }

    function onFilterFormSubmit(ev) {
        var form = ev.target;
        if (!isGenericFilterForm(form)) return;

        var submitter = ev.submitter || (ev.nativeEvent && ev.nativeEvent.submitter);
        if (submitter && submitter.getAttribute('name') === 'reset' && submitter.getAttribute('value') === 'true') {
            return;
        }

        if (!validateFilterForm(form)) {
            ev.preventDefault();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        document.addEventListener('submit', onFilterFormSubmit, true);
    }

    window.GenericFilterFormValidation = {
        validate: validateFilterForm,
        isGenericFilterForm: isGenericFilterForm,
        clearFormErrors: clearFormErrors
    };
})();
