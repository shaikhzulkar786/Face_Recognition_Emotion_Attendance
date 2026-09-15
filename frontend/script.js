// ============================================================
// SMART ATTENDANCE SYSTEM
// FAST BROWSER CAMERA
// FACE RECOGNITION + EMOTION + ATTENDANCE
// ============================================================


// ============================================================
// GLOBAL VARIABLES
// ============================================================

let cameraStream = null;

let cameraRunning = false;

let cameraMode = "attendance";

let registrationRunning = false;

let registrationStudentId = null;

let registrationTotalPhotos = 200;

let registrationCaptured = 0;

let recognitionTimer = null;

let registrationTimer = null;

let processingFrame = false;


// Recognition request interval.
// Backend itself controls emotion frequency.
const RECOGNITION_INTERVAL = 1800;


// Registration interval.
const REGISTRATION_INTERVAL = 350;


// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupCameraArea();

        refreshDashboard();

        setInterval(
            refreshDashboard,
            5000
        );

    }
);


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ============================================================
// CAMERA AREA
// ============================================================

function setupCameraArea() {

    const container =
        document.querySelector(
            ".camera-container"
        );


    if (!container) {

        return;

    }


    container.innerHTML = `

        <div
            id="browserCameraBox"
            style="
                position:relative;
                width:100%;
                max-width:900px;
                margin:auto;
                background:#111827;
                border-radius:12px;
                overflow:hidden;
                min-height:400px;
                display:flex;
                align-items:center;
                justify-content:center;
            "
        >

            <video
                id="cameraVideo"
                autoplay
                playsinline
                muted
                style="
                    width:100%;
                    height:auto;
                    max-height:600px;
                    display:none;
                    object-fit:contain;
                    background:#111827;
                "
            ></video>


            <canvas
                id="cameraOverlay"
                style="
                    position:absolute;
                    pointer-events:none;
                    display:none;
                "
            ></canvas>


            <div
                id="cameraPlaceholder"
                style="
                    text-align:center;
                    color:white;
                    padding:50px 20px;
                "
            >

                <div
                    style="
                        font-size:60px;
                    "
                >
                    📷
                </div>

                <h3>
                    Smart Attendance Camera
                </h3>

                <p>
                    Start the camera to recognize students
                </p>

            </div>

        </div>


        <canvas
            id="captureCanvas"
            style="display:none;"
        ></canvas>


        <div
            id="cameraMessage"
            style="
                text-align:center;
                margin-top:12px;
                font-weight:600;
            "
        ></div>

    `;

}


// ============================================================
// CAMERA STATUS
// ============================================================

function updateCameraStatus(running) {

    const status =
        document.getElementById(
            "cameraStatus"
        );


    const startButton =
        document.getElementById(
            "startCameraBtn"
        );


    const stopButton =
        document.getElementById(
            "stopCameraBtn"
        );


    if (running) {

        if (status) {

            status.textContent =
                "Camera Running";

            status.classList.remove(
                "camera-stopped"
            );

            status.classList.add(
                "camera-running"
            );

        }


        if (startButton) {

            startButton.disabled =
                true;

        }


        if (stopButton) {

            stopButton.disabled =
                false;

        }

    }

    else {

        if (status) {

            status.textContent =
                "Camera Stopped";

            status.classList.remove(
                "camera-running"
            );

            status.classList.add(
                "camera-stopped"
            );

        }


        if (startButton) {

            startButton.disabled =
                false;

        }


        if (stopButton) {

            stopButton.disabled =
                true;

        }

    }

}


// ============================================================
// CAMERA MESSAGE
// ============================================================

function showCameraMessage(
    message,
    type = "normal"
) {

    const element =
        document.getElementById(
            "cameraMessage"
        );


    if (!element) {

        return;

    }


    element.textContent =
        message;


    if (type === "success") {

        element.style.color =
            "green";

    }

    else if (type === "error") {

        element.style.color =
            "red";

    }

    else {

        element.style.color =
            "#2563eb";

    }

}


// ============================================================
// START CAMERA
// ============================================================

async function startCamera() {

    try {

        if (cameraRunning) {

            showCameraMessage(
                "Camera is already running."
            );

            return;

        }


        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            alert(
                "Browser camera supported nahi hai.\n\n" +
                "Chrome ya Edge use karo."
            );

            return;

        }


        showCameraMessage(
            "Requesting camera permission..."
        );


        cameraStream =
            await navigator.mediaDevices.getUserMedia({

                video: {

                    width: {
                        ideal: 640
                    },

                    height: {
                        ideal: 360
                    },

                    facingMode:
                        "user"

                },

                audio: false

            });


        const video =
            document.getElementById(
                "cameraVideo"
            );


        const overlay =
            document.getElementById(
                "cameraOverlay"
            );


        const placeholder =
            document.getElementById(
                "cameraPlaceholder"
            );


        if (!video) {

            throw new Error(
                "Camera video element not found."
            );

        }


        video.srcObject =
            cameraStream;


        await video.play();


        video.style.display =
            "block";


        if (overlay) {

            overlay.style.display =
                "block";

        }


        if (placeholder) {

            placeholder.style.display =
                "none";

        }


        cameraRunning =
            true;


        cameraMode =
            "attendance";


        updateCameraStatus(
            true
        );


        showCameraMessage(
            "Camera started. Looking for registered students..."
        );


        startRecognitionLoop();

    }


    catch (error) {

        console.error(
            "Camera start error:",
            error
        );


        cameraRunning =
            false;


        updateCameraStatus(
            false
        );


        let message =
            "Unable to access camera.";


        if (
            error.name ===
            "NotAllowedError"
        ) {

            message =
                "Camera permission denied.\n\n" +
                "Browser address bar se Camera → Allow karo.";

        }


        else if (
            error.name ===
            "NotFoundError"
        ) {

            message =
                "Camera not found.";

        }


        else if (
            error.name ===
            "NotReadableError"
        ) {

            message =
                "Camera kisi dusre application mein use ho raha hai.";

        }


        alert(
            message
        );

    }

}


// ============================================================
// STOP CAMERA
// ============================================================

async function stopCamera() {

    try {

        stopRecognitionLoop();

        stopRegistrationLoop();


        if (cameraStream) {

            cameraStream
                .getTracks()
                .forEach(
                    function (track) {

                        track.stop();

                    }
                );


            cameraStream =
                null;

        }


        const video =
            document.getElementById(
                "cameraVideo"
            );


        const overlay =
            document.getElementById(
                "cameraOverlay"
            );


        const placeholder =
            document.getElementById(
                "cameraPlaceholder"
            );


        if (video) {

            video.pause();

            video.srcObject =
                null;

            video.style.display =
                "none";

        }


        if (overlay) {

            overlay.style.display =
                "none";

            clearFaceOverlay();

        }


        if (placeholder) {

            placeholder.style.display =
                "block";

        }


        cameraRunning =
            false;


        registrationRunning =
            false;


        registrationStudentId =
            null;


        updateCameraStatus(
            false
        );


        showCameraMessage(
            "Camera stopped."
        );

    }


    catch (error) {

        console.error(
            "Camera stop error:",
            error
        );

    }

}


// ============================================================
// CAPTURE FRAME
// ============================================================

function captureFrameBlob() {

    return new Promise(
        function (
            resolve,
            reject
        ) {

            const video =
                document.getElementById(
                    "cameraVideo"
                );


            const canvas =
                document.getElementById(
                    "captureCanvas"
                );


            if (
                !video ||
                !canvas
            ) {

                reject(
                    new Error(
                        "Camera elements not found."
                    )
                );

                return;

            }


            if (
                video.readyState < 2
            ) {

                reject(
                    new Error(
                        "Camera video is not ready."
                    )
                );

                return;

            }


            // IMPORTANT:
            // Do NOT send 1280x720 every time.
            // 640x360 = much faster.

            const width =
                Math.min(
                    video.videoWidth || 640,
                    640
                );


            const originalWidth =
                video.videoWidth || 640;


            const originalHeight =
                video.videoHeight || 360;


            const scale =
                width /
                originalWidth;


            const height =
                Math.round(
                    originalHeight *
                    scale
                );


            canvas.width =
                width;


            canvas.height =
                height;


            const context =
                canvas.getContext(
                    "2d"
                );


            context.drawImage(

                video,

                0,
                0,

                width,
                height

            );


            canvas.toBlob(

                function (blob) {

                    if (!blob) {

                        reject(
                            new Error(
                                "Could not create image."
                            )
                        );

                        return;

                    }


                    resolve(
                        blob
                    );

                },

                "image/jpeg",

                0.70

            );

        }
    );

}


// ============================================================
// SYNC OVERLAY
// ============================================================

function syncOverlayToVideo() {

    const video =
        document.getElementById(
            "cameraVideo"
        );


    const overlay =
        document.getElementById(
            "cameraOverlay"
        );


    const box =
        document.getElementById(
            "browserCameraBox"
        );


    if (
        !video ||
        !overlay ||
        !box
    ) {

        return false;

    }


    const width =
        video.videoWidth;


    const height =
        video.videoHeight;


    if (
        !width ||
        !height
    ) {

        return false;

    }


    const videoRect =
        video.getBoundingClientRect();


    const boxRect =
        box.getBoundingClientRect();


    overlay.width =
        width;


    overlay.height =
        height;


    overlay.style.left =
        `${videoRect.left - boxRect.left}px`;


    overlay.style.top =
        `${videoRect.top - boxRect.top}px`;


    overlay.style.width =
        `${videoRect.width}px`;


    overlay.style.height =
        `${videoRect.height}px`;


    return true;

}


// ============================================================
// DRAW FACE BOXES
// ============================================================

function drawFaces(faces) {

    const video =
        document.getElementById(
            "cameraVideo"
        );


    const overlay =
        document.getElementById(
            "cameraOverlay"
        );


    if (
        !video ||
        !overlay
    ) {

        return;

    }


    const width =
        video.videoWidth;


    const height =
        video.videoHeight;


    if (
        !width ||
        !height
    ) {

        return;

    }


    if (
        !syncOverlayToVideo()
    ) {

        return;

    }


    const context =
        overlay.getContext(
            "2d"
        );


    context.clearRect(
        0,
        0,
        width,
        height
    );


    if (
        !faces ||
        !faces.length
    ) {

        return;

    }


    // Backend receives 640px width.
    // Browser video may be larger.
    const scaleX =
        width /
        Math.min(
            width,
            640
        );


    faces.forEach(
        function (face) {

            let x =
                Number(face.x) ||
                0;


            let y =
                Number(face.y) ||
                0;


            let w =
                Number(face.width) ||
                0;


            let h =
                Number(face.height) ||
                0;


            // Scale coordinates when needed.
            x *= scaleX;
            w *= scaleX;

            const backendHeight =
                Math.round(
                    360 *
                    (Math.min(width, 640) /
                    width)
                );

            if (backendHeight > 0) {

                // Keep Y proportional.
                const scaleY =
                    height /
                    Math.max(
                        1,
                        backendHeight
                    );

                y *= scaleY;
                h *= scaleY;

            }


            if (
                w <= 0 ||
                h <= 0
            ) {

                return;

            }


            const isKnown =
                face.name &&
                face.name !== "Unknown";


            context.lineWidth =
                4;


            context.strokeStyle =
                isKnown
                    ? "#22c55e"
                    : "#ef4444";


            context.strokeRect(
                x,
                y,
                w,
                h
            );


            let label =
                face.name ||
                "Unknown";


            if (
                face.emotion &&
                face.emotion !==
                    "Unknown"
            ) {

                label +=
                    " | " +
                    face.emotion;

            }


            context.font =
                "bold 20px Arial";


            const textWidth =
                context.measureText(
                    label
                ).width;


            context.fillStyle =
                isKnown
                    ? "#22c55e"
                    : "#ef4444";


            context.fillRect(

                x,

                Math.max(
                    0,
                    y - 32
                ),

                textWidth + 16,

                32

            );


            context.fillStyle =
                "#ffffff";


            context.fillText(

                label,

                x + 8,

                Math.max(
                    22,
                    y - 9
                )

            );

        }
    );

}


// ============================================================
// CLEAR FACE BOX
// ============================================================

function clearFaceOverlay() {

    const overlay =
        document.getElementById(
            "cameraOverlay"
        );


    if (!overlay) {

        return;

    }


    const context =
        overlay.getContext(
            "2d"
        );


    context.clearRect(

        0,
        0,

        overlay.width,
        overlay.height

    );

}


// ============================================================
// RESIZE
// ============================================================

window.addEventListener(
    "resize",
    function () {

        if (!cameraRunning) {

            return;

        }


        requestAnimationFrame(
            function () {

                syncOverlayToVideo();

            }
        );

    }
);


// ============================================================
// RECOGNITION LOOP
// ============================================================

function startRecognitionLoop() {

    stopRecognitionLoop();


    recognitionTimer =
        setInterval(

            async function () {

                if (!cameraRunning) {

                    return;

                }


                if (
                    cameraMode !==
                    "attendance"
                ) {

                    return;

                }


                if (processingFrame) {

                    return;

                }


                await processRecognitionFrame();

            },

            RECOGNITION_INTERVAL

        );

}


// ============================================================
// STOP RECOGNITION LOOP
// ============================================================

function stopRecognitionLoop() {

    if (
        recognitionTimer
    ) {

        clearInterval(
            recognitionTimer
        );


        recognitionTimer =
            null;

    }

}


// ============================================================
// PROCESS RECOGNITION FRAME
// ============================================================

async function processRecognitionFrame() {

    processingFrame =
        true;


    try {

        const blob =
            await captureFrameBlob();


        const formData =
            new FormData();


        formData.append(

            "frame",

            blob,

            "camera.jpg"

        );


        const response =
            await fetch(

                "/api/browser/process-frame",

                {

                    method:
                        "POST",

                    body:
                        formData

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            console.error(

                "Recognition error:",

                result.message

            );

            return;

        }


        drawFaces(
            result.faces || []
        );


        if (
            result.recognized &&
            result.person
        ) {

            const person =
                result.person;


            showCameraMessage(

                `${person.name} recognized | ` +
                `Emotion: ${person.emotion || "Unknown"}`,

                "success"

            );

        }

        else {

            showCameraMessage(

                "Looking for registered students..."

            );

        }

    }


    catch (error) {

        console.error(

            "Recognition frame error:",

            error

        );

    }


    finally {

        processingFrame =
            false;

    }

}


// ============================================================
// REGISTER STUDENT
// ============================================================

async function registerStudent() {

    try {

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


        if (
            !studentIdInput ||
            !studentNameInput
        ) {

            alert(
                "Registration fields not found."
            );

            return;

        }


        const studentId =
            parseInt(
                studentIdInput.value
            );


        const studentName =
            studentNameInput.value.trim();


        if (
            !studentId ||
            isNaN(studentId) ||
            studentId <= 0
        ) {

            alert(
                "Please enter a valid Student ID."
            );

            studentIdInput.focus();

            return;

        }


        if (!studentName) {

            alert(
                "Please enter Student Name."
            );

            studentNameInput.focus();

            return;

        }


        // ----------------------------------------------------
        // START CAMERA
        // ----------------------------------------------------

        if (!cameraRunning) {

            await startCamera();


            if (!cameraRunning) {

                return;

            }

        }


        // ----------------------------------------------------
        // REGISTRATION MODE
        // ----------------------------------------------------

        cameraMode =
            "registration";


        stopRecognitionLoop();


        registrationRunning =
            true;


        registrationStudentId =
            studentId;


        registrationTotalPhotos =
            200;


        registrationCaptured =
            0;


        if (registerButton) {

            registerButton.disabled =
                true;

            registerButton.textContent =
                "Starting...";

        }


        showRegistrationStatus(
            "Starting registration..."
        );


        // ----------------------------------------------------
        // START SESSION
        // ----------------------------------------------------

        const startResponse =
            await fetch(

                "/api/browser/register/start",

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            person_id:
                                studentId,

                            name:
                                studentName,

                            photos:
                                200

                        })

                }

            );


        const startResult =
            await startResponse.json();


        if (
            !startResponse.ok ||
            !startResult.success
        ) {

            throw new Error(

                startResult.message ||
                "Registration could not start."

            );

        }


        registrationTotalPhotos =
            startResult.total_photos ||
            200;


        showRegistrationStatus(

            `Position your face inside camera. ` +
            `Capturing 0/${registrationTotalPhotos}`

        );


        startRegistrationLoop();

    }


    catch (error) {

        console.error(

            "Registration error:",

            error

        );


        alert(

            error.message ||
            "Registration failed."

        );


        registrationRunning =
            false;


        cameraMode =
            "attendance";


        const button =
            document.getElementById(
                "registerBtn"
            );


        if (button) {

            button.disabled =
                false;

            button.textContent =
                "Register Student";

        }


        if (cameraRunning) {

            startRecognitionLoop();

        }

    }

}


// ============================================================
// REGISTRATION LOOP
// ============================================================

function startRegistrationLoop() {

    stopRegistrationLoop();


    registrationTimer =
        setInterval(

            async function () {

                if (
                    !registrationRunning
                ) {

                    return;

                }


                if (
                    processingFrame
                ) {

                    return;

                }


                await captureRegistrationFrame();

            },

            REGISTRATION_INTERVAL

        );

}


// ============================================================
// STOP REGISTRATION LOOP
// ============================================================

function stopRegistrationLoop() {

    if (
        registrationTimer
    ) {

        clearInterval(
            registrationTimer
        );


        registrationTimer =
            null;

    }

}


// ============================================================
// CAPTURE REGISTRATION FRAME
// ============================================================

async function captureRegistrationFrame() {

    processingFrame =
        true;


    try {

        const blob =
            await captureFrameBlob();


        const formData =
            new FormData();


        formData.append(

            "person_id",

            registrationStudentId

        );


        formData.append(

            "frame",

            blob,

            "registration.jpg"

        );


        const response =
            await fetch(

                "/api/browser/register/frame",

                {

                    method:
                        "POST",

                    body:
                        formData

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            console.error(

                "Registration frame error:",

                result.message

            );

            return;

        }


        registrationCaptured =
            result.captured || 0;


        // ----------------------------------------------------
        // FACE BOX
        // ----------------------------------------------------

        if (
            result.face_detected
        ) {

            drawFaces([{

                name:
                    "Capturing",

                emotion:
                    "",

                x:
                    result.x,

                y:
                    result.y,

                width:
                    result.width,

                height:
                    result.height

            }]);

        }


        if (
            result.face_detected
        ) {

            showRegistrationStatus(

                `📸 Capturing photos: ` +

                `${registrationCaptured}/` +

                `${registrationTotalPhotos}`

            );

        }

        else {

            showRegistrationStatus(

                `⚠️ Face not detected | ` +

                `${registrationCaptured}/` +

                `${registrationTotalPhotos}`

            );

        }


        // ----------------------------------------------------
        // COMPLETE
        // ----------------------------------------------------

        if (
            result.complete
        ) {

            await finishRegistration();

        }

    }


    catch (error) {

        console.error(

            "Registration capture error:",

            error

        );

    }


    finally {

        processingFrame =
            false;

    }

}


// ============================================================
// FINISH REGISTRATION
// ============================================================

async function finishRegistration() {

    if (
        !registrationRunning
    ) {

        return;

    }


    registrationRunning =
        false;


    stopRegistrationLoop();


    showRegistrationStatus(

        "Photos captured. Training recognition model..."

    );


    try {

        const response =
            await fetch(

                "/api/browser/register/finish",

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            person_id:
                                registrationStudentId

                        })

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            throw new Error(

                result.message ||
                "Model training failed."

            );

        }


        showRegistrationStatus(

            `✅ ${result.name} registered successfully! ` +
            `${result.photos} photos captured.`,

            "success"

        );


        alert(
            result.message
        );


        // ----------------------------------------------------
        // CLEAR FORM
        // ----------------------------------------------------

        const idInput =
            document.getElementById(
                "studentId"
            );


        const nameInput =
            document.getElementById(
                "studentName"
            );


        if (idInput) {

            idInput.value =
                "";

        }


        if (nameInput) {

            nameInput.value =
                "";

        }


        // ----------------------------------------------------
        // REFRESH
        // ----------------------------------------------------

        await loadStudents();

        await loadStats();


        // ----------------------------------------------------
        // ATTENDANCE MODE
        // ----------------------------------------------------

        cameraMode =
            "attendance";


        registrationStudentId =
            null;


        const button =
            document.getElementById(
                "registerBtn"
            );


        if (button) {

            button.disabled =
                false;

            button.textContent =
                "Register Student";

        }


        if (cameraRunning) {

            startRecognitionLoop();

        }

    }


    catch (error) {

        console.error(

            "Finish registration error:",

            error

        );


        alert(

            error.message ||
            "Registration finish failed."

        );


        cameraMode =
            "attendance";


        registrationStudentId =
            null;


        const button =
            document.getElementById(
                "registerBtn"
            );


        if (button) {

            button.disabled =
                false;

            button.textContent =
                "Register Student";

        }


        if (cameraRunning) {

            startRecognitionLoop();

        }

    }

}


// ============================================================
// REGISTRATION STATUS
// ============================================================

function showRegistrationStatus(

    message,

    type = "normal"

) {

    let element =
        document.getElementById(
            "registrationStatus"
        );


    if (!element) {

        const button =
            document.getElementById(
                "registerBtn"
            );


        if (!button) {

            return;

        }


        element =
            document.createElement(
                "div"
            );


        element.id =
            "registrationStatus";


        element.style.marginTop =
            "12px";


        element.style.padding =
            "12px";


        element.style.borderRadius =
            "8px";


        element.style.textAlign =
            "center";


        element.style.fontWeight =
            "600";


        button.parentNode.insertBefore(

            element,

            button.nextSibling

        );

    }


    element.textContent =
        message;


    if (
        type === "success"
    ) {

        element.style.color =
            "#15803d";

        element.style.background =
            "#dcfce7";

    }

    else {

        element.style.color =
            "#1d4ed8";

        element.style.background =
            "#dbeafe";

    }

}


// ============================================================
// LOAD ATTENDANCE
// ============================================================

async function loadAttendance() {

    try {

        const response =
            await fetch(
                "/api/attendance"
            );


        if (!response.ok) {

            throw new Error(
                "Attendance API error"
            );

        }


        const records =
            await response.json();


        const table =
            document.getElementById(
                "attendanceTableBody"
            );


        if (!table) {

            return;

        }


        table.innerHTML =
            "";


        if (
            !Array.isArray(records) ||
            records.length === 0
        ) {

            table.innerHTML = `

                <tr>

                    <td
                        colspan="6"
                        class="loading-cell"
                    >
                        No attendance records found.
                    </td>

                </tr>

            `;

            return;

        }


        records.forEach(

            function (record) {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${escapeHtml(record.person_id)}
                    </td>

                    <td>
                        ${escapeHtml(record.name)}
                    </td>

                    <td>
                        ${escapeHtml(
                            record.emotion ||
                            "Unknown"
                        )}
                    </td>

                    <td>
                        ${escapeHtml(record.date)}
                    </td>

                    <td>
                        ${escapeHtml(record.time)}
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


                table.appendChild(
                    row
                );

            }

        );

    }


    catch (error) {

        console.error(
            "Attendance error:",
            error
        );

    }

}


// ============================================================
// DELETE ATTENDANCE
// ============================================================

async function deleteAttendance(
    attendanceId
) {

    try {

        if (
            attendanceId ===
                undefined ||
            attendanceId ===
                null ||
            attendanceId ===
                ""
        ) {

            alert(
                "Invalid attendance record ID."
            );

            return;

        }


        const confirmed =
            confirm(

                "Are you sure you want to delete this attendance record?\n\n" +

                "Only this attendance record will be deleted.\n" +

                "Student registration and photos will NOT be deleted."

            );


        if (!confirmed) {

            return;

        }


        const response =
            await fetch(

                `/api/attendance/${attendanceId}`,

                {

                    method:
                        "DELETE"

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

            "Server error while deleting attendance record.\n\n" +
            "Flask terminal check karo."

        );

    }

}


// ============================================================
// LOAD STUDENTS
// ============================================================

async function loadStudents() {

    try {

        const response =
            await fetch(
                "/api/students"
            );


        if (!response.ok) {

            throw new Error(
                "Students API error"
            );

        }


        const students =
            await response.json();


        const table =
            document.getElementById(
                "studentsTableBody"
            );


        if (!table) {

            return;

        }


        table.innerHTML =
            "";


        if (
            !Array.isArray(students) ||
            students.length === 0
        ) {

            table.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        class="loading-cell"
                    >
                        No registered students.
                    </td>

                </tr>

            `;

            return;

        }


        students.forEach(

            function (student) {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${escapeHtml(student.id)}
                    </td>

                    <td>
                        ${escapeHtml(student.name)}
                    </td>

                    <td>
                        ${escapeHtml(
                            student.photos || 0
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            student.status ||
                            "Registered"
                        )}
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


                table.appendChild(
                    row
                );

            }

        );

    }


    catch (error) {

        console.error(

            "Students error:",

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
            studentId ===
                undefined ||
            studentId ===
                null ||
            studentId ===
                ""
        ) {

            alert(
                "Invalid Student ID."
            );

            return;

        }


        const confirmed =
            confirm(

                `Are you sure you want to delete Student ID ${studentId}?\n\n` +

                `This will delete:\n` +

                `• Student photos\n` +

                `• Student registration\n` +

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

                    method:
                        "DELETE"

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
// LOAD STATS
// ============================================================

async function loadStats() {

    try {

        const response =
            await fetch(
                "/api/stats"
            );


        if (!response.ok) {

            throw new Error(
                "Stats API error"
            );

        }


        const stats =
            await response.json();


        const totalRecords =
            document.getElementById(
                "totalRecords"
            );


        const todayAttendance =
            document.getElementById(
                "todayAttendance"
            );


        const registeredStudents =
            document.getElementById(
                "registeredStudents"
            );


        if (totalRecords) {

            totalRecords.textContent =
                stats.total_records ??
                0;

        }


        if (todayAttendance) {

            todayAttendance.textContent =
                stats.today_attendance ??
                0;

        }


        if (registeredStudents) {

            registeredStudents.textContent =
                stats.registered_students ??
                stats.total_students ??
                0;

        }

    }


    catch (error) {

        console.error(
            "Stats error:",
            error
        );

    }

}


// ============================================================
// REFRESH DASHBOARD
// ============================================================

async function refreshDashboard() {

    await Promise.all([

        loadStats(),

        loadStudents(),

        loadAttendance()

    ]);

}