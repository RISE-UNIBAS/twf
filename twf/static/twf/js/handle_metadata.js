function editMetadata(base_key, obj_type, obj_id, key) {
    let span = document.getElementById('metadata-value-' + key);
    let oldValue = span.innerText;

    span.innerHTML = `<input type="text" id="edit-${key}" value="${oldValue}"> 
                      <button onclick="saveMetadata('${base_key}', '${obj_type}', ${obj_id}, '${key}')">Save</button>
                      <button onclick="cancelEdit('metadata-value-${key}', '${oldValue}')">Cancel</button>`;
}

function cancelEdit(elementId, originalValue) {
    document.getElementById(elementId).innerHTML = originalValue;
}

function saveMetadata(base_key, obj_type, obj_id, key) {
    let newValue = document.getElementById('edit-' + key).value;

    fetch(`/metadata/update/${obj_type}/${obj_id}/${base_key}/`, {  // Replace with your actual Django view
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ key: key, value: newValue })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('metadata-value-' + key).innerHTML = data.new_value;
    });
}

function deleteMetadata(base_key, obj_type, obj_id, key) {
    if (confirm('Are you sure you want to delete this metadata entry?')) {
        fetch(`/metadata/delete/${obj_type}/${obj_id}/${base_key}/`, {  // Replace with your actual Django view
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ key: key })
        })
        .then(response => response.json())
        .then(() => {
            document.getElementById('metadata-' + key).remove();
        });
    }
}

function getCsrfToken() {
    let csrfToken = null;
    document.cookie.split(";").forEach(cookie => {
        let [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            csrfToken = value;
        }
    });
    console.log("CSRF Token:", csrfToken);
    return csrfToken;
}

