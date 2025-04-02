document.addEventListener("DOMContentLoaded", function () {
    const checkInOutButton = document.getElementById("checkInOutButton");
    const statusText = document.getElementById("statusText");
    const employeeName = document.getElementById("employeeName");

    // Set employee name dynamically
    fetch("/get_employee_name")
        .then(response => response.json())
        .then(data => {
            employeeName.textContent = data.name || "User";
        })
        .catch(error => console.error("Error fetching name:", error));

    checkInOutButton.addEventListener("click", function () {
        fetch("/mark_attendance", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    checkInOutButton.textContent = data.new_status === "checked_in" ? "Check Out" : "Check In";
                    statusText.textContent = `Current Status: ${data.new_status.replace('_', ' ')}`;
                }
            })
            .catch(error => console.error("Error:", error));
    });
});
