// ============================================================
// SMART ATTENDANCE SYSTEM
// frontend/script.js
// ============================================================


// ============================================================
// GLOBAL VARIABLES
// ============================================================

let cameraRunning = false;
let refreshInterval = null;


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    loadAttendance();

    loadStats();

    loadStudents();

    checkCameraStatus();

    startAutoRefresh();

});


// ============================================================
// AUTO REFRESH
// ============================================================

function startAutoRefresh() {

    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    refreshInterval = setInterval(function () {

        loadAttendance();

        loadStats();

        loadStudents();

        checkCameraStatus();

    }, 3000);

}


// ============================================================
// LOAD ATTENDANCE
// ============================================================

async function loadAttendance() {

    try {

        const response =
            await fetch("/api/attendance");


        if (!response.ok) {

            throw new Error(
                "Failed to load attendance records."
            );

        }


        const records =
            await response.json();


        const tableBody =
            document.getElementById(
                "attendanceTableBody"
            );


        if (!tableBody) {

            console.error(
                "attendanceTableBody not found."
            );

            return;

        }


        tableBody.innerHTML = "";


        if (
            !records ||
            records.length === 0
        ) {

            tableBody.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        style="text-align:center;"
                    >
                        No attendance records found.
                    </td>
                </tr>
            `;

            return;

        }


        records.forEach(function (record) {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${record.person_id ?? "-"}
                </td>

                <td>
                    ${escapeHtml(
                        record.name ?? "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.emotion ?? "Unknown"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.date ?? "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.time ?? "-"
                    )}
                </td>

                <td>

                    <button
                        class="attendance-delete-btn"
                        onclick="deleteAttendance(${record.id})"
                    >
                        Delete
                    </button>

                </td>

            `;


            tableBody.appendChild(row);

        });

    }

    catch (error) {

        console.error(
            "Load attendance error:",
            error
        );

    }

}


// ============================================================
// DELETE ATTENDANCE RECORD
// ============================================================

async function deleteAttendance(
    attendanceId
) {

    try {

        if (
            attendanceId === undefined ||
            attendanceId === null ||
            attendanceId === ""
        ) {

            alert(
                "Invalid attendance record ID."
            );

            return;

        }


        const confirmed =
            confirm(

                "Are you sure you want to delete " +
                "this attendance record?\n\n" +

                "Only this attendance record will " +
                "be deleted.\n\n" +

                "Student registration and photos " +
                "will NOT be deleted."

            );


        if (!confirmed) {

            return;

        }


        const response =
            await fetch(
                `/api/attendance/${attendanceId}`,
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            alert(
                result.message ||
                "Attendance record delete failed."
            );

            return;

        }


        alert(
            result.message
        );


        await loadAttendance();

        await loadStats();

    }

    catch (error) {

        console.error(
            "Delete attendance error:",
            error
        );


        alert(
            "Server error while deleting " +
            "attendance record.\n\n" +
            "Flask terminal check karo."
        );

    }

}


// ============================================================
// LOAD DASHBOARD STATS
// ============================================================

async function loadStats() {

    try {

        const response =
            await fetch("/api/stats");


        if (!response.ok) {

            throw new Error(
                "Failed to load statistics."
            );

        }


        const stats =
            await response.json();


        // ----------------------------------------
        // TOTAL RECORDS
        // ----------------------------------------

        const totalRecordsElement =
            document.getElementById(
                "totalRecords"
            );


        if (totalRecordsElement) {

            totalRecordsElement.textContent =
                stats.total_records ?? 0;

        }


        // ----------------------------------------
        // TODAY ATTENDANCE
        // ----------------------------------------

        const todayAttendanceElement =
            document.getElementById(
                "todayAttendance"
            );


        if (todayAttendanceElement) {

            todayAttendanceElement.textContent =
                stats.today_attendance ?? 0;

        }


        // ----------------------------------------
        // REGISTERED STUDENTS
        // ----------------------------------------

        const registeredStudentsElement =
            document.getElementById(
                "registeredStudents"
            );


        if (registeredStudentsElement) {

            registeredStudentsElement.textContent =

                stats.registered_students ??
                stats.total_students ??
                0;

        }

    }

    catch (error) {

        console.error(
            "Load stats error:",
            error
        );

    }

}


// ============================================================
// LOAD REGISTERED STUDENTS
// ============================================================

async function loadStudents() {

    try {

        const response =
            await fetch("/api/students");


        if (!response.ok) {

            throw new Error(
                "Failed to load students."
            );

        }


        const students =
            await response.json();


        const tableBody =
            document.getElementById(
                "studentsTableBody"
            );


        if (!tableBody) {

            console.error(
                "studentsTableBody not found."
            );

            return;

        }


        tableBody.innerHTML = "";


        if (
            !students ||
            students.length === 0
        ) {

            tableBody.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        style="text-align:center;"
                    >
                        No registered students found.
                    </td>

                </tr>

            `;

            return;

        }


        students.forEach(function (student) {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${student.id ?? "-"}
                </td>

                <td>
                    ${escapeHtml(
                        student.name ?? "-"
                    )}
                </td>

                <td>
                    ${student.photos ?? 0}
                </td>

                <td>

                    <span class="status-badge">

                        ${escapeHtml(
                            student.status ??
                            "Registered"
                        )}

                    </span>

                </td>

                <td>

                    <button
                        class="delete-btn"
                        onclick="deleteStudent(${student.id})"
                    >
                        Delete
                    </button>

                </td>

            `;


            tableBody.appendChild(row);

        });

    }

    catch (error) {

        console.error(
            "Load students error:",
            error
        );

    }

}


// ============================================================
// DELETE STUDENT
// ============================================================

async function deleteStudent(
    studentId
) {

    try {

        if (
            studentId === undefined ||
            studentId === null ||
            studentId === ""
        ) {

            alert(
                "Invalid student ID."
            );

            return;

        }


        const confirmed =
            confirm(

                `Are you sure you want to delete ` +
                `Student ID ${studentId}?\n\n` +

                `This will delete:\n` +

                `• Student registration\n` +
                `• Student photos\n` +
                `• Attendance records\n` +
                `• Recognition model data\n\n` +

                `This action cannot be undone.`

            );


        if (!confirmed) {

            return;

        }


        const response =
            await fetch(
                `/api/students/${studentId}`,
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            alert(
                result.message ||
                "Student delete failed."
            );

            return;

        }


        alert(
            result.message
        );


        await loadStudents();

        await loadAttendance();

        await loadStats();

    }

    catch (error) {

        console.error(
            "Delete student error:",
            error
        );


        alert(
            "Server error while deleting student.\n\n" +
            "Flask terminal check karo."
        );

    }

}


// ============================================================
// REGISTER STUDENT
// ============================================================

async function registerStudent() {

    try {

        // ----------------------------------------
        // GET INPUTS
        // ----------------------------------------

        const studentIdInput =
            document.getElementById(
                "studentId"
            );


        const studentNameInput =
            document.getElementById(
                "studentName"
            );


        const registerButton =
            document.getElementById(
                "registerBtn"
            );


        // ----------------------------------------
        // CHECK INPUT ELEMENTS
        // ----------------------------------------

        if (!studentIdInput) {

            alert(
                "Student ID input not found."
            );

            return;

        }


        if (!studentNameInput) {

            alert(
                "Student Name input not found."
            );

            return;

        }


        // ----------------------------------------
        // GET VALUES
        // ----------------------------------------

        const studentIdText =
            studentIdInput.value.trim();


        const name =
            studentNameInput.value.trim();


        // ----------------------------------------
        // VALIDATE STUDENT ID
        // ----------------------------------------

        if (!studentIdText) {

            alert(
                "Please enter Student ID."
            );

            studentIdInput.focus();

            return;

        }


        const personId =
            Number(studentIdText);


        if (
            !Number.isInteger(personId) ||
            personId <= 0
        ) {

            alert(
                "Please enter a valid Student ID."
            );

            studentIdInput.focus();

            return;

        }


        // ----------------------------------------
        // VALIDATE NAME
        // ----------------------------------------

        if (!name) {

            alert(
                "Please enter Student Name."
            );

            studentNameInput.focus();

            return;

        }


        // ----------------------------------------
        // DEFAULT PHOTO COUNT
        // ----------------------------------------

        const photos = 200;


        // ----------------------------------------
        // CONFIRM REGISTRATION
        // ----------------------------------------

        const confirmed =
            confirm(

                `Register Student?\n\n` +

                `Student ID: ${personId}\n` +
                `Name: ${name}\n` +
                `Photos: ${photos}\n\n` +

                `The camera will start and ` +
                `capture ${photos} photos.`

            );


        if (!confirmed) {

            return;

        }


        // ----------------------------------------
        // DISABLE BUTTON
        // ----------------------------------------

        if (registerButton) {

            registerButton.disabled =
                true;

            registerButton.textContent =
                "Registering...";

        }


        // ----------------------------------------
        // SEND REQUEST
        // IMPORTANT:
        // BACKEND EXPECTS person_id
        // ----------------------------------------

        const response =
            await fetch(
                "/api/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            person_id:
                                personId,

                            name:
                                name,

                            photos:
                                photos

                        })

                }
            );


        // ----------------------------------------
        // READ RESPONSE
        // ----------------------------------------

        const result =
            await response.json();


        // ----------------------------------------
        // ERROR
        // ----------------------------------------

        if (
            !response.ok ||
            !result.success
        ) {

            alert(

                result.message ||
                "Student registration failed."

            );

            return;

        }


        // ----------------------------------------
        // SUCCESS
        // ----------------------------------------

        alert(
            result.message ||
            "Student registered successfully."
        );


        // ----------------------------------------
        // CLEAR FORM
        // ----------------------------------------

        studentIdInput.value = "";

        studentNameInput.value = "";


        // ----------------------------------------
        // REFRESH DASHBOARD
        // ----------------------------------------

        await loadStudents();

        await loadStats();

        await loadAttendance();

    }

    catch (error) {

        console.error(
            "Register student error:",
            error
        );


        alert(

            "Server error during registration.\n\n" +

            "Flask terminal check karo."

        );

    }

    finally {

        const registerButton =
            document.getElementById(
                "registerBtn"
            );


        if (registerButton) {

            registerButton.disabled =
                false;

            registerButton.textContent =
                "Register Student";

        }

    }

}


// ============================================================
// START CAMERA
// ============================================================

async function startCamera() {

    try {

        const response =
            await fetch(
                "/api/start-camera",
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            alert(

                result.message ||
                "Camera start failed."

            );

            return;

        }


        cameraRunning = true;


        updateCameraUI(
            true
        );

    }

    catch (error) {

        console.error(
            "Start camera error:",
            error
        );


        alert(

            "Could not start camera.\n\n" +
            "Flask terminal check karo."

        );

    }

}


// ============================================================
// STOP CAMERA
// ============================================================

async function stopCamera() {

    try {

        const response =
            await fetch(
                "/api/stop-camera",
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            alert(

                result.message ||
                "Camera stop failed."

            );

            return;

        }


        cameraRunning = false;


        updateCameraUI(
            false
        );

    }

    catch (error) {

        console.error(
            "Stop camera error:",
            error
        );


        alert(

            "Could not stop camera.\n\n" +
            "Flask terminal check karo."

        );

    }

}


// ============================================================
// CHECK CAMERA STATUS
// ============================================================

async function checkCameraStatus() {

    try {

        const response =
            await fetch(
                "/api/camera-status"
            );


        if (!response.ok) {

            return;

        }


        const result =
            await response.json();


        cameraRunning =
            result.running === true;


        updateCameraUI(
            cameraRunning
        );

    }

    catch (error) {

        console.error(
            "Camera status error:",
            error
        );

    }

}


// ============================================================
// UPDATE CAMERA UI
// ============================================================

function updateCameraUI(
    running
) {

    const startButton =
        document.getElementById(
            "startCameraBtn"
        );


    const stopButton =
        document.getElementById(
            "stopCameraBtn"
        );


    const cameraStatus =
        document.getElementById(
            "cameraStatus"
        );


    // ----------------------------------------
    // START BUTTON
    // ----------------------------------------

    if (startButton) {

        startButton.disabled =
            running;

    }


    // ----------------------------------------
    // STOP BUTTON
    // ----------------------------------------

    if (stopButton) {

        stopButton.disabled =
            !running;

    }


    // ----------------------------------------
    // STATUS
    // ----------------------------------------

    if (cameraStatus) {

        if (running) {

            cameraStatus.textContent =
                "Camera Running";


            cameraStatus.classList.add(
                "camera-running"
            );


            cameraStatus.classList.remove(
                "camera-stopped"
            );

        }

        else {

            cameraStatus.textContent =
                "Camera Stopped";


            cameraStatus.classList.add(
                "camera-stopped"
            );


            cameraStatus.classList.remove(
                "camera-running"
            );

        }

    }

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;

}


// ============================================================
// MANUAL REFRESH
// ============================================================

async function refreshDashboard() {

    await loadAttendance();

    await loadStats();

    await loadStudents();

    await checkCameraStatus();

}


// ============================================================
// EXPORT FUNCTIONS
// ============================================================

window.loadAttendance =
    loadAttendance;


window.loadStats =
    loadStats;


window.loadStudents =
    loadStudents;


window.deleteAttendance =
    deleteAttendance;


window.deleteStudent =
    deleteStudent;


window.registerStudent =
    registerStudent;


window.startCamera =
    startCamera;


window.stopCamera =
    stopCamera;


window.refreshDashboard =
    refreshDashboard;