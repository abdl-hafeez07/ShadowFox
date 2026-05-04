import './style.css'

const introView = document.getElementById('intro-view');
const uploadView = document.getElementById('upload-view');
const uploadSection = document.getElementById('upload-section');
const fileInput = document.getElementById('file-input');
const loadingSection = document.getElementById('loading-section');
const resultsView = document.getElementById('results-view');
const previewImg = document.getElementById('preview-img');
const resetBtn = document.getElementById('reset-btn');
const topTag = document.getElementById('top-prediction');
const barsContainer = document.getElementById('bars-container');

const ICONS = {
  'Buildings': '🏢',
  'Forest': '🌲',
  'Mountain': '⛰️',
  'Sea': '🌊',
  'Street': '🛣️'
};

// Drag & Drop Handlers
uploadSection.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  uploadSection.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  uploadSection.addEventListener(eventName, () => uploadSection.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
  uploadSection.addEventListener(eventName, () => uploadSection.classList.remove('dragover'), false);
});

uploadSection.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', handleFileSelect, false);

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  if(files.length) handleFiles(files[0]);
}

function handleFileSelect(e) {
  if(e.target.files.length) handleFiles(e.target.files[0]);
}

function handleFiles(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please upload an image file (JPG, PNG)');
    return;
  }
  
  // Display preview
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    uploadToServer(file);
  };
  reader.readAsDataURL(file);
}

async function uploadToServer(file) {
  // UI Switch to Loading
  uploadSection.classList.add('hidden');
  loadingSection.classList.remove('hidden');

  const formData = new FormData();
  formData.append('image', file);

  try {
    const res = await fetch('http://127.0.0.1:5000/predict', {
      method: 'POST',
      body: formData
    });
    
    if (!res.ok) throw new Error('Network response was not ok');
    
    const data = await res.json();
    if(data.error) throw new Error(data.error);
    
    displayResults(data);
  } catch (err) {
    console.error(err);
    alert('Error predicting image. Ensure the Flask backend is running on port 5000.');
    resetUI();
  }
}

function displayResults(data) {
  // Update Top Prediction
  const topClass = data.top_class;
  const topProb = (data.top_probability * 100).toFixed(1);
  
  topTag.querySelector('.icon').innerText = ICONS[topClass] || '✨';
  topTag.querySelector('.class-name').innerText = topClass;
  topTag.querySelector('.confidence').innerText = topProb + '%';

  // Build Bars
  barsContainer.innerHTML = '';
  data.predictions.forEach((pred, index) => {
    const probPct = (pred.probability * 100).toFixed(1);
    const barHtml = `
      <div class="bar-item">
        <div class="bar-label">${pred.class}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: 0%"></div>
        </div>
        <div class="bar-value">${probPct}%</div>
      </div>
    `;
    barsContainer.insertAdjacentHTML('beforeend', barHtml);
  });

  // Switch UI to Full Results View
  loadingSection.classList.add('hidden');
  uploadView.classList.add('hidden');
  introView.classList.add('hidden');
  resultsView.classList.remove('hidden');

  // Trigger Animation
  setTimeout(() => {
    const fills = barsContainer.querySelectorAll('.bar-fill');
    data.predictions.forEach((pred, idx) => {
      fills[idx].style.width = `${pred.probability * 100}%`;
    });
  }, 50);
}

resetBtn.addEventListener('click', resetUI);

function resetUI() {
  fileInput.value = '';
  resultsView.classList.add('hidden');
  loadingSection.classList.add('hidden');
  
  // Restore initial state
  introView.classList.remove('hidden');
  uploadView.classList.remove('hidden');
  uploadSection.classList.remove('hidden');
}
