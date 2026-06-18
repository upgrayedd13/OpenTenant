const monthLabelText = document.getElementById("monthLabelText");
const monthPicker = document.getElementById("monthPicker");
const yearInput = document.getElementById("yearInput");
const monthPickerGrid = document.getElementById("monthPickerGrid");
const eventModal = document.getElementById("eventModal");
const eventModalTitle = document.getElementById("eventModalTitle");
const eventModalBody = document.getElementById("eventModalBody");
const eventModalClose = document.getElementById("eventModalClose");
const months = ["Jan", "Feb", "Mar" ,"Apr" ,"May" ,"Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function initCalendar(calendarEl, monthLabelBtn, options={}) {
    const { onDayClick } = options;
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

        fetch(`/api/calendar/events?year=${year}&month=${month + 1}`)
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    alert(data.error || "Unknown server error!");
                    throw new Error(data.error);
                }
                return data;
            })
            .then(events => {
                const byDate = {};
                events.forEach(e => {
                    const localDate = new Date(e.start_time).toISOString().slice(0, 10);  // YYYY-MM-DD
                    byDate[localDate] = byDate[localDate] || [];
                    byDate[localDate].push(e);
                });

                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                    const cell = document.createElement("div");
                    cell.className = "day";
                    if (onDayClick) cell.classList.add("day--clickable");
                    cell.innerHTML = `<div class="day-number">${day}</div>`;

                    (byDate[dateStr] || []).forEach(ev => {
                        const el = document.createElement("div");
                        el.className = "event";
                        el.textContent = ev.title;
                        el.onclick = (e) => {
                            e.stopPropagation();
                            openEventModal(ev);
                        };
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
        const start = new Date(ev.start_time);
        const startStr = start.toLocaleString("default", {
            weekday: "short", month: "short", day: "numeric",
            hour: "numeric", minute: "2-digit"
        });
        if (ev.end_time) {
            const end = new Date(ev.end_time);
            const endStr = end.toLocaleString("default", {
                hour: "numeric", minute: "2-digit"
            });
            return `${startStr} – ${endStr}`;
        }
        return startStr;
    }

    function openEventModal(ev) {
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
