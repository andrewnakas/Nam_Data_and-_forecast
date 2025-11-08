// Global variables
let forecastData = null;
let locationIndex = null;
let charts = {
    temp: null,
    wind: null
};

// Load location index on page load
window.addEventListener('load', async () => {
    await loadLocationIndex();
});

// Load the index of available locations
async function loadLocationIndex() {
    const statusDiv = document.getElementById('status');

    try {
        const response = await fetch('data/index.json');

        if (!response.ok) {
            throw new Error('Could not load location index');
        }

        locationIndex = await response.json();

        // Populate location dropdown
        const select = document.getElementById('locationSelect');
        select.innerHTML = '<option value="">-- Select a City --</option>';

        locationIndex.locations.forEach((loc, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = loc.name;
            if (loc.error) {
                option.textContent += ' (Data unavailable)';
                option.disabled = true;
            }
            select.appendChild(option);
        });

        // Show last update time
        const updateTime = new Date(locationIndex.last_updated);
        statusDiv.className = 'status success';
        statusDiv.innerHTML = `Data last updated: ${updateTime.toUTCString()}`;

        console.log(`Loaded ${locationIndex.locations.length} locations`);

    } catch (error) {
        statusDiv.className = 'status error';
        statusDiv.innerHTML = `Error loading location data: ${error.message}. The data may not be generated yet. GitHub Actions will update it every 6 hours.`;
        console.error('Error loading index:', error);
    }
}

// Load data for selected location
async function loadLocationData() {
    const select = document.getElementById('locationSelect');
    const selectedIndex = select.value;

    if (!selectedIndex) {
        document.getElementById('results').style.display = 'none';
        document.getElementById('modelInfo').style.display = 'none';
        return;
    }

    const location = locationIndex.locations[selectedIndex];
    const statusDiv = document.getElementById('status');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const modelInfoDiv = document.getElementById('modelInfo');

    if (location.error) {
        statusDiv.className = 'status error';
        statusDiv.innerHTML = `Data unavailable for ${location.name}: ${location.error}`;
        return;
    }

    // Show loading
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    modelInfoDiv.style.display = 'none';

    try {
        const response = await fetch(`data/${location.filename}`);

        if (!response.ok) {
            throw new Error(`Failed to load data file: ${response.status}`);
        }

        forecastData = await response.json();

        // Hide loading
        loadingDiv.style.display = 'none';

        // Show success message
        statusDiv.className = 'status success';
        statusDiv.innerHTML = `Loaded ${forecastData.hourly_data.length} hours of forecast data for ${forecastData.location_name}`;

        // Show model info
        modelInfoDiv.style.display = 'block';
        const modelTime = new Date(forecastData.model_run);
        modelInfoDiv.innerHTML = `
            <h3>Model Information</h3>
            <p><strong>Location:</strong> ${forecastData.location_name}</p>
            <p><strong>Coordinates:</strong> ${forecastData.location.lat.toFixed(4)}°N, ${Math.abs(forecastData.location.lon).toFixed(4)}°${forecastData.location.lon < 0 ? 'W' : 'E'}</p>
            <p><strong>Model Run:</strong> ${modelTime.toUTCString()}</p>
            <p><strong>Forecast Hours:</strong> ${forecastData.hourly_data.length}</p>
        `;

        // Show results
        resultsDiv.style.display = 'block';

        // Display data
        displaySurfaceData();
        updateLevelDisplay();

    } catch (error) {
        loadingDiv.style.display = 'none';
        statusDiv.className = 'status error';
        statusDiv.innerHTML = `Error loading forecast: ${error.message}`;
        console.error('Error loading location data:', error);
    }
}

// Refresh data - reload the index
async function refreshData() {
    document.getElementById('status').innerHTML = 'Refreshing...';
    await loadLocationIndex();
    const select = document.getElementById('locationSelect');
    if (select.value) {
        await loadLocationData();
    }
}

// Show/hide tabs
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    if (tabName === 'charts' && forecastData) {
        updateCharts();
    }
}

// Display surface weather data
function displaySurfaceData() {
    const surfaceDiv = document.getElementById('surfaceData');

    if (!forecastData || !forecastData.hourly_data) {
        surfaceDiv.innerHTML = '<p>No data available</p>';
        return;
    }

    let html = '<div class="data-table"><table>';
    html += '<thead><tr>';
    html += '<th>Valid Time (UTC)</th>';
    html += '<th>Hour</th>';
    html += '<th>Temp (°C)</th>';
    html += '<th>Temp (°F)</th>';
    html += '<th>Wind Speed (m/s)</th>';
    html += '<th>Wind Speed (mph)</th>';
    html += '<th>Wind Dir (°)</th>';
    html += '<th>Precip (mm)</th>';
    html += '</tr></thead><tbody>';

    forecastData.hourly_data.forEach(hour => {
        const validTime = new Date(hour.valid_time);
        const surface = hour.surface || {};

        const tempC = surface.temperature_2m || surface.temperature_surface;
        const tempF = tempC ? (tempC * 9/5 + 32).toFixed(1) : 'N/A';
        const windMs = surface.wind_speed_10m;
        const windMph = windMs ? (windMs * 2.23694).toFixed(1) : 'N/A';

        html += '<tr>';
        html += `<td>${validTime.toUTCString()}</td>`;
        html += `<td>F${String(hour.forecast_hour).padStart(3, '0')}</td>`;
        html += `<td>${tempC?.toFixed(1) || 'N/A'}</td>`;
        html += `<td>${tempF}</td>`;
        html += `<td>${windMs?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${windMph}</td>`;
        html += `<td>${surface.wind_direction_10m?.toFixed(0) || 'N/A'}${surface.wind_direction_10m ? '°' : ''}</td>`;
        html += `<td>${surface.precipitation?.toFixed(2) || surface.precipitation_rate?.toFixed(4) || 'N/A'}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    surfaceDiv.innerHTML = html;
}

// Update pressure level display
function updateLevelDisplay() {
    const levelDiv = document.getElementById('levelData');
    const selectedLevel = document.getElementById('levelSelect').value;

    if (!forecastData || !forecastData.hourly_data) {
        levelDiv.innerHTML = '<p>No data available</p>';
        return;
    }

    let html = '<div class="data-table"><table>';
    html += '<thead><tr>';
    html += '<th>Valid Time (UTC)</th>';
    html += '<th>Hour</th>';
    html += '<th>Temp (°C)</th>';
    html += '<th>Temp (°F)</th>';
    html += '<th>Wind Speed (m/s)</th>';
    html += '<th>Wind Speed (mph)</th>';
    html += '<th>Wind Dir (°)</th>';
    html += '<th>RH (%)</th>';
    html += '<th>Height (m)</th>';
    html += '</tr></thead><tbody>';

    forecastData.hourly_data.forEach(hour => {
        const validTime = new Date(hour.valid_time);
        const levelData = hour.levels?.[selectedLevel] || {};

        const tempC = levelData.temperature;
        const tempF = tempC ? (tempC * 9/5 + 32).toFixed(1) : 'N/A';
        const windMs = levelData.wind_speed;
        const windMph = windMs ? (windMs * 2.23694).toFixed(1) : 'N/A';

        html += '<tr>';
        html += `<td>${validTime.toUTCString()}</td>`;
        html += `<td>F${String(hour.forecast_hour).padStart(3, '0')}</td>`;
        html += `<td>${tempC?.toFixed(1) || 'N/A'}</td>`;
        html += `<td>${tempF}</td>`;
        html += `<td>${windMs?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${windMph}</td>`;
        html += `<td>${levelData.wind_direction?.toFixed(0) || 'N/A'}${levelData.wind_direction ? '°' : ''}</td>`;
        html += `<td>${levelData.relative_humidity?.toFixed(1) || 'N/A'}</td>`;
        html += `<td>${levelData.height?.toFixed(0) || 'N/A'}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    levelDiv.innerHTML = html;
}

// Update charts
function updateCharts() {
    if (!forecastData || !forecastData.hourly_data) return;

    const labels = forecastData.hourly_data.map(h => {
        const date = new Date(h.valid_time);
        return `${date.getUTCMonth()+1}/${date.getUTCDate()} ${String(date.getUTCHours()).padStart(2, '0')}Z`;
    });

    // Temperature chart (with Fahrenheit)
    const tempsC = forecastData.hourly_data.map(h => h.surface.temperature_2m || h.surface.temperature_surface || null);
    const tempsF = tempsC.map(t => t !== null ? (t * 9/5 + 32) : null);
    updateTempChart(labels, tempsC, tempsF);

    // Wind chart
    const windMs = forecastData.hourly_data.map(h => h.surface.wind_speed_10m || null);
    const windMph = windMs.map(w => w !== null ? (w * 2.23694) : null);
    updateWindChart(labels, windMs, windMph);

    // Precipitation chart
    const precip = forecastData.hourly_data.map(h => h.surface.precipitation || h.surface.precipitation_rate || null);
}

function updateTempChart(labels, dataC, dataF) {
    const ctx = document.getElementById('tempChart').getContext('2d');

    if (charts.temp) {
        charts.temp.destroy();
    }

    charts.temp = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: dataC,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                yAxisID: 'y',
                fill: true
            }, {
                label: 'Temperature (°F)',
                data: dataF,
                borderColor: 'rgb(255, 159, 64)',
                backgroundColor: 'rgba(255, 159, 64, 0.1)',
                tension: 0.4,
                yAxisID: 'y1',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Temperature Forecast',
                    font: { size: 16 }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: '°C' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: '°F' },
                    grid: { drawOnChartArea: false }
                },
                x: {
                    title: { display: true, text: 'Forecast Time (UTC)' }
                }
            }
        }
    });
}

function updateWindChart(labels, dataMs, dataMph) {
    const ctx = document.getElementById('windChart').getContext('2d');

    if (charts.wind) {
        charts.wind.destroy();
    }

    charts.wind = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wind Speed (m/s)',
                data: dataMs,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                yAxisID: 'y',
                fill: true
            }, {
                label: 'Wind Speed (mph)',
                data: dataMph,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                yAxisID: 'y1',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Wind Speed Forecast',
                    font: { size: 16 }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'm/s' },
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'mph' },
                    beginAtZero: true,
                    grid: { drawOnChartArea: false }
                },
                x: {
                    title: { display: true, text: 'Forecast Time (UTC)' }
                }
            }
        }
    });
}

// Check API status on load
window.addEventListener('load', async () => {
    try {
        await loadLocationIndex();
    } catch (error) {
        console.error('Error loading location index:', error);
    }
});
