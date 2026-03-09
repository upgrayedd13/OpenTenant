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
    if (data.residents) {
        const name = data.residents.split(" ");
        document.getElementById("first_name").value = name[0];
        document.getElementById("last_name").value = name[1];
    }

    if (data.unit_number) {
        document.getElementById("unit_number").value = data.unit_number;
    }

    if (data.lease_start_date) {
        document.getElementById("lease_start_date").value = data.lease_start_date;
    }

    if (data.lease_end_date) {
        document.getElementById("lease_end_date").value = data.lease_end_date;
    }

    if (data.base_rent) {
        document.getElementById("base_monthly_rent").value = data.base_rent.toFixed(2);
    }

    if (data.monthly_rent_total) {
        document.getElementById("monthly_rent_total").value = data.monthly_rent_total.toFixed(2);
    }

    document.getElementById("lease_num_occupants").value = 1;  // TODO: actually parse this value
});