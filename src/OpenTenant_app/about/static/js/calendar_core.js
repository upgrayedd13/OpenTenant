const monthLabelText = document.getElementById("monthLabelText");
const monthPicker = document.getElementById("monthPicker");
const yearInput = document.getElementById("yearInput");
const monthPickerGrid = document.getElementById("monthPickerGrid");
const eventModal = document.getElementById("eventModal");
const eventModalTitle = document.getElementById("eventModalTitle");
const eventModalBody = document.getElementById("eventModalBody");
const eventModalActions = document.getElementById("eventModalActions");
const eventModalClose = document.getElementById("eventModalClose");
const months = ["Jan", "Feb", "Mar" ,"Apr" ,"May" ,"Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function initCalendar(calendarEl, monthLabelBtn, options={}) {
    const { onDayClick, renderEventActions } = options;
    let current = new Date();

    // Build month buttons once
    months.forEach((name, i) => {
        const btn = document.createElement("button");
        btn.className = "month-pick-btn";
        btn.textContent = name;
        btn.onclick = () => {
            current.setMonth(i);
            closePicker();
            renderCalendar();
        };
        monthPickerGrid.appendChild(btn);
    });

    ////////////////////////
    // Handler functions
    ////////////////////////
    function renderCalendar() {
        calendarEl.innerHTML = "";
        const year = current.getFullYear();
        const month = current.getMonth();

        monthLabelText.textContent = current.toLocaleString("default", {
            month: "long", year: "numeric"
        });

        const firstDay = new Date(year, month, 1);
        const startOffset = firstDay.getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        for (let i = 0; i < startOffset; i++) {
            calendarEl.appendChild(document.createElement("div"));
        }

        const start = new Date(year, month, 1);
        const end = new Date(year, month + 1, 1);
        const startISO = start.toISOString();
        const endISO = end.toISOString();

        fetch(`/api/calendar/events?start=${startISO}&end=${endISO}`)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    alert(data.error || "Unknown server error!");
                    throw new Error(data.error);
                }
                return data;
            })
            .then(events => {
                // Spread each event across every calendar day it covers,
                // tagging each entry with its position in the span.
                const byDate = {};
                const toLocalDateString = (date) => {
                    const y = date.getFullYear();
                    const m = String(date.getMonth() + 1).padStart(2, '0');
                    const d = String(date.getDate()).padStart(2, '0');
                    return `${y}-${m}-${d}`;
                };

                events.forEach(e => {
                    const eventStart = new Date(e.start_time);
                    const eventEnd   = new Date(e.end_time);
                    const startDateStr = toLocalDateString(eventStart);
                    const endDateStr   = toLocalDateString(eventEnd);
                    const isMultiDay   = startDateStr !== endDateStr;

                    let cur = new Date(eventStart);
                    cur.setHours(0, 0, 0, 0);
                    
                    while (cur < eventEnd) {
                        const dayStart = new Date(cur);
                        const dayEnd   = new Date(cur);
                        dayEnd.setDate(dayEnd.getDate() + 1);
                        dayEnd.setHours(0, 0, 0, 0);
                        
                        if (eventStart < dayEnd && eventEnd > dayStart) {
                            const dateStr = toLocalDateString(cur);
                            byDate[dateStr] = byDate[dateStr] || [];
                            byDate[dateStr].push({
                                ...e,
                                _isMultiDay: isMultiDay,
                                _isStart:    dateStr === startDateStr,
                                _isEnd:      dateStr === endDateStr,
                            });
                        }
                        cur = dayEnd;
                    }
                });

                // Map from occurrence key → [segment elements], used to
                // coordinate hover highlight across all segments of one occurrence.
                // Key = id + start_time to scope to this occurrence, not all
                // instances of a recurring event.
                const segmentMap = new Map();

                function addSegment(key, el) {
                    if (!segmentMap.has(key)) segmentMap.set(key, []);
                    segmentMap.get(key).push(el);
                    el.addEventListener("mouseenter", () => {
                        segmentMap.get(key).forEach(s => s.classList.add("event--hovered"));
                    });
                    el.addEventListener("mouseleave", () => {
                        segmentMap.get(key).forEach(s => s.classList.remove("event--hovered"));
                    });
                }

                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr  = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                    const colIndex = (startOffset + day - 1) % 7;  // 0=Sun … 6=Sat

                        const cell = document.createElement("div");
                        cell.className = "day";
                        cell.dataset.date = dateStr;
                        if (onDayClick) cell.classList.add("day--clickable");
                        cell.innerHTML = `<div class="day-number">${day}</div>`;

                    // Multi-day events first so they stack above single-day ones
                    const dayEvents = [...(byDate[dateStr] || [])].sort(
                        (a, b) => (b._isMultiDay ? 1 : 0) - (a._isMultiDay ? 1 : 0)
                    );

                    dayEvents.forEach(ev => {
                        const el = document.createElement("div");
                        const segKey = `${ev.id}-${ev.start_time}`;

                        if (ev._isMultiDay) {
                            const isRowStart = colIndex === 0;
                            const isRowEnd   = colIndex === 6;
                            let cls = "event";
                            if (ev._isStart)    cls += " event--span-start";
                            else if (ev._isEnd) cls += " event--span-end";
                            else                cls += " event--span-mid";

                            if (!ev._isEnd   && isRowEnd)   cls += " event--row-end";
                            if (!ev._isStart && isRowStart) cls += " event--row-start";
                            el.className = cls;

                            // Show title on the first visible segment in each row
                            if (ev._isStart || (!ev._isStart && isRowStart)) {
                                el.textContent = ev.title;
                            } else {
                                el.setAttribute("aria-label", ev.title);
                            }
                        } else {
                            el.className = "event";
                            el.textContent = ev.title;
                        }

                        el.onclick = (e) => { e.stopPropagation(); openEventModal(ev); };
                        addSegment(segKey, el);
                        cell.appendChild(el);
                    });

                    if (onDayClick) {
                        cell.onclick = () => onDayClick(dateStr, cell, renderCalendar);
                    }

                    calendarEl.appendChild(cell);
                }
            })
            .catch(err => console.error(err));
    }

    function formatEventTime(ev) {
        const start        = new Date(ev.start_time);
        const end          = new Date(ev.end_time);
        const startDateStr = start.toISOString().slice(0, 10);
        const endDateStr   = end.toISOString().slice(0, 10);
        const isMultiDay   = startDateStr !== endDateStr;

        // All-day events are stored as 00:00 → 23:59 UTC
        const isAllDay     = start.getUTCHours() === 0 && start.getUTCMinutes() === 0 &&
                             end.getUTCHours() === 23   && end.getUTCMinutes() >= 59;
        const dateOpts     = { weekday: "short", month: "short", day: "numeric" };
        const timeOpts     = { hour: "numeric", minute: "2-digit" };

        if (isAllDay) {
            const s = start.toLocaleString("default", dateOpts);
            return isMultiDay ? `${s} - ${end.toLocaleString("default", dateOpts)}` : s;
        }

        const s = start.toLocaleString("default", { ...dateOpts, ...timeOpts });
        if (isMultiDay) {
            return `${s} - ${end.toLocaleString("default", { ...dateOpts, ...timeOpts })}`;
        }

        if (ev.end_time) {
            return `${s} - ${end.toLocaleString("default", timeOpts)}`;
        }

        return s;
    }

    function openEventModal(ev) {
        if (options.onEventClick) {
            options.onEventClick(ev);
            return;
        }

        eventModalTitle.textContent = ev.title || "Untitled event";
        eventModalBody.innerHTML = "";

        const time = document.createElement("p");
        time.className = "event-modal-time";
        time.textContent = formatEventTime(ev);
        eventModalBody.appendChild(time);

        if (ev.location) {
            const loc = document.createElement("p");
            loc.className = "event-modal-location";
            loc.textContent = ev.location;
            eventModalBody.appendChild(loc);
        }

        if (ev.description) {
            const desc = document.createElement("p");
            desc.className = "event-modal-description";
            desc.textContent = ev.description;
            eventModalBody.appendChild(desc);
        }

        eventModalActions.innerHTML = "";
        if (renderEventActions) {
            renderEventActions(ev, eventModalActions, { closeEventModal, renderCalendar });
        }

        eventModal.hidden = false;
    }

    function closeEventModal() {
        eventModal.hidden = true;
    }

    function openPicker() {
        yearInput.value = current.getFullYear();
        updatePickerHighlight();
        monthPicker.hidden = false;
        monthLabelBtn.setAttribute("aria-expanded", "true");
    }

    function closePicker() {
        monthPicker.hidden = true;
        monthLabelBtn.setAttribute("aria-expanded", "false");
    }

    function updatePickerHighlight() {
        monthPickerGrid.querySelectorAll(".month-pick-btn").forEach((btn, i) => {
            btn.classList.toggle("active", i === current.getMonth());
        });
    }

    ////////////////////////
    // Attach handlers
    ////////////////////////
    monthLabelBtn.onclick = () => {
        monthPicker.hidden ? openPicker() : closePicker();
    };

    document.getElementById("pickerClose").onclick = closePicker;

    document.getElementById("yearPrev").onclick = () => {
        current.setFullYear(current.getFullYear() - 1);
        yearInput.value = current.getFullYear();
        updatePickerHighlight();
        renderCalendar();
    };

    document.getElementById("yearNext").onclick = () => {
        current.setFullYear(current.getFullYear() + 1);
        yearInput.value = current.getFullYear();
        updatePickerHighlight();
        renderCalendar();
    };

    yearInput.onchange = () => {
        const y = parseInt(yearInput.value);
        if (y >= 1900 && y <= 2100) {
            current.setFullYear(y);
            updatePickerHighlight();
            renderCalendar();
        }
    };

    // Close picker when clicking outside
    document.addEventListener("click", (e) => {
        if (!monthPicker.hidden &&
            !monthPicker.contains(e.target) &&
            e.target !== monthLabelBtn) {
            closePicker();
        }
    });

    eventModalClose.onclick = closeEventModal;

    // Close event modal when clicking the backdrop (outside the content box)
    eventModal.addEventListener("click", (e) => {
        if (e.target === eventModal) closeEventModal();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !eventModal.hidden) closeEventModal();
    });

    return { renderCalendar, getCurrent: () => current };
}
