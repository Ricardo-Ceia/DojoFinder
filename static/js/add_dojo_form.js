function setupImagePreview(inputId, previewId, containerId) {
    const container = document.getElementById(containerId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    container.addEventListener('click', () => input.click());

    input.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
            reader.readAsDataURL(this.files[0]);
        }
    });
}

setupImagePreview('dojoImage', 'dojoPreview', 'dojoImageContainer');
setupImagePreview('senseiImage', 'senseiPreview', 'senseiImageContainer');
setupImagePreview('athletesImage', 'athletesPreview', 'athletesImageContainer');

function addScheduleEntry() {
    const scheduleEntries = document.getElementById('scheduleEntries');
    const entryIndex = scheduleEntries.children.length;
    const entry = document.createElement('div');
    entry.className = 'schedule-entry';
    entry.innerHTML = `
        <button type="button" class="delete-schedule" onclick="deleteScheduleEntry(this)">×</button>
        
        <label>Day of Week</label>
        <select name="schedules[${entryIndex}][day_of_week]" required>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
            <option value="Thursday">Thursday</option>
            <option value="Friday">Friday</option>
            <option value="Saturday">Saturday</option>
            <option value="Sunday">Sunday</option>
        </select>

        <label>Age Range (e.g., 10-90)</label>
        <input type="text" 
               name="schedules[${entryIndex}][age_range]" 
               placeholder="Age Range (e.g., 10-90)"
               required>

        <label>Start Time</label>
        <input type="time" name="schedules[${entryIndex}][start_time]" required>
        
        <label>End Time</label>
        <input type="time" name="schedules[${entryIndex}][end_time]" required>
        
        <label>Instructor</label>
        <input type="text" name="schedules[${entryIndex}][instructor]" placeholder="Instructor name" required>

        <label>
            <input type="checkbox" name="schedules[${entryIndex}][competition_only]">
            Competition Class Only
        </label>
    `;

    scheduleEntries.appendChild(entry);
}

function deleteScheduleEntry(button) {
    button.parentElement.remove();
}

function formatPrice(input) {
    let value = input.value.replace(/\D/g, "");
    value = parseInt(value);

    if (!isNaN(value)) {
        input.value = value;
    }
}

function closeForm() {
    $('#formOverlay').css('display', 'none');
}