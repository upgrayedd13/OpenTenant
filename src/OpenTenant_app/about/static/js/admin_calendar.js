import { initCalendar } from "./calendar_core.js";

const calendarEl     = document.getElementById("calendar");
const monthLabel     = document.getElementById("monthLabel");
const adminMain      = document.querySelector(".admin-main");
const eventPaneDate  = document.getElementById("eventPaneDate");
const eventForm      = document.getElementById("eventForm");
const eventPaneClose = document.getElementById("eventPaneClose");
const eventTitle     = document.getElementById("eventTitle");
const eventRepeat    = document.getElementById("eventRepeat");
const weekdayPicker  = document.getElementById("weekdayPicker");
const repeatEndRow   = document.getElementById("repeatEndRow");
const customRruleRow = document.getElementById("customRruleRow");
const customRrule    = document.getElementById("customRrule");
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
        // Fallback: common zones only
        zones = [
            "UTC",
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "America/Anchorage", "Pacific/Honolulu",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
            "Asia/Dubai", "Asia/Kolkata", "Asia/Shanghai", "Asia/Tokyo",
            "Australia/Sydney", "Pacific/Auckland",
        ];
        if (!zones.includes(local)) zones.unshift(local);
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


/////////////////////////////////////////////////////////////////
//////////////////////// Panel Open/Close ///////////////////////
/////////////////////////////////////////////////////////////////
function openPanel(dateStr, cell) {
    if (selectedCell) {
        selectedCell.classList.remove("selected");
    }
    selectedDateStr = dateStr;
    selectedCell    = cell;
    cell.classList.add("selected");

    const [year, month, day] = dateStr.split("-").map(Number);
    eventPaneDate.textContent = new Date(year, month - 1, day).toLocaleDateString("default", {
        weekday: "long", month: "long", day: "numeric"
    });

    eventForm.reset();
    eventTimezone.value = Intl.DateTimeFormat().resolvedOptions().timeZone;
    clearExceptions();
    syncRepeatUI();
    adminMain.classList.add("panel-open");
    setTimeout(() => eventTitle.focus(), 350);
}

function closePanel() {
    if (selectedCell?.isConnected) selectedCell.classList.remove("selected");
    selectedCell    = null;
    selectedDateStr = null;
    adminMain.classList.remove("panel-open");
}

eventPaneClose.onclick = closePanel;


/////////////////////////////////////////////////////////////////
///////////////////////// Recurrence UI /////////////////////////
/////////////////////////////////////////////////////////////////
function syncRepeatUI() {
    const mode = eventRepeat.value;
    const repeating = mode !== "none";

    weekdayPicker.classList.toggle("hidden", mode !== "weekly");
    repeatEndRow.classList.toggle("hidden", !repeating);
    customRruleRow.classList.toggle("hidden", mode !== "custom");
    exceptionsSection.classList.toggle("hidden", !repeating);

    // keep end-condition inputs in sync with selected radio
    syncEndConditionInputs();
}

eventRepeat.onchange = syncRepeatUI;

// Radio buttons controlling end condition enable/disable their sibling inputs
repeatEndRow.addEventListener("change", e => {
    if (e.target.name === "repeatEnd") syncEndConditionInputs();
});

function syncEndConditionInputs() {
    const selected = repeatEndRow.querySelector('input[name="repeatEnd"]:checked')?.value;
    document.getElementById("repeatUntil").disabled = selected !== "until";
    document.getElementById("repeatCount").disabled = selected !== "count";
}

// Weekday toggle buttons
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
/**
 * Returns an RFC 5545 RRULE string based on the current form state,
 * or null if the event does not repeat.
 */
function buildRrule(eventDate) {
    const mode = eventRepeat.value;
    if (mode === "none") {
        return null;
    }

    if (mode === "custom") {
        const raw = customRrule.value.trim();
        return raw || null;
    }

    const freqMap = { daily: "DAILY", weekly: "WEEKLY", monthly: "MONTHLY" };
    let rule = `RRULE:FREQ=${freqMap[mode]}`;

    // BYDAY for weekly
    if (mode === "weekly") {
        const days = Array.from(weekdayPicker.querySelectorAll(".wd-btn.active"))
            .map(b => b.dataset.day);

        // Fall back to the day-of-week of the selected date
        if (days.length === 0) {
            const dayNames = ["SU","MO","TU","WE","TH","FR","SA"];
            const [y, m, d] = eventDate.split("-").map(Number);
            days.push(dayNames[new Date(y, m - 1, d).getDay()]);
        }
        rule += `;BYDAY=${days.join(",")}`;
    }

    // End condition
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
/**
 * Returns a UTC-offset string like "+0530" or "-0500" for the given IANA
 * timezone at the given local date/time, accounting for DST.
 */
function tzOffset(ianaZone, dateStr, timeStr) {
    // Build a Date that represents the wall-clock time in the chosen zone.
    // We do this by formatting a known UTC instant in that zone and comparing.
    const [y, mo, d] = dateStr.split("-").map(Number);
    const [h, mi]    = (timeStr || "00:00").split(":").map(Number);

    // Use the Intl API to find what UTC instant corresponds to this local time.
    // Strategy: format an approximate UTC Date in the target zone and measure drift.
    const approxUtc = Date.UTC(y, mo - 1, d, h, mi);
    const fmt = new Intl.DateTimeFormat("en-CA", {
        timeZone: ianaZone,
        year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", hour12: false,
    });

    // Parse what the zone thinks the local time is for our approx UTC instant
    const parts = Object.fromEntries(fmt.formatToParts(new Date(approxUtc)).map(p => [p.type, p.value]));
    const localMs = Date.UTC(
        Number(parts.year), Number(parts.month) - 1, Number(parts.day),
        Number(parts.hour === "24" ? 0 : parts.hour), Number(parts.minute)
    );

    const offsetMin = Math.round((approxUtc - localMs) / 60000);
    const sign  = offsetMin <= 0 ? "+" : "-";
    const abs   = Math.abs(offsetMin);
    const hh    = String(Math.floor(abs / 60)).padStart(2, "0");
    const mm    = String(abs % 60).padStart(2, "0");
    return `${sign}${hh}${mm}`;
}

/**
 * Combine a date string (YYYY-MM-DD) and time string (HH:MM) into the
 * format the backend expects: "YYYY-MM-DD HH:MM:SS" (TIME_FORMAT).
 * If no time is given we default to midnight / 23:59.
 */
function buildDatetime(date, time, fallback = "00:00") {
    const t      = (time || fallback).replace(":", "");  // "HH:MM" → "HHMM"
    const d      = date.replace(/-/g, "");               // "YYYY-MM-DD" → "YYYYMMDD"
    const offset = tzOffset(eventTimezone.value, date, time || fallback);
    return `${d}-${t}-${offset}`;
}

eventForm.onsubmit = async (e) => {
    e.preventDefault();
    if (!selectedDateStr) {
        return;
    }

    const title       = eventTitle.value.trim();
    const startTime   = document.getElementById("eventStartTime").value;
    const endTime     = document.getElementById("eventEndTime").value;
    const location    = document.getElementById("eventLocation").value.trim() || null;
    const description = document.getElementById("eventDesc").value.trim() || null;

    if (!title) {
        return;
    }

    const startDatetime = buildDatetime(selectedDateStr, startTime, "00:00");
    const endDatetime   = buildDatetime(selectedDateStr, endTime,   "23:59");

    // Basic client-side guard: end must be after start
    if (endTime && startTime && endTime <= startTime) {
        alert("End time must be after start time.");
        return;
    }

    const rrule = buildRrule(selectedDateStr);

    const exceptions = getExceptionDates().map(d => ({
        exception_date: buildDatetime(d, "00:00")
    }));

    const payload = {
        title,
        start_time:  startDatetime,
        end_time:    endDatetime,
        location,
        description,
        rrule,
        exceptions: exceptions.length ? exceptions : null,
    };

    try {
        const res  = await fetch("/api/calendar/events", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Unknown error");
        closePanel();
        renderCalendar();
    } catch (err) {
        alert(err.message || "Failed to create event");
    }
};


/////////////////////////////////////////////////////////////////
///////////////////////// Calendar Init /////////////////////////
/////////////////////////////////////////////////////////////////
const { renderCalendar, getCurrent } = initCalendar(calendarEl, monthLabel, {
    onDayClick: (dateStr, cell) => openPanel(dateStr, cell),
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
