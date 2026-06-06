const calendarEl = document.getElementById("calendar");
const monthLabel = document.getElementById("monthLabel");

let current = new Date();

function renderCalendar() {
    calendarEl.innerHTML = "";

    const year = current.getFullYear();
    const month = current.getMonth();
    const tzOffset = current.getTimezoneOffset();

    monthLabel.textContent = current.toLocaleString("default", {
        month: "long",
        year: "numeric"
    });

    const firstDay = new Date(year, month, 1);
    const startOffset = firstDay.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // empty cells before first day
    for (let i = 0; i < startOffset; i++) {
        calendarEl.appendChild(document.createElement("div"));
    }

    fetch(`/api/calendar/events?year=${year}&month=${month + 1}&tz=${tzOffset}`)
        .then(async response => {
            const data = await response.json();

            if (!response.ok) {
                alert(data.error || "Unknown server error!");
                throw new Error(data.error);
            }

            return data;
        })
        .then(events => {
            // const byDate = {};
            // events.forEach(e => {
            //     byDate[e.date] = byDate[e.date] || [];
            //     byDate[e.date].push(e);
            // });

            for (let day = 1; day <= daysInMonth; day++) {
                const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                const cell = document.createElement("div");
                cell.className = "day";

                cell.innerHTML = `<div class="day-number">${day}</div>`;

                // (byDate[dateStr] || []).forEach(ev => {
                //     const el = document.createElement("div");
                //     el.className = "event";
                //     el.textContent = ev.title;
                //     cell.appendChild(el);
                // });

                // cell.onclick = () => createEvent(dateStr);
                calendarEl.appendChild(cell);
            }
        })
        .catch(err => {
            console.error(err);
        }
    );
}

function createEvent(date) {
    const title = prompt("Event title?");
    if (!title) return;

    fetch("/api/calendar/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, date })
    }).then(renderCalendar);
}

document.getElementById("prev").onclick = () => {
    current.setMonth(current.getMonth() - 1);
    renderCalendar();
};

document.getElementById("next").onclick = () => {
    current.setMonth(current.getMonth() + 1);
    renderCalendar();
};

renderCalendar();
