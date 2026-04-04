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

    const response = await fetch("/upload-lease", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Failed to parse lease");
        return;
    }

    const data = await response.json();

    // Autofill fields
    if (data.authorized_adults) {
        document.getElementById("personal_info-given_name").value = data.authorized_adults;
    }

    if (data.unit_number) {
        document.getElementById("apartment_info-unit_number").value = data.unit_number;
    }

    if (data.lease_start_date) {
        document.getElementById("apartment_info-lease_start_date").value = data.lease_start_date;
    }

    if (data.lease_end_date) {
        document.getElementById("apartment_info-lease_end_date").value = data.lease_end_date;
    }

    if (data.base_rent) {
        document.getElementById("apartment_info-base_monthly_rent").value = data.base_rent.toFixed(2);
    }

    if (data.monthly_rent_total) {
        document.getElementById("apartment_info-monthly_rent_total").value = data.monthly_rent_total.toFixed(2);
    }

    if (data.num_authorized_adults || data.num_authorized_minors) {
        document.getElementById("apartment_info-num_occupants").value = data.num_authorized_adults + data.num_authorized_minors
    }

    if (data.address) {
        document.getElementById("apartment_info-address").value = data.address;
    }
});