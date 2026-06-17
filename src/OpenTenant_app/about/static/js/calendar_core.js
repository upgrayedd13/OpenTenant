const monthLabelText = document.getElementById("monthLabelText");
const monthPicker = document.getElementById("monthPicker");
const yearInput = document.getElementById("yearInput");
const monthPickerGrid = document.getElementById("monthPickerGrid");
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

    return { renderCalendar, getCurrent: () => current };
}
