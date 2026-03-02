const uploadBtn = document.getElementById("uploadLeaseBtn");
const pdfInput = document.getElementById("leasePdfInput");

uploadBtn.addEventListener("click", () => {
    pdfInput.click(); // opens file dialog
});

pdfInput.addEventListener("change", async () => {
    const file = pdfInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf", file);

    const response = await fetch("/parse-lease", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Failed to parse lease");
        return;
    }

    const data = await response.json();

    // Autofill fields
    if (data.first_name)
        document.getElementById("first_name").value = data.first_name;

    if (data.last_name)
        document.getElementById("last_name").value = data.last_name;

    if (data.unit_number)
        document.getElementById("unit_number").value = data.unit_number;

    if (data.lease_start)
        document.getElementById("lease_start").value = data.lease_start;

    if (data.lease_end)
        document.getElementById("lease_end").value = data.lease_end;

    if (data.monthly_rate)
        document.getElementById("monthly_rate").value = data.monthly_rate;
});