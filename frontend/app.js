// API configuration
const API_BASE = 'http://localhost:8000';

// DOM elements
const authButton = document.getElementById('auth-button');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const userInfo = document.getElementById('user-info');
const userDisplay = document.getElementById('user-display');
const createProjectSection = document.getElementById('create-project');
const projectList = document.getElementById('project-list');

// State
let currentUser = null;
let apiKey = localStorage.getItem('makergit_api_key');

// Utility functions
function showMessage(message, type = 'error') {
  const existing = document.querySelector('.error, .success');
  if (existing) existing.remove();

  const div = document.createElement('div');
  div.className = type;
  div.textContent = message;

  const header = document.querySelector('header');
  header.appendChild(div);

  setTimeout(() => div.remove(), 5000);
}

function setAuthHeader() {
  return apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {};
}

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  // Build headers carefully to merge with options headers
  const headers = {
    'Content-Type': 'application/json',
    ...setAuthHeader(),
    ...(options.headers || {}),
  };
  
  const config = {
    ...options,
    headers, // Set headers last so they don't get overwritten
  };

  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Authentication functions
function showLogin() {
  loginForm.style.display = 'block';
  registerForm.style.display = 'none';
  authButton.style.display = 'none';
}

function showRegister() {
  loginForm.style.display = 'none';
  registerForm.style.display = 'block';
}

async function login() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  if (!username || !password) {
    showMessage('Please fill in all fields');
    return;
  }

  try {
    const data = await apiCall('/auth/login', {
      method: 'POST',
      body: { username, password },
    });

    apiKey = data.api_key;
    localStorage.setItem('makergit_api_key', apiKey);
    await loadUser();
    showMessage('Login successful!', 'success');
  } catch (error) {
    showMessage(`Login failed: ${error.message}`);
  }
}

async function register() {
  const username = document.getElementById('register-username').value;
  const email = document.getElementById('register-email').value;
  const displayName = document.getElementById('register-display-name').value;
  const password = document.getElementById('register-password').value;

  if (!username || !email || !password) {
    showMessage('Please fill in required fields');
    return;
  }

  try {
    const data = await apiCall('/auth/register', {
      method: 'POST',
      body: { username, email, display_name: displayName, password },
    });

    apiKey = data.api_key;
    localStorage.setItem('makergit_api_key', apiKey);
    currentUser = data;
    updateUI();
    showMessage('Registration successful!', 'success');
  } catch (error) {
    showMessage(`Registration failed: ${error.message}`);
  }
}

function logout() {
  apiKey = null;
  currentUser = null;
  localStorage.removeItem('makergit_api_key');
  updateUI();
  showMessage('Logged out successfully', 'success');
}

async function loadUser() {
  if (!apiKey) return;

  try {
    currentUser = await apiCall('/auth/me');
    updateUI();
  } catch (error) {
    console.error('Failed to load user:', error);
    logout();
  }
}

// Project functions
async function loadProjects() {
  try {
    const projects = await apiCall('/projects/');
    displayProjects(projects);
  } catch (error) {
    console.error('Failed to load projects:', error);
    displayProjects([]);
  }
}

function displayProjects(projects) {
  const container = projectList.querySelector('.card') || projectList;
  container.innerHTML = projects.length === 0
    ? '<div class="card">No projects found. Be the first to create one!</div>'
    : projects.map(project => `
        <div class="card">
          <h3>${project.title}</h3>
          <p>${project.summary || 'No summary available'}</p>
          <div class="tags">${(project.tags || []).map(tag => `<span>${tag}</span>`).join('')}</div>
          <button onclick="selectProject('${project.id}')">Manage Devices & Firmware</button>
        </div>
      `).join('');
}

async function createProject() {
  const title = document.getElementById('project-title').value.trim();
  const summary = document.getElementById('project-summary').value.trim();
  const description = document.getElementById('project-description').value.trim();
  const tagsInput = document.getElementById('project-tags').value.trim();

  if (!title) {
    showMessage('Project title is required');
    return;
  }

  const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag) : [];

  try {
    const project = await apiCall('/projects/', {
      method: 'POST',
      body: { title, summary, description, tags },
    });

    // Clear form
    document.getElementById('project-title').value = '';
    document.getElementById('project-summary').value = '';
    document.getElementById('project-description').value = '';
    document.getElementById('project-tags').value = '';

    showMessage('Project created successfully!', 'success');
    loadProjects(); // Refresh the project list
  } catch (error) {
    showMessage(`Failed to create project: ${error.message}`);
  }
}

// ===== DEVICE MANAGEMENT =====

let currentProjectId = null;

function switchTab(tab) {
  // Update tab buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');

  // Hide all tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.style.display = 'none';
  });

  // Show selected tab
  if (tab === 'projects') {
    document.getElementById('project-list').style.display = 'block';
  } else if (tab === 'devices') {
    document.getElementById('devices-section').style.display = 'block';
    loadDevices();
    loadFirmware();
  } else if (tab === 'boms') {
    document.getElementById('boms-section').style.display = 'block';
    loadBOMs();
  }
}

async function registerDevice() {
  const name = document.getElementById('device-name').value.trim();
  const type = document.getElementById('device-type').value.trim();
  const uniqueId = document.getElementById('device-unique-id').value.trim();

  if (!name || !type || !uniqueId) {
    showMessage('Please fill in all device fields');
    return;
  }

  if (!currentProjectId) {
    showMessage('Please select a project first');
    return;
  }

  try {
    const device = await apiCall(`/api/devices/devices?project_id=${currentProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        name,
        device_type: type,
        unique_id: uniqueId,
        config: {}
      }
    });

    document.getElementById('device-name').value = '';
    document.getElementById('device-type').value = '';
    document.getElementById('device-unique-id').value = '';

    showMessage('Device registered successfully!', 'success');
    loadDevices();
  } catch (error) {
    showMessage(`Failed to register device: ${error.message}`);
  }
}

async function loadDevices() {
  if (!currentProjectId) return;

  try {
    const devices = await apiCall(`/api/devices/devices?project_id=${currentProjectId}`);
    displayDevices(devices);
  } catch (error) {
    console.error('Failed to load devices:', error);
    document.getElementById('devices-container').innerHTML =
      '<p>Error loading devices</p>';
  }
}

function displayDevices(devices) {
  const container = document.getElementById('devices-container');

  if (devices.length === 0) {
    container.innerHTML = '<p>No devices registered yet</p>';
    return;
  }

  container.innerHTML = devices
    .map(device => `
      <div class="device-card">
        <h4>${device.name}</h4>
        <p><strong>Type:</strong> ${device.device_type}</p>
        <p><strong>Unique ID:</strong> ${device.unique_id}</p>
        <p><strong>Status:</strong> <span class="status-${device.status}">${device.status}</span></p>
        <p><strong>Firmware:</strong> ${device.firmware_version || 'Not deployed'}</p>
        ${device.last_seen ? `<p><strong>Last Seen:</strong> ${new Date(device.last_seen).toLocaleString()}</p>` : ''}
        <button onclick="deleteDevice('${device.id}')">Delete</button>
      </div>
    `)
    .join('');
}

async function deleteDevice(deviceId) {
  if (!confirm('Are you sure you want to delete this device?')) return;

  try {
    await apiCall(`/api/devices/devices/${deviceId}`, {
      method: 'DELETE'
    });

    showMessage('Device deleted', 'success');
    loadDevices();
  } catch (error) {
    showMessage(`Failed to delete device: ${error.message}`);
  }
}

async function uploadFirmware() {
  const version = document.getElementById('firmware-version').value.trim();
  const releaseNotes = document.getElementById('firmware-release-notes').value.trim();
  const binaryUrl = document.getElementById('firmware-binary-url').value.trim();
  const isStable = document.getElementById('firmware-is-stable').checked;

  if (!version || !binaryUrl) {
    showMessage('Please fill in version and binary URL');
    return;
  }

  if (!currentProjectId) {
    showMessage('Please select a project first');
    return;
  }

  try {
    const firmware = await apiCall(`/api/devices/firmware?project_id=${currentProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        version,
        description: releaseNotes,
        binary_url: binaryUrl,
        is_stable: isStable
      }
    });

    document.getElementById('firmware-version').value = '';
    document.getElementById('firmware-release-notes').value = '';
    document.getElementById('firmware-binary-url').value = '';
    document.getElementById('firmware-is-stable').checked = false;

    showMessage('Firmware version uploaded!', 'success');
    loadFirmware();
  } catch (error) {
    showMessage(`Failed to upload firmware: ${error.message}`);
  }
}

async function loadFirmware() {
  if (!currentProjectId) return;

  try {
    const versions = await apiCall(`/api/devices/firmware?project_id=${currentProjectId}`);
    displayFirmware(versions);
  } catch (error) {
    console.error('Failed to load firmware:', error);
    document.getElementById('firmware-container').innerHTML =
      '<p>Error loading firmware versions</p>';
  }
}

function displayFirmware(versions) {
  const container = document.getElementById('firmware-container');

  if (versions.length === 0) {
    container.innerHTML = '<p>No firmware versions uploaded yet</p>';
    return;
  }

  container.innerHTML = versions
    .map(fw => `
      <div class="firmware-card">
        <h4>v${fw.version} ${fw.is_stable ? '<span class="badge-stable">Stable</span>' : ''}</h4>
        <p><strong>URL:</strong> <code>${fw.binary_url}</code></p>
        ${fw.release_notes ? `<p><strong>Notes:</strong> ${fw.release_notes}</p>` : ''}
        <p><strong>Uploaded:</strong> ${new Date(fw.created_at).toLocaleString()}</p>
        ${fw.size_bytes ? `<p><strong>Size:</strong> ${(fw.size_bytes / 1024 / 1024).toFixed(2)} MB</p>` : ''}
      </div>
    `)
    .join('');
}

// ===== PROJECT SELECTION =====

async function selectProject(projectId) {
  currentProjectId = projectId;
  document.getElementById('device-project-id').value = projectId;
  document.getElementById('firmware-project-id').value = projectId;
  document.getElementById('bom-project-id').value = projectId;
  switchTab('devices');
}

// ===== BOM (BILL OF MATERIALS) MANAGEMENT =====

let currentBOMId = null;
let currentBOMItems = [];

async function createBOM() {
  const name = document.getElementById('bom-name').value.trim();
  const version = document.getElementById('bom-version').value.trim();
  const description = document.getElementById('bom-description').value.trim();
  const deviceId = document.getElementById('bom-device-id').value || null;

  if (!name || !version) {
    showMessage('Please fill in BOM name and version');
    return;
  }

  if (!currentProjectId) {
    showMessage('Please select a project first');
    return;
  }

  try {
    const bom = await apiCall(`/api/boms/boms?project_id=${currentProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        name,
        version,
        description,
        device_id: deviceId
      }
    });

    document.getElementById('bom-name').value = '';
    document.getElementById('bom-version').value = '';
    document.getElementById('bom-description').value = '';
    
    showMessage('BOM created successfully!', 'success');
    loadBOMs();
  } catch (error) {
    showMessage(`Failed to create BOM: ${error.message}`);
  }
}

async function loadBOMs() {
  if (!currentProjectId) return;

  try {
    const boms = await apiCall(`/api/boms/boms?project_id=${currentProjectId}`);
    displayBOMs(boms);
  } catch (error) {
    console.error('Failed to load BOMs:', error);
    document.getElementById('boms-container').innerHTML = '<p>Error loading BOMs</p>';
  }
}

function displayBOMs(boms) {
  const container = document.getElementById('boms-container');

  if (boms.length === 0) {
    container.innerHTML = '<p>No BOMs created yet. Create one to get started!</p>';
    return;
  }

  container.innerHTML = boms
    .map(bom => `
      <div class="bom-card">
        <h4>${bom.name}</h4>
        <p><strong>Version:</strong> ${bom.version}</p>
        ${bom.description ? `<p><strong>Description:</strong> ${bom.description}</p>` : ''}
        <p><strong>Items:</strong> ${bom.items ? bom.items.length : 0}</p>
        ${bom.estimated_cost ? `<p><strong>Estimated Cost:</strong> $${bom.estimated_cost.toFixed(2)}</p>` : ''}
        <button onclick="editBOM('${bom.id}')">Edit</button>
        <button onclick="duplicateBOM('${bom.id}')">Duplicate</button>
      </div>
    `)
    .join('');
}

async function editBOM(bomId) {
  currentBOMId = bomId;
  
  try {
    const bom = await apiCall(`/api/boms/boms/${bomId}`);
    currentBOMItems = bom.items || [];
    
    document.getElementById('bom-editor-title').textContent = `Edit BOM: ${bom.name}`;
    document.getElementById('bom-info-version').textContent = bom.version;
    document.getElementById('bom-item-count').textContent = bom.items ? bom.items.length : 0;
    
    // Calculate total cost
    const totalCost = (bom.items || []).reduce((sum, item) => {
      return sum + ((item.unit_price || 0) * item.quantity);
    }, 0);
    document.getElementById('bom-total-cost').textContent = totalCost.toFixed(2);
    
    displayBOMItems(currentBOMItems);
    
    document.getElementById('bom-list').style.display = 'none';
    document.getElementById('add-item-section').style.display = 'block';
    document.getElementById('bom-editor').style.display = 'block';
  } catch (error) {
    showMessage(`Failed to load BOM: ${error.message}`);
  }
}

function displayBOMItems(items) {
  const container = document.getElementById('items-container');

  if (items.length === 0) {
    container.innerHTML = '<p>No items in this BOM yet</p>';
    return;
  }

  container.innerHTML = items
    .map(item => `
      <div class="bom-item-card">
        <div class="item-header">
          <span class="item-ref">${item.reference}</span>
          <span class="item-qty">Qty: ${item.quantity}</span>
          ${item.unit_price ? `<span class="item-price">$${(item.unit_price * item.quantity).toFixed(2)}</span>` : ''}
        </div>
        <p><strong>${item.description}</strong></p>
        ${item.part_number ? `<p>Part: ${item.part_number}</p>` : ''}
        ${item.manufacturer ? `<p>Mfg: ${item.manufacturer}</p>` : ''}
        ${item.supplier ? `<p>Supplier: ${item.supplier}</p>` : ''}
        ${item.datasheet_url ? `<p><a href="${item.datasheet_url}" target="_blank">Datasheet</a></p>` : ''}
        <button onclick="deleteItem('${item.id}')">Delete</button>
      </div>
    `)
    .join('');
}

async function addBOMItem() {
  const reference = document.getElementById('item-reference').value.trim();
  const description = document.getElementById('item-description').value.trim();
  const quantity = parseInt(document.getElementById('item-quantity').value) || 1;
  const partNumber = document.getElementById('item-part-number').value.trim();
  const manufacturer = document.getElementById('item-manufacturer').value.trim();
  const unitPrice = parseFloat(document.getElementById('item-unit-price').value) || null;
  const supplier = document.getElementById('item-supplier').value.trim();
  const datasteetUrl = document.getElementById('item-datasheet-url').value.trim();
  const notes = document.getElementById('item-notes').value.trim();

  if (!reference || !description) {
    showMessage('Reference and description are required');
    return;
  }

  if (!currentBOMId) {
    showMessage('No BOM selected');
    return;
  }

  try {
    const item = await apiCall(`/api/boms/boms/${currentBOMId}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        reference,
        description,
        quantity,
        part_number: partNumber,
        manufacturer,
        unit_price: unitPrice,
        supplier,
        datasheet_url: datasteetUrl,
        notes
      }
    });

    currentBOMItems.push(item);
    displayBOMItems(currentBOMItems);
    
    // Clear form
    document.getElementById('item-reference').value = '';
    document.getElementById('item-description').value = '';
    document.getElementById('item-quantity').value = '1';
    document.getElementById('item-part-number').value = '';
    document.getElementById('item-manufacturer').value = '';
    document.getElementById('item-unit-price').value = '';
    document.getElementById('item-supplier').value = '';
    document.getElementById('item-datasheet-url').value = '';
    document.getElementById('item-notes').value = '';

    showMessage('Component added to BOM!', 'success');
  } catch (error) {
    showMessage(`Failed to add item: ${error.message}`);
  }
}

async function deleteItem(itemId) {
  if (!confirm('Delete this component?')) return;

  try {
    await apiCall(`/api/boms/bom-items/${itemId}`, {
      method: 'DELETE'
    });

    currentBOMItems = currentBOMItems.filter(item => item.id !== itemId);
    displayBOMItems(currentBOMItems);
    
    showMessage('Component removed', 'success');
  } catch (error) {
    showMessage(`Failed to delete item: ${error.message}`);
  }
}

async function searchComponentLibrary() {
  const query = document.getElementById('library-search-query').value.trim();

  if (!query || query.length < 2) {
    showMessage('Enter at least 2 characters to search');
    return;
  }

  try {
    const results = await apiCall(`/api/boms/library/search?q=${encodeURIComponent(query)}`);
    displayLibrarySearchResults(results);
  } catch (error) {
    console.error('Library search failed:', error);
    document.getElementById('library-search-results').innerHTML = '<p>No components found</p>';
  }
}

function displayLibrarySearchResults(components) {
  const container = document.getElementById('library-search-results');

  if (components.length === 0) {
    container.innerHTML = '<p>No components found in library</p>';
    return;
  }

  container.innerHTML = components
    .map(comp => `
      <div class="library-component-card">
        <h5>${comp.name}</h5>
        <p><strong>Part Number:</strong> ${comp.part_number}</p>
        ${comp.manufacturer ? `<p><strong>Manufacturer:</strong> ${comp.manufacturer}</p>` : ''}
        ${comp.package_type ? `<p><strong>Package:</strong> ${comp.package_type}</p>` : ''}
        ${comp.datasheet_url ? `<p><a href="${comp.datasheet_url}" target="_blank">View Datasheet</a></p>` : ''}
      </div>
    `)
    .join('');
}

async function forkBOM() {
  if (!currentBOMId) return;

  const newName = prompt('New BOM name (for variant):');
  const newVersion = prompt('New version:');

  if (!newName || !newVersion) return;

  try {
    await apiCall(`/api/boms/boms/${currentBOMId}/fork`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        new_name: newName,
        new_version: newVersion,
        new_device_id: null
      }
    });

    showMessage('BOM forked successfully!', 'success');
    closeBOMEditor();
  } catch (error) {
    showMessage(`Failed to fork BOM: ${error.message}`);
  }
}

function closeBOMEditor() {
  currentBOMId = null;
  currentBOMItems = [];
  document.getElementById('bom-editor').style.display = 'none';
  document.getElementById('bom-list').style.display = 'block';
  loadBOMs();
}

async function duplicateBOM(bomId) {
  const newName = prompt('New BOM name:');
  const newVersion = prompt('New version:');

  if (!newName || !newVersion) return;

  try {
    await apiCall(`/api/boms/boms/${bomId}/fork`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        new_name: newName,
        new_version: newVersion
      }
    });

    showMessage('BOM duplicated!', 'success');
    loadBOMs();
  } catch (error) {
    showMessage(`Failed to duplicate BOM: ${error.message}`);
  }
}
function updateUI() {
  if (currentUser) {
    authButton.style.display = 'none';
    loginForm.style.display = 'none';
    registerForm.style.display = 'none';
    userInfo.style.display = 'block';
    userDisplay.textContent = `Hello, ${currentUser.display_name || currentUser.username}!`;
    createProjectSection.style.display = 'block';
    document.getElementById('tabs').style.display = 'block';
  } else {
    authButton.style.display = 'inline-block';
    loginForm.style.display = 'none';
    registerForm.style.display = 'none';
    userInfo.style.display = 'none';
    createProjectSection.style.display = 'none';
    document.getElementById('tabs').style.display = 'none';
  }
}

// Initialize the app
async function init() {
  console.log('init() - apiKey from localStorage:', localStorage.getItem('makergit_api_key') || 'NOT FOUND');
  updateUI();
  await loadUser();
  await loadProjects();
}

// Start the app when the page loads
document.addEventListener('DOMContentLoaded', init);
