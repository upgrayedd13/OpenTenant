import { initCalendar } from "./calendar_core.js";

const calendarEl        = document.getElementById("calendar");
const monthLabel        = document.getElementById("monthLabel");
const adminMain         = document.querySelector(".admin-main");
const eventPaneDate     = document.getElementById("eventPaneDate");
const eventForm         = document.getElementById("eventForm");
const eventPaneClose    = document.getElementById("eventPaneClose");
const eventTitle        = document.getElementById("eventTitle");
const eventAllDay       = document.getElementById("eventAllDay");
const eventStartDate    = document.getElementById("eventStartDate");
const eventEndDate      = document.getElementById("eventEndDate");
const timeRow           = document.getElementById("timeRow");
const eventRepeat       = document.getElementById("eventRepeat");
const weekdayPicker     = document.getElementById("weekdayPicker");
const repeatEndRow      = document.getElementById("repeatEndRow");
const customRruleRow    = document.getElementById("customRruleRow");
const customRrule       = document.getElementById("customRrule");
const exceptionsSection = document.getElementById("exceptionsSection");
const addExceptionBtn   = document.getElementById("addExceptionBtn");
const exceptionList     = document.getElementById("exceptionList");
const eventTimezone     = document.getElementById("eventTimezone");


// Populate with every IANA timezone the browser knows about, defaulting to the
// client's local timezone. Falls back to a small curated list if the Intl API
// doesn't support supportedValuesOf (Firefox < 112, older Safari).
(function populateTimezones() {
    const local = Intl.DateTimeFormat().resolvedOptions().timeZone;
    let zones;
    try {
        zones = Intl.supportedValuesOf("timeZone");
    } catch {
        zones = [
            "UTC",
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "America/Anchorage", "Pacific/Honolulu",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
            "Asia/Dubai", "Asia/Kolkata", "Asia/Shanghai", "Asia/Tokyo",
            "Australia/Sydney", "Pacific/Auckland",
        ];
        if (!zones.includes(local)) {
            zones.unshift(local);
        }
    }
    zones.forEach(tz => {
        const opt = document.createElement("option");
        opt.value = tz;
        opt.textContent = tz.replace(/_/g, " ");
        eventTimezone.appendChild(opt);
    });
    eventTimezone.value = local;
}());

let selectedDateStr = null;
let selectedCell    = null;
let editingEventId  = null;


/////////////////////////////////////////////////////////////////
//////////////////////// Panel Open/Close ///////////////////////
/////////////////////////////////////////////////////////////////
function extractTime(isoString) {
    if (!isoString) return "00:00";
    const date = new Date(isoString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

function extractLocalDate(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function openPanel(dateStr, cell) {
    if (cell && cell === selectedCell) {
        closePanel();
        return;
    }

    updatePanelHeaderAndHighlight(dateStr, cell);

    document.getElementById("eventDeleteActions").innerHTML = "";
    eventForm.reset();
    // Set after reset() so these aren't cleared back to empty
    eventStartDate.value = dateStr;
    eventEndDate.value   = dateStr;
    eventTimezone.value  = Intl.DateTimeFormat().resolvedOptions().timeZone;
    timeRow.classList.remove("hidden");
    weekdayPicker.querySelectorAll(".wd-btn").forEach(b => b.classList.remove("active"));
    clearExceptions();
    syncRepeatUI();
    adminMain.classList.add("panel-open");
    setTimeout(() => eventTitle.focus(), 350);
}

function openPanelForEdit(ev) {
    if (editingEventId === ev.id) {
        closePanel();
        return;
    }

    const startDateStr = extractLocalDate(ev.start_time);
    const endDateStr   = extractLocalDate(ev.end_time);
    
    // Use the helper to open panel and highlight the start date
    openPanel(startDateStr, null);
    
    // Prefill form values
    editingEventId = ev.id;
    eventTitle.value = ev.title || "";
    eventStartDate.value = startDateStr;
    eventEndDate.value = endDateStr;
    eventTimezone.value = ev.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    // Handle All-Day toggle
    const start = new Date(ev.start_time);
    const end = new Date(ev.end_time);
    const isAllDay = start.getHours() === 0 && start.getMinutes() === 0 &&
                     end.getHours() === 23 && end.getMinutes() === 59;
    
    eventAllDay.checked = isAllDay;
    if (isAllDay) {
        timeRow.classList.add("hidden");
    } else {
        timeRow.classList.remove("hidden");
    }
    
    // Always prefill times so they are available if "All-day" is unchecked
    document.getElementById("eventStartTime").value = extractTime(ev.start_time);
    document.getElementById("eventEndTime").value = extractTime(ev.end_time);
    
    document.getElementById("eventLocation").value = ev.location || "";
    document.getElementById("eventDesc").value = ev.description || "";
    
    // Recurrence
    eventRepeat.value = ev.rrule ? (ev.rrule.includes("DAILY") ? "daily" : ev.rrule.includes("WEEKLY") ? "weekly" : ev.rrule.includes("MONTHLY") ? "monthly" : "custom") : "none";
    
    if (eventRepeat.value === "weekly") {
        // This is a simplification; ideally we'd parse the BYDAY part of the RRULE
        // For now, we just trigger the auto-select for the start date
        autoSelectWeekday(startDateStr);
    } else if (eventRepeat.value === "custom") {
        customRrule.value = ev.rrule || "";
    }
    
    syncRepeatUI();
    
    // Handle exceptions
    clearExceptions();
    if (ev.exceptions) {
        ev.exceptions.forEach(ex => {
            const dateStr = extractLocalDate(ex.exception_date);
            addException(dateStr);
        });
    }
    
    // Render delete actions
    const deleteActionsContainer = document.getElementById("eventDeleteActions");
    renderEventDeleteActions(ev, deleteActionsContainer, { 
        closeEventModal: closePanel, 
        renderCalendar: renderCalendar 
    });
    
    setTimeout(() => eventTitle.focus(), 350);
}

function updatePanelHeaderAndHighlight(dateStr, cell) {
    // Update header text
    if (dateStr) {
        const [year, month, day] = dateStr.split("-").map(Number);
        eventPaneDate.textContent = new Date(year, month - 1, day).toLocaleDateString("default", {
            weekday: "long", month: "long", day: "numeric"
        });
    }

    // Update calendar highlight
    if (selectedCell) selectedCell.classList.remove("selected");
    
    if (cell) {
        selectedCell = cell;
        cell.classList.add("selected");
    } else {
        // Try to find the cell in the DOM if only dateStr is provided
        const foundCell = document.querySelector(`.day[data-date="${dateStr}"]`);
        if (foundCell) {
            selectedCell = foundCell;
            foundCell.classList.add("selected");
        } else {
            selectedCell = null;
        }
    }
    selectedDateStr = dateStr;
}

function closePanel() {
    if (selectedCell?.isConnected) selectedCell.classList.remove("selected");
    selectedCell    = null;
    selectedDateStr = null;
    editingEventId  = null;
    adminMain.classList.remove("panel-open");
}

eventPaneClose.onclick = closePanel;

// All-day toggle: hide/show the time inputs
eventAllDay.onchange = () => {
    timeRow.classList.toggle("hidden", eventAllDay.checked);
};

// Keep end date >= start date when start date changes; re-sync weekday pick
eventStartDate.onchange = () => {
    const newDate = eventStartDate.value;
    updatePanelHeaderAndHighlight(newDate, null);

    if (eventEndDate.value && eventEndDate.value < newDate) {
        eventEndDate.value = newDate;
    }

    if (eventRepeat.value === "weekly") {
        autoSelectWeekday(newDate);
    }
};


/////////////////////////////////////////////////////////////////
///////////////////////// Recurrence UI /////////////////////////
/////////////////////////////////////////////////////////////////
function autoSelectWeekday(dateStr) {
    if (!dateStr) return;
    const dayNames = ["SU","MO","TU","WE","TH","FR","SA"];
    const [y, m, d] = dateStr.split("-").map(Number);
    const dayCode = dayNames[new Date(y, m - 1, d).getDay()];
    weekdayPicker.querySelectorAll(".wd-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.day === dayCode);
    });
}

function syncRepeatUI() {
    const mode = eventRepeat.value;
    const repeating = mode !== "none";

    weekdayPicker.classList.toggle("hidden", mode !== "weekly");
    if (mode === "weekly") {
        autoSelectWeekday(eventStartDate.value || selectedDateStr);
    }

    repeatEndRow.classList.toggle("hidden", !repeating);
    customRruleRow.classList.toggle("hidden", mode !== "custom");
    exceptionsSection.classList.toggle("hidden", !repeating);

    syncEndConditionInputs();
}

eventRepeat.onchange = syncRepeatUI;

repeatEndRow.addEventListener("change", e => {
    if (e.target.name === "repeatEnd") syncEndConditionInputs();
});

function syncEndConditionInputs() {
    const selected = repeatEndRow.querySelector('input[name="repeatEnd"]:checked')?.value;
    document.getElementById("repeatUntil").disabled = selected !== "until";
    document.getElementById("repeatCount").disabled = selected !== "count";
}

weekdayPicker.querySelectorAll(".wd-btn").forEach(btn => {
    btn.addEventListener("click", () => btn.classList.toggle("active"));
});


/////////////////////////////////////////////////////////////////
//////////////////////// Exception Dates ////////////////////////
/////////////////////////////////////////////////////////////////
function clearExceptions() {
    exceptionList.innerHTML = "";
}

function addException(dateStr = "") {
    const li = document.createElement("li");
    li.className = "exception-item";

    const input = document.createElement("input");
    input.type  = "date";
    input.value = dateStr;
    input.className = "exception-date-input";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "remove-exception-btn";
    removeBtn.textContent = "×";
    removeBtn.setAttribute("aria-label", "Remove date");
    removeBtn.onclick = () => li.remove();

    li.appendChild(input);
    li.appendChild(removeBtn);
    exceptionList.appendChild(li);
    input.focus();
}

addExceptionBtn.onclick = () => addException();

function getExceptionDates() {
    return Array.from(exceptionList.querySelectorAll(".exception-date-input"))
        .map(inp => inp.value)
        .filter(Boolean);
}


/////////////////////////////////////////////////////////////////
/////////////////////// Build RRULE String //////////////////////
/////////////////////////////////////////////////////////////////
function buildRrule(eventDate) {
    const mode = eventRepeat.value;
    if (mode === "none") {
        return null;
    }

    if (mode === "custom") {
        return customRrule.value.trim() || null;
    }

    const freqMap = { daily: "DAILY", weekly: "WEEKLY", monthly: "MONTHLY" };
    let rule = `RRULE:FREQ=${freqMap[mode]}`;

    if (mode === "weekly") {
        const days = Array.from(weekdayPicker.querySelectorAll(".wd-btn.active"))
            .map(b => b.dataset.day);
        if (days.length === 0) {
            const dayNames = ["SU","MO","TU","WE","TH","FR","SA"];
            const [y, m, d] = eventDate.split("-").map(Number);
            days.push(dayNames[new Date(y, m - 1, d).getDay()]);
        }
        rule += `;BYDAY=${days.join(",")}`;
    }

    const endMode = repeatEndRow.querySelector('input[name="repeatEnd"]:checked')?.value;
    if (endMode === "until") {
        const until = document.getElementById("repeatUntil").value;
        if (until) {
            rule += `;UNTIL=${until.replace(/-/g, "")}T000000Z`;
        }
    } else if (endMode === "count") {
        const count = parseInt(document.getElementById("repeatCount").value, 10);
        if (count > 0) {
            rule += `;COUNT=${count}`;
        }
    }

    return rule;
}


/////////////////////////////////////////////////////////////////
////////////////////////// Submit Form //////////////////////////
/////////////////////////////////////////////////////////////////
function buildDatetime(date, time, fallback = "00:00") {
    return `${date}T${time || fallback}:00`;
}

eventForm.onsubmit = async (e) => {
    e.preventDefault();
    if (!selectedDateStr) return;

    const title        = eventTitle.value.trim();
    const startDateVal = eventStartDate.value || selectedDateStr;
    const endDateVal   = eventEndDate.value   || startDateVal;
    const isAllDay     = eventAllDay.checked;
    const startTime    = document.getElementById("eventStartTime").value;
    const endTime      = document.getElementById("eventEndTime").value;
    const location     = document.getElementById("eventLocation").value.trim() || null;
    const description  = document.getElementById("eventDesc").value.trim() || null;

    if (!title) {
        return;
    }

    if (endDateVal < startDateVal) {
        alert("End date must be on or after the start date.");
        return;
    }

    if (!isAllDay && startTime && endTime && startDateVal === endDateVal && endTime <= startTime) {
        alert("End time must be after start time.");
        return;
    }

    const startDatetime = buildDatetime(startDateVal, isAllDay ? null : startTime, "00:00");
    const endDatetime   = buildDatetime(endDateVal,   isAllDay ? null : endTime,   "23:59");

    const rrule = buildRrule(startDateVal);

    const exceptions = getExceptionDates().map(d => ({
        exception_date: buildDatetime(d, startTime, "00:00"),
        timezone: eventTimezone.value
    }));

    const payload = {
        title,
        start_time:  startDatetime,
        end_time:    endDatetime,
        location,
        description,
        rrule,
        timezone:    eventTimezone.value,
        exceptions:  exceptions.length ? exceptions : null,
    };

    try {
        let res;
        if (editingEventId) {
            res = await fetch(`/api/calendar/events/${editingEventId}`, {
                method:  "PUT",
                headers: { "Content-Type": "application/json" },
                body:    JSON.stringify(payload),
            });
        } else {
            res = await fetch("/api/calendar/events", {
                method:  "POST",
                headers: { "Content-Type": "application/json" },
                body:    JSON.stringify(payload),
            });
        }
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Unknown error");
        closePanel();
        renderCalendar();
    } catch (err) {
        alert(err.message || "Failed to save event");
    }
};


/////////////////////////////////////////////////////////////////
///////////////////////// Delete Event //////////////////////////
/////////////////////////////////////////////////////////////////
function makeDeleteBtn(label, onClick, danger = false) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "event-delete-btn" + (danger ? " event-delete-btn--danger" : "");
    btn.textContent = label;
    btn.onclick = onClick;
    return btn;
}

async function deleteEvent(ev, scope, closeEventModal, renderCalendar) {
    const confirmMsg = scope === "series"
        ? "Delete this event and every occurrence in its series? This cannot be undone."
        : "Delete this one date from the series? This cannot be undone.";
    if (!window.confirm(confirmMsg)) return;

    const payload = { scope };
    if (scope === "single") {
        payload.occurrence_start = new Date(ev.start_time).toISOString();
    }

    try {
        const res  = await fetch(`/api/calendar/events/${ev.id}`, {
            method:  "DELETE",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Unknown error");
        closeEventModal();
        renderCalendar();
    } catch (err) {
        alert(err.message || "Failed to delete event");
    }
}

function renderEventDeleteActions(ev, container, { closeEventModal, renderCalendar }) {
    container.innerHTML = "";
    if (ev.rrule) {
        const note = document.createElement("p");
        note.className = "event-modal-recurring-note";
        note.textContent = "This event repeats.";
        container.appendChild(note);

        const btnRow = document.createElement("div");
        btnRow.className = "event-delete-btn-row";
        btnRow.appendChild(makeDeleteBtn("Delete just this date",  () => deleteEvent(ev, "single", closeEventModal, renderCalendar)));
        btnRow.appendChild(makeDeleteBtn("Delete entire series",   () => deleteEvent(ev, "series", closeEventModal, renderCalendar), true));
        container.appendChild(btnRow);
    } else {
        container.appendChild(makeDeleteBtn("Delete event", () => deleteEvent(ev, "series", closeEventModal, renderCalendar), true));
    }
}


/////////////////////////////////////////////////////////////////
///////////////////////// Calendar Init /////////////////////////
/////////////////////////////////////////////////////////////////
const { renderCalendar, getCurrent } = initCalendar(calendarEl, monthLabel, {
    onDayClick:         (dateStr, cell) => openPanel(dateStr, cell),
    onEventClick:       (ev) => openPanelForEdit(ev),
    renderEventActions: renderEventDeleteActions,
});

document.getElementById("prev").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() - 1);
    closePanel();
    renderCalendar();
};
document.getElementById("next").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() + 1);
    closePanel();
    renderCalendar();
};

renderCalendar();
