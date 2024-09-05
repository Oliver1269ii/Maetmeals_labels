document.getElementById('downloadButton').addEventListener('click', function() {
    // Specify the filename to be downloaded from the server
    const filename = 'output.pdf';
    const downloadLink = document.createElement('a');
    downloadLink.href = `/uploads/${filename}`;
    downloadLink.download = filename;

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
});