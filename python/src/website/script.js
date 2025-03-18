const loginForm = document.getElementById("loginForm");
const uploadForm = document.getElementById("uploadForm");
const downloadForm = document.getElementById("downloadForm");
const loginMessage = document.getElementById("loginMessage");
const uploadMessage = document.getElementById("uploadMessage");
const downloadMessage = document.getElementById("downloadMessage");
const uploadSection = document.getElementById("upload-section");
const downloadSection = document.getElementById("download-section");

let authToken = "";

// Set the base URLs for Minikube services
const AUTH_URL = "http://192.168.49.2:30001"; // Auth service exposed via NodePort
const GATEWAY_URL = "http://192.168.49.2:30002"; // Gateway service exposed via NodePort

// Handle Login
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        loginMessage.textContent = "Logging in...";
        const response = await fetch(`${AUTH_URL}/login`, {
            method: "POST",
            headers: {
                Authorization: `Basic ${btoa(`${email}:${password}`)}`,
            },
        });

        if (response.ok) {
            authToken = await response.text();
            loginMessage.textContent = "Login successful!";
            uploadSection.style.display = "block";
        } else {
            loginMessage.textContent = "Login failed: " + (await response.text());
        }
    } catch (error) {
        loginMessage.textContent = "Error connecting to the server.";
        console.error(error);
    }
});

// Handle Video Upload
uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const videoFile = document.getElementById("video").files[0];

    if (videoFile) {
        const formData = new FormData();
        formData.append("video", videoFile);

        try {
            uploadMessage.textContent = "Uploading your video...";
            const response = await fetch(`${GATEWAY_URL}/upload`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${authToken}`,
                },
                body: formData,
            });

            if (response.ok) {
                uploadMessage.textContent = "Video uploaded successfully!";
                downloadSection.style.display = "block";
            } else {
                uploadMessage.textContent = "Upload failed: " + (await response.text());
            }
        } catch (error) {
            uploadMessage.textContent = "Error connecting to the server.";
            console.error(error);
        }
    }
});

// Handle MP3 Download
downloadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileId = document.getElementById("fileId").value;

    if (fileId) {
        try {
            const response = await fetch(`${GATEWAY_URL}/download?fid=${fileId}`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${authToken}`,
                },
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", `${fileId}.mp3`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                downloadMessage.textContent = "Download started!";
            } else {
                downloadMessage.textContent = "Failed to fetch MP3 file.";
            }
        } catch (error) {
            downloadMessage.textContent = "Error connecting to the server.";
            console.error(error);
        }
    }
});
