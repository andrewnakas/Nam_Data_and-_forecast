// Global variables
let forecastData = null;
let charts = {
    temp: null,
    wind: null,
    precip: null
};

// Set location from preset buttons
function setLocation(lat, lon) {
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lon;
}

// Show/hide tabs
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');

    // Update charts if charts tab is selected
    if (tabName === 'charts' && forecastData) {
        updateCharts();
    }
}

// Fetch forecast data from backend
async function fetchForecast() {
    const lat = document.getElementById('latitude').value;
    const lon = document.getElementById('longitude').value;
    const hours = document.getElementById('hours').value;

    const statusDiv = document.getElementById('status');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const modelInfoDiv = document.getElementById('modelInfo');

    // Clear previous results
    statusDiv.innerHTML = '';
    statusDiv.className = 'status';
    resultsDiv.style.display = 'none';
    modelInfoDiv.style.display = 'none';

    // Show loading
    loadingDiv.style.display = 'block';

    try {
        const response = await fetch(`/api/forecast?lat=${lat}&lon=${lon}&hours=${hours}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch forecast');
        }

        forecastData = await response.json();

        // Hide loading
        loadingDiv.style.display = 'none';

        // Show success message
        statusDiv.className = 'status success';
        statusDiv.innerHTML = `Forecast data loaded successfully! ${forecastData.hourly_data.length} hours of data retrieved.`;

        // Show model info
        modelInfoDiv.style.display = 'block';
        const modelTime = new Date(forecastData.model_run);
        modelInfoDiv.innerHTML = `
            <h3>Model Information</h3>
            <p><strong>Model Run:</strong> ${modelTime.toUTCString()}</p>
            <p><strong>Location:</strong> ${forecastData.location.lat.toFixed(4)}°N, ${Math.abs(forecastData.location.lon).toFixed(4)}°${forecastData.location.lon < 0 ? 'W' : 'E'}</p>
            <p><strong>Forecast Hours:</strong> ${forecastData.hourly_data.length}</p>
        `;

        // Show results
        resultsDiv.style.display = 'block';

        // Display surface data
        displaySurfaceData();

        // Display level data
        updateLevelDisplay();

    } catch (error) {
        loadingDiv.style.display = 'none';
        statusDiv.className = 'status error';
        statusDiv.innerHTML = `Error: ${error.message}`;
        console.error('Error fetching forecast:', error);
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
    html += '<th>Wind Speed (m/s)</th>';
    html += '<th>Wind Dir (°)</th>';
    html += '<th>Wind U (m/s)</th>';
    html += '<th>Wind V (m/s)</th>';
    html += '<th>Precip (mm)</th>';
    html += '</tr></thead><tbody>';

    forecastData.hourly_data.forEach(hour => {
        const validTime = new Date(hour.valid_time);
        const surface = hour.surface || {};

        html += '<tr>';
        html += `<td>${validTime.toUTCString()}</td>`;
        html += `<td>F${String(hour.forecast_hour).padStart(3, '0')}</td>`;
        html += `<td>${surface.temperature_2m?.toFixed(1) || surface.temperature_surface?.toFixed(1) || 'N/A'}</td>`;
        html += `<td>${surface.wind_speed_10m?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${surface.wind_direction_10m?.toFixed(0) || 'N/A'}${surface.wind_direction_10m ? '°' : ''}</td>`;
        html += `<td>${surface.wind_u_10m?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${surface.wind_v_10m?.toFixed(2) || 'N/A'}</td>`;
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
    html += '<th>Wind Speed (m/s)</th>';
    html += '<th>Wind Dir (°)</th>';
    html += '<th>Wind U (m/s)</th>';
    html += '<th>Wind V (m/s)</th>';
    html += '<th>RH (%)</th>';
    html += '<th>Height (m)</th>';
    html += '</tr></thead><tbody>';

    forecastData.hourly_data.forEach(hour => {
        const validTime = new Date(hour.valid_time);
        const levelData = hour.levels?.[selectedLevel] || {};

        html += '<tr>';
        html += `<td>${validTime.toUTCString()}</td>`;
        html += `<td>F${String(hour.forecast_hour).padStart(3, '0')}</td>`;
        html += `<td>${levelData.temperature?.toFixed(1) || 'N/A'}</td>`;
        html += `<td>${levelData.wind_speed?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${levelData.wind_direction?.toFixed(0) || 'N/A'}${levelData.wind_direction ? '°' : ''}</td>`;
        html += `<td>${levelData.wind_u?.toFixed(2) || 'N/A'}</td>`;
        html += `<td>${levelData.wind_v?.toFixed(2) || 'N/A'}</td>`;
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

    // Temperature chart
    const temps = forecastData.hourly_data.map(h => h.surface.temperature_2m || h.surface.temperature_surface || null);
    updateTempChart(labels, temps);

    // Wind chart
    const windSpeeds = forecastData.hourly_data.map(h => h.surface.wind_speed_10m || null);
    const windDirs = forecastData.hourly_data.map(h => h.surface.wind_direction_10m || null);
    updateWindChart(labels, windSpeeds, windDirs);

    // Precipitation chart
    const precip = forecastData.hourly_data.map(h => h.surface.precipitation || h.surface.precipitation_rate || null);
    updatePrecipChart(labels, precip);
}

function updateTempChart(labels, data) {
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
                data: data,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
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
                },
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Forecast Time (UTC)'
                    }
                }
            }
        }
    });
}

function updateWindChart(labels, speeds, directions) {
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
                data: speeds,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                yAxisID: 'y',
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
                },
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Wind Speed (m/s)'
                    },
                    beginAtZero: true
                },
                x: {
                    title: {
                        display: true,
                        text: 'Forecast Time (UTC)'
                    }
                }
            }
        }
    });
}

function updatePrecipChart(labels, data) {
    const ctx = document.getElementById('precipChart').getContext('2d');

    if (charts.precip) {
        charts.precip.destroy();
    }

    charts.precip = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Precipitation (mm)',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Precipitation Forecast',
                    font: { size: 16 }
                },
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Precipitation (mm)'
                    },
                    beginAtZero: true
                },
                x: {
                    title: {
                        display: true,
                        text: 'Forecast Time (UTC)'
                    }
                }
            }
        }
    });
}

// Check API status on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        if (status.status === 'available') {
            console.log('NAM data available. Latest run:', status.latest_run);
        } else {
            console.warn('NAM data unavailable');
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
});
