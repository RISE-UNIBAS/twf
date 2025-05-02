document.addEventListener('DOMContentLoaded', function () {
    const editor = document.getElementById('export-config-editor');
    const hiddenConfigField = document.getElementsByName('config')[0];
    const exportTypeSelect = document.getElementById('id_export_type');

    let currentEditingField = null; // Will hold { sectionName, fieldDiv } info

    exportTypeSelect.setAttribute('data-prev-value', exportTypeSelect.value);

    const exportTypeSections = {
        'document': ['general', 'documents', 'pages'],
        'page': ['general', 'pages'],
        'collection': ['general', 'items'],
        'dictionary': ['general', 'entries'],
        'tag_report': ['general', 'tags'],
    };

    function capitalize(s) {
        return s.charAt(0).toUpperCase() + s.slice(1);
    }

    function initializeEditor(initialData = null, selectedExportType = 'document') {

        // Prevent showing sections if no valid export type selected
        if (!selectedExportType || selectedExportType === '--------') {
            editor.innerHTML = '';
            return;
        }

        editor.innerHTML = '';  // Clear current editor contents

        const sections = exportTypeSections[selectedExportType] || ['general'];

        sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.classList.add('card', 'mb-3');
            sectionDiv.innerHTML = `
                <div class="card-header">
                    <strong>${capitalize(section)} Section</strong>
                </div>
                <div class="card-body" id="${section}-fields">
                </div>
                <div class="card-footer text-end">
                    <button type="button" class="btn btn-sm btn-danger me-2" onclick="resetSection('${section}')">Reset Section</button>
                    <button type="button" class="btn btn-sm btn-primary" onclick="addField('${section}')">Add Field</button>
                </div>
            `;
            editor.appendChild(sectionDiv);

            // Load existing fields if any
            if (initialData && initialData[section]) {
                Object.entries(initialData[section]).forEach(([exportKey, details]) => {
                    addField(section, exportKey, details.source_type, details.source);
                });
            }
        });
    }

    function askDangerConfirmation(message, onConfirm) {
        // Set modal body
        document.querySelector('#confirmDangerModal .modal-body').textContent = message;

        // Get the modal
        const dangerModal = new bootstrap.Modal(document.getElementById('confirmDangerModal'));
        dangerModal.show();

        // Replace the Confirm button handlers
        const confirmButton = document.getElementById('confirmDangerActionButton');
        confirmButton.replaceWith(confirmButton.cloneNode(true)); // clear old listeners
        const newConfirmButton = document.getElementById('confirmDangerActionButton');

        newConfirmButton.addEventListener('click', function () {
            dangerModal.hide();
            if (onConfirm) {
                onConfirm();
            }
        });
    }

    function updateFieldPreview(fieldDiv) {
        const keyInput = fieldDiv.querySelector('input[type="text"]');
        const preview = fieldDiv.querySelector('.source-preview');
        const sourceDataInput = fieldDiv.querySelector('.source-data');

        let valid = true;
        let summary = '';

        if (!keyInput || !sourceDataInput || !preview) return;

        const exportKey = keyInput.value.trim();
        if (!exportKey) {
            valid = false;
        }

        try {
            const sourceInfo = JSON.parse(sourceDataInput.value);
            const type = sourceInfo.source_type;
            const source = sourceInfo.source;
            const fallback = sourceInfo.fallback;

            if (!type || !source) {
                valid = false;
            }

            if (type === 'static') {
                summary = `static: "${source}"`;
            } else if (type === 'metadata') {
                summary = `metadata: ${source}`;
            } else if (type === 'db_field') {
                summary = `db: ${source}`;
            } else if (type === 'text_content') {
                summary = `text: ${source}`;
            } else if (type === 'special') {
                summary = `special: ${source}`;
            }

            if (fallback) {
                summary += ` (fallback: "${fallback}")`;
            }
        } catch (e) {
            valid = false;
            summary = 'Invalid source data';
        }

        preview.textContent = summary || 'No configuration';

        if (valid) {
            fieldDiv.classList.remove('border', 'border-danger');
        } else {
            fieldDiv.classList.add('border', 'border-danger');
        }
    }


    function renderSourceOptions(section, sourceType, selectedSource) {
        const container = document.getElementById('source-options-container');
        container.innerHTML = '';

        if (sourceType === 'db_field') {
            const select = document.createElement('select');
            select.classList.add('form-select', 'mb-2');

            const fields = dbFields[section] || [];
            fields.forEach(fieldTuple => {
                const [fieldName, label, sampleValue] = fieldTuple;

                const option = document.createElement('option');
                option.value = fieldName;
                option.textContent = label;

                if (fieldName === selectedSource) {
                    option.selected = true;
                }
                select.appendChild(option);
            });

            container.appendChild(select);

            // Sample value container
            const sampleDiv = document.createElement('div');
            sampleDiv.classList.add('mt-2', 'text-muted');
            sampleDiv.id = 'sample-value-display';
            container.appendChild(sampleDiv);

            function updateSampleValue(selectedField) {
                const fields = dbFields[section] || [];
                const match = fields.find(([fieldName]) => fieldName === selectedField);
                if (match) {
                    sampleDiv.textContent = `Sample: ${match[2] || 'No sample available'}`;
                } else {
                    sampleDiv.textContent = '';
                }
            }

            // Initial
            updateSampleValue(select.value);

            select.addEventListener('change', function () {
                updateSampleValue(this.value);
            });
        }
        else if (sourceType === 'metadata') {
            container.innerHTML = '';

            let selectedService = null;
            let selectedKey = null;

            if (selectedSource && selectedSource.includes('.')) {
                [selectedService, selectedKey] = selectedSource.split('.', 2);
            }

            const isPageSection = (section === 'pages');
            const fields = isPageSection ? metadataPageFields : metadataDocFields;
            const services = Object.keys(fields);

            if (!selectedService && services.length > 0) {
                selectedService = services[0];
            }

            // Create Service Select
            const serviceSelect = document.createElement('select');
            serviceSelect.classList.add('form-select', 'mb-2');
            services.forEach(service => {
                const option = document.createElement('option');
                option.value = service;
                option.textContent = service;
                if (service === selectedService) {
                    option.selected = true;
                }
                serviceSelect.appendChild(option);
            });
            container.appendChild(serviceSelect);

            // Key Select/Input container
            const keySelectOrInputDiv = document.createElement('div');
            keySelectOrInputDiv.id = 'metadata-key-container';
            container.appendChild(keySelectOrInputDiv);

            // Sample display
            const sampleDiv = document.createElement('div');
            sampleDiv.classList.add('mt-2', 'text-muted');
            sampleDiv.id = 'sample-value-display';
            container.appendChild(sampleDiv);

            function renderKeySelect(service) {
                keySelectOrInputDiv.innerHTML = '';

                if (fields[service]) {
                    const keySelect = document.createElement('select');
                    keySelect.classList.add('form-select');

                    fields[service].forEach(([keyName, label, sampleValue]) => {
                        const option = document.createElement('option');
                        option.value = keyName;
                        option.textContent = label;

                        if (keyName === selectedKey) {
                            option.selected = true;
                        }
                        keySelect.appendChild(option);
                    });

                    keySelectOrInputDiv.appendChild(keySelect);

                    function updateSampleValue(selectedKeyName) {
                        const keys = fields[service] || [];
                        const match = keys.find(([keyName]) => keyName === selectedKeyName);
                        if (match) {
                            sampleDiv.textContent = `Sample: ${match[2] || 'No sample available'}`;
                        } else {
                            sampleDiv.textContent = '';
                        }
                    }

                    updateSampleValue(keySelect.value);

                    keySelect.addEventListener('change', function () {
                        updateSampleValue(this.value);
                    });

                } else {
                    const keyInput = document.createElement('input');
                    keyInput.type = 'text';
                    keyInput.classList.add('form-control');
                    keyInput.placeholder = 'Metadata Key';
                    keyInput.value = selectedKey || '';
                    keySelectOrInputDiv.appendChild(keyInput);

                    sampleDiv.textContent = 'No known keys for this service.';
                }
            }

            renderKeySelect(selectedService);

            serviceSelect.addEventListener('change', function () {
                renderKeySelect(this.value);
            });
        }
        else if (sourceType === 'static') {
            const input = document.createElement('input');
            input.type = 'text';
            input.classList.add('form-control');
            input.placeholder = 'Static Value';
            input.value = selectedSource || '';
            container.appendChild(input);
        }
        else if (sourceType === 'text_content') {
            const select = document.createElement('select');
            select.classList.add('form-select');

            const textOptions = {
                general: [],
                documents: ['Document Text', 'List of Page Texts', 'List of Lists of Annotations'],
                pages: ['Page Text', 'List of Annotations']
            };

            const values = textOptions[section] || [];

            values.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                if (opt === selectedSource) {
                    option.selected = true;
                }
                select.appendChild(option);
            });

          container.appendChild(select);
        }
        else if (sourceType === 'special') {
            const select = document.createElement('select');
            select.classList.add('form-select');

            let fields;
            if (section === 'general') {
                const exportType = exportTypeSelect.value;
                if (exportType === 'collection') {
                    fields = specialFields['general_collection'] || [];
                } else {
                    fields = specialFields['general_project'] || [];
                }
            } else {
                fields = specialFields[section] || [];
            }
            fields.forEach(fieldTuple => {
                const [field, label] = Array.isArray(fieldTuple) ? fieldTuple : [fieldTuple, fieldTuple];
                const option = document.createElement('option');
                option.value = field;
                option.textContent = label;
                if (field === selectedSource) {
                   option.selected = true;
                }
                select.appendChild(option);
            });

            container.appendChild(select);
        }
    }

    window.openSourceEditor = function(section, buttonElement) {
        const fieldDiv = buttonElement.closest('.row');

        const sourceDataInput = fieldDiv.querySelector('.source-data');
        let sourceType = 'db_field';
        let source = '';
        let fallback = '';

        if (sourceDataInput && sourceDataInput.value) {
            try {
                const sourceInfo = JSON.parse(sourceDataInput.value);
                sourceType = sourceInfo.source_type || 'db_field';
                source = sourceInfo.source || '';
                fallback = sourceInfo.fallback || '';
            } catch (e) {
                console.error('Invalid source-data JSON:', e);
            }
        }

        const sourceTypeSelect = document.getElementById('source-type');
        const fallbackInput = document.getElementById('fallback-value');

        sourceTypeSelect.value = sourceType;
        fallbackInput.value = fallback;

        const sectionLabels = {
          general: "Project",
          documents: "Document",
          pages: "Page",
          items: "Collection Item",
          entries: "Dictionary Entry",
          tags: "Tag"
        };

        const sectionName = sectionLabels[section] || section.charAt(0).toUpperCase() + section.slice(1);
        document.getElementById('sourceEditorModalLabel').textContent = `Edit ${sectionName} Source`;

        const keyInput = fieldDiv.querySelector('input[type="text"]');
        const keyName = keyInput ? keyInput.value.trim() : '';
        document.getElementById('source-key-display').textContent = keyName ? `Export Key: "${keyName}"` : '';

        const disallowedTypes = [];
        if (section === 'general') {
          disallowedTypes.push('metadata', 'text_content');
        }

        Array.from(sourceTypeSelect.options).forEach(option => {
          option.disabled = disallowedTypes.includes(option.value);
        });

        // Set up dynamic source options initially
        renderSourceOptions(section, sourceType, source);

        // --- VERY IMPORTANT: Attach change listener dynamically ---
        if (sourceTypeSelect._changeListener) {
            sourceTypeSelect.removeEventListener('change', sourceTypeSelect._changeListener);
        }

        const changeListener = function() {
            renderSourceOptions(section, this.value, '');
        };

        sourceTypeSelect.addEventListener('change', changeListener);
        sourceTypeSelect._changeListener = changeListener;
        // ----------------------------------------------------------

        currentEditingField = { section, fieldDiv };

        const modal = new bootstrap.Modal(document.getElementById('sourceEditorModal'));
        modal.show();
    };



    window.addField = function(section, exportKey = '', sourceType = '', source = '', fallback = '') {
        const container = document.getElementById(`${section}-fields`);
        const fieldDiv = document.createElement('div');
        fieldDiv.classList.add('row', 'mb-2');

        const sourceInfo = {
            source_type: sourceType,
            source: source,
            fallback: fallback
        };

        fieldDiv.innerHTML = `
            <div class="col-3">
                <input type="text" class="form-control" placeholder="Export Key" value="${exportKey}">
            </div>
            <div class="col-3">
                <button type="button" class="btn btn-outline-secondary btn-sm" onclick="openSourceEditor('${section}', this)">Edit Source</button>
                <input type="hidden" class="source-data" value='${JSON.stringify({
                    source_type: sourceType,
                    source: source,
                    fallback: fallback
                })}'>
                <div class="source-preview small text-muted mt-1"></div>
            </div>
            <div class="col-2">
                <button type="button" class="btn btn-danger btn-sm" onclick="this.parentElement.parentElement.remove()">X</button>
            </div>
        `;

        container.appendChild(fieldDiv);
        updateFieldPreview(fieldDiv);

        const keyInput = fieldDiv.querySelector('input[type="text"]');
            keyInput.addEventListener('input', () => {
                updateFieldPreview(fieldDiv);
        });
    }


    window.resetSection = function(section) {
        const container = document.getElementById(`${section}-fields`);
        if (container) {
            askDangerConfirmation(`Are you sure you want to reset all fields in the "${capitalize(section)}" section?`, function () {
                container.innerHTML = '';
            });
        }
    }

    document.getElementById('save-source-button').addEventListener('click', function () {
        if (!currentEditingField) return;

        const sourceType = document.getElementById('source-type').value;
        let source = '';

        const sourceContainer = document.getElementById('source-options-container');
        if (sourceType === 'metadata') {
            const serviceSelect = sourceContainer.querySelector('select');
            const keyInputOrSelect = sourceContainer.querySelector('#metadata-key-container select, #metadata-key-container input');

            const service = serviceSelect ? serviceSelect.value.trim() : '';
            const key = keyInputOrSelect ? keyInputOrSelect.value.trim() : '';

            if (service && key) {
                source = `${service}.${key}`;
            }
        } else {
            const sourceInput = sourceContainer.querySelector('input, select');
            source = sourceInput ? sourceInput.value.trim() : '';
        }

        const fallback = document.getElementById('fallback-value').value.trim();

        const sourceData = {
            source_type: sourceType,
            source: source,
            fallback: fallback
        };

        const sourceDataInput = currentEditingField.fieldDiv.querySelector('.source-data');
        sourceDataInput.value = JSON.stringify(sourceData);
        updateFieldPreview(currentEditingField.fieldDiv);

        const modal = bootstrap.Modal.getInstance(document.getElementById('sourceEditorModal'));
        modal.hide();
    });


    const form = document.getElementById('export-configuration-form');
    if (!form) {
        console.error('Form not found — check placement of script or crispy output.');
    } else {
        console.log("Form found5", form);
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            console.log("SAVE FORM");

            const hiddenConfigField = form.querySelector('input[name="config"]');
            if (!hiddenConfigField) {
                console.error('Missing hidden config input!');
                return;
            }

            const result = {};
            const currentSections = exportTypeSections[exportTypeSelect.value] || ['general'];

            currentSections.forEach(section => {
                const sectionFields = document.getElementById(`${section}-fields`)?.querySelectorAll('.row') || [];
                if (sectionFields.length > 0) {
                    result[section] = {};
                    sectionFields.forEach(field => {
                        const keyInput = field.querySelector('input[type="text"]');
                        const sourceDataInput = field.querySelector('.source-data');

                        if (!keyInput || !sourceDataInput) return;

                        const exportKey = keyInput.value.trim();
                        let sourceInfo = {};

                        try {
                            sourceInfo = JSON.parse(sourceDataInput.value);
                        } catch (e) {
                            console.error('Invalid source-data JSON:', e);
                            return;
                        }

                        if (exportKey && sourceInfo.source_type && sourceInfo.source) {
                            result[section][exportKey] = sourceInfo;
                        }
                    });
                }
            });

            hiddenConfigField.value = JSON.stringify(result);
            form.submit();
        });
    }


    // Listen for export_type changes
    exportTypeSelect.addEventListener('change', function () {
        const currentSections = exportTypeSections[this.getAttribute('data-prev-value')] || ['general'];
        let hasExistingFields = false;

        // Check if any fields exist
        currentSections.forEach(section => {
            const sectionFields = document.getElementById(`${section}-fields`);
            if (sectionFields && sectionFields.querySelector('.row')) {
                hasExistingFields = true;
            }
        });

        if (hasExistingFields) {
            askDangerConfirmation(
                "You have unsaved field mappings. Changing the export type will clear them. Continue?",
                () => {
                    initializeEditor(null, this.value);
                    this.setAttribute('data-prev-value', this.value);
                }
            );
        } else {
            initializeEditor(null, this.value);
            this.setAttribute('data-prev-value', this.value);
        }
    });

    // Load existing config if available
    try {
        const initialData = JSON.parse(hiddenConfigField.value);
        initializeEditor(initialData, exportTypeSelect.value);
    } catch (e) {
        initializeEditor(null, exportTypeSelect.value);
    }


});
