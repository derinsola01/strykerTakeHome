
const root = document.getElementById("root");

root.innerHTML = `
    <h2>Upload Invoice</h2>
    <input type="file" id="file" />
    <button onclick="upload()">Upload</button>
    <pre id="output"></pre>
`;

function upload() {
    const fileInput = document.getElementById("file");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").textContent =
            JSON.stringify(data, null, 2);
    });
}
