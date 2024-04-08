let audioContext;
let source;
let analyser;
let canvas;
let canvasCtx;
let audioBuffer;

window.onload = function () {
    document.getElementById('audio-input').addEventListener('change', handleFileSelect);

    canvas = document.getElementById('waveform');
    canvasCtx = canvas.getContext('2d');

    initializeAudioContext();
};

function initializeAudioContext() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();

    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;

    source = audioContext.createBufferSource();
    source.connect(analyser);
    analyser.connect(audioContext.destination);
}

function handleFileSelect(event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            audioContext.decodeAudioData(e.target.result, function (buffer) {
                audioBuffer = buffer;
                visualize();
            });
        };

        reader.readAsArrayBuffer(file);
    }
}

function visualize() {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = '#2ecc71';
    canvasCtx.beginPath();

    const sliceWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
            canvasCtx.moveTo(x, y);
        } else {
            canvasCtx.lineTo(x, y);
        }

        x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
}

function applyEqualization() {
    const filter = audioContext.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 35; // Adjust the base freq

    source.disconnect();
    source.connect(filter);
    filter.connect(analyser);
    analyser.connect(audioContext.destination);

    source.buffer = audioBuffer;
    source.start();
    visualize();
}
