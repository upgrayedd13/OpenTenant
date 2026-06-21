const uploadBtn = document.getElementById("uploadLeaseBtn");
const pdfInput = document.getElementById("leasePdfInput");
let config = null;

async function getUploadConfig() {
    const res = await fetch("/config");
    if (!res.ok) {
        throw new Error("Failed to load config");
    }
    return res.json();
}

async function ensureConfigLoaded() {
    if (!config) {
        config = await getUploadConfig();
    }
}

uploadBtn.addEventListener("click", () => {
    pdfInput.click();  // opens file dialog
});

async function uploadFile(file) {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await fetch("/account/upload-lease", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(`Upload failed: ${data.error}`);
    }

    return await response.json();
}

pdfInput.addEventListener("change", async () => {
    const file = pdfInput.files[0];
    if (!file) {
        alert("Didn't get file!");
        return;
    }

    await ensureConfigLoaded();

    if (file.size > config.maxUploadBytes) {
        alert(`File is too large. Max size is ${config.maxUploadBytes / 1024 / 1024} MB`);
        return;
    }

    const spinner = document.getElementById("uploadSpinner");
    spinner.classList.remove("hidden");

    let data;
    try {
        data = await uploadFile(file);
        if (data.error) {
            alert(`Lease validation error: ${data.error}\n\nPlease check the autofilled fields and correct them.`);
        }
    } catch (err) {
        console.error(err);
        alert(err.message);
        return;
    } finally {
        spinner.classList.add("hidden");
    }

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
        document.getElementById("apartment_info-base_monthly_rent").value = parseFloat(data.base_rent).toFixed(2);
    }

    if (data.monthly_rent_total) {
        document.getElementById("apartment_info-monthly_rent_total").value = parseFloat(data.monthly_rent_total).toFixed(2);
    }

    if (data.num_occupants) {
        document.getElementById("apartment_info-num_occupants").value = data.num_occupants;
    }

    if (data.upload_token) {
        document.getElementById("register_info-upload_token").value = data.upload_token;
    }
});
