// Client-side Application Logic for Project Tracker

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // 1. Dark / Light Theme Toggle Management
  // ==========================================
  const btnThemeToggle = document.getElementById('btn-theme-toggle');
  const themeSun = document.getElementById('theme-sun');
  const themeMoon = document.getElementById('theme-moon');

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      themeSun.classList.remove('hidden');
      themeMoon.classList.add('hidden');
    } else {
      document.documentElement.classList.remove('dark');
      themeSun.classList.add('hidden');
      themeMoon.classList.remove('hidden');
    }
  }

  // Set initial theme based on localStorage, default to dark
  let currentTheme = localStorage.getItem('theme') || 'dark';
  applyTheme(currentTheme);

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener('click', () => {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', currentTheme);
      applyTheme(currentTheme);
      updateChartThemeColors(currentTheme);
    });
  }

  function updateChartThemeColors(theme) {
    const labelColor = theme === 'dark' ? '#94a3b8' : '#475569';
    const gridColor = theme === 'dark' ? 'rgba(51, 65, 85, 0.2)' : 'rgba(148, 163, 184, 0.18)';
    const gridBorderColor = theme === 'dark' ? 'rgba(51, 65, 85, 0.4)' : '#e2e8f0';

    if (window.earningsChart) {
      window.earningsChart.options.scales.y.grid.color = gridColor;
      window.earningsChart.options.scales.y.ticks.color = labelColor;
      window.earningsChart.options.scales.x.ticks.color = labelColor;
      window.earningsChart.update();
    }
    if (window.ratioChart) {
      window.ratioChart.options.plugins.legend.labels.color = labelColor;
      window.ratioChart.update();
    }
    if (window.timelineChart) {
      window.timelineChart.options.scales.x.grid.color = gridColor;
      window.timelineChart.options.scales.x.ticks.color = labelColor;
      window.timelineChart.options.scales.y.ticks.color = labelColor;
      window.timelineChart.update();
    }
  }

  // ==========================================
  // 2. DOM Dialog / Modal Handling
  // ==========================================
  const addDialog = document.getElementById('dialog-add-project');
  const editDialog = document.getElementById('dialog-edit-project');
  
  const btnOpenAdd = document.getElementById('btn-open-add-dialog');
  const btnCloseDialogs = document.querySelectorAll('.btn-close-dialog');
  
  function setAppInert(isInert) {
    const elementsToInert = ['header', 'main', 'footer'];
    elementsToInert.forEach(tag => {
      const el = document.querySelector(tag);
      if (el) {
        if (isInert) {
          el.setAttribute('inert', '');
        } else {
          el.removeAttribute('inert');
        }
      }
    });
  }

  if (btnOpenAdd && addDialog) {
    btnOpenAdd.addEventListener('click', () => {
      addDialog.showModal();
      setAppInert(true);
    });
  }

  btnCloseDialogs.forEach(btn => {
    btn.addEventListener('click', () => {
      if (addDialog && addDialog.open) addDialog.close();
      if (editDialog && editDialog.open) editDialog.close();
    });
  });

  if (addDialog) addDialog.addEventListener('close', () => setAppInert(false));
  if (editDialog) editDialog.addEventListener('close', () => setAppInert(false));

  // ==========================================
  // 3. Prepopulating the Edit Project Form
  // ==========================================
  const editTriggers = document.querySelectorAll('.btn-edit-trigger');
  const formEdit = document.getElementById('form-edit-project');

  editTriggers.forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      const title = btn.getAttribute('data-title');
      const type = btn.getAttribute('data-type');
      const startDate = btn.getAttribute('data-start-date');
      const endDate = btn.getAttribute('data-end-date');
      const earnings = btn.getAttribute('data-earnings');
      const status = btn.getAttribute('data-status');
      const tag = btn.getAttribute('data-tag');

      if (formEdit && editDialog) {
        formEdit.action = `/edit/${id}`;
        
        document.getElementById('edit-title').value = title;
        document.getElementById('edit-start-date').value = startDate;
        document.getElementById('edit-end-date').value = endDate;
        document.getElementById('edit-status').value = status;
        document.getElementById('edit-tag').value = tag || 'Other';

        if (type === 'Freelance') {
          document.getElementById('edit-type-freelance').checked = true;
          toggleEarningsInput('Freelance', 'edit');
          document.getElementById('edit-earnings').value = earnings;
        } else {
          document.getElementById('edit-type-personal').checked = true;
          toggleEarningsInput('Personal', 'edit');
          document.getElementById('edit-earnings').value = '0';
        }

        editDialog.showModal();
        setAppInert(true);
      }
    });
  });

  // ==========================================
  // 4. Form Date Constraint Validation
  // ==========================================
  const formAdd = document.getElementById('form-add-project');
  
  function validateDates(form, startInputId, endInputId) {
    const startInput = form.querySelector(`#${startInputId}`);
    const endInput = form.querySelector(`#${endInputId}`);
    
    if (startInput.value && endInput.value) {
      const startDate = new Date(startInput.value);
      const endDate = new Date(endInput.value);
      
      if (endDate < startDate) {
        endInput.setCustomValidity('End date must be on or after start date.');
      } else {
        endInput.setCustomValidity('');
      }
    }
  }

  const addStart = document.getElementById('add-start-date');
  const addEnd = document.getElementById('add-end-date');
  if (addStart && addEnd) {
    [addStart, addEnd].forEach(input => {
      input.addEventListener('change', () => {
        validateDates(formAdd, 'add-start-date', 'add-end-date');
      });
    });
  }

  const editStart = document.getElementById('edit-start-date');
  const editEnd = document.getElementById('edit-end-date');
  if (editStart && editEnd) {
    [editStart, editEnd].forEach(input => {
      input.addEventListener('change', () => {
        validateDates(formEdit, 'edit-start-date', 'edit-end-date');
      });
    });
  }

  document.querySelectorAll('input, select').forEach(input => {
    input.addEventListener('input', () => {
      input.setCustomValidity('');
    });
  });

  // ==========================================
  // 5. Delete Confirmation Handler
  // ==========================================
  document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const confirmDelete = confirm('Are you sure you want to delete this project? This action cannot be undone.');
      if (!confirmDelete) e.preventDefault();
    });
  });

  // ==========================================
  // 6. Ledger Filter Search
  // ==========================================
  const searchInput = document.getElementById('ledger-search');
  const tableRows = document.querySelectorAll('#table-ledger tbody tr');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      
      tableRows.forEach(row => {
        const titleEl = row.querySelector('[data-field="title"]');
        const tagEl = row.querySelector('[data-field="tag"]');
        if (titleEl) {
          const titleText = titleEl.textContent.toLowerCase();
          const tagText = tagEl ? tagEl.textContent.toLowerCase() : '';
          
          if (titleText.includes(query) || tagText.includes(query)) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        }
      });
    });
  }

  // ==========================================
  // 7. Chart.js Data Pull and Render
  // ==========================================
  fetch('/api/data')
    .then(response => response.json())
    .then(data => {
      renderComboChart(data);
      renderRatioChart(data);
      renderTimelineChart(data);
    })
    .catch(err => {
      console.error('Error fetching analytics data for charts:', err);
    });

  // Revenue Combo Chart (Bar + Cumulative Line)
  function renderComboChart(data) {
    const canvas = document.getElementById('chart-earnings');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Gradient fill for bars
    const gradientBar = ctx.createLinearGradient(0, 0, 0, 300);
    gradientBar.addColorStop(0, 'rgba(99, 102, 241, 0.85)'); // Indigo
    gradientBar.addColorStop(1, 'rgba(99, 102, 241, 0.15)');

    // Gradient fill for trend area
    const gradientLine = ctx.createLinearGradient(0, 0, 0, 300);
    gradientLine.addColorStop(0, 'rgba(139, 92, 246, 0.25)'); // Purple
    gradientLine.addColorStop(1, 'rgba(139, 92, 246, 0.01)');

    const labelColor = currentTheme === 'dark' ? '#94a3b8' : '#475569';
    const gridColor = currentTheme === 'dark' ? 'rgba(51, 65, 85, 0.2)' : 'rgba(148, 163, 184, 0.18)';

    window.earningsChart = new Chart(ctx, {
      data: {
        labels: data.freelance_labels,
        datasets: [
          {
            type: 'bar',
            label: 'Project Earnings',
            data: data.freelance_earnings,
            backgroundColor: gradientBar,
            borderColor: 'rgba(99, 102, 241, 0.9)',
            borderWidth: 1,
            borderRadius: 6,
            order: 2,
            maxBarThickness: 40
          },
          {
            type: 'line',
            label: 'Cumulative Revenue',
            data: data.freelance_cumulative,
            borderColor: '#8b5cf6', // Violet
            borderWidth: 3,
            pointBackgroundColor: '#8b5cf6',
            pointBorderColor: '#0b0f19',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: true,
            backgroundColor: gradientLine,
            tension: 0.35,
            order: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' },
              boxWidth: 12
            }
          },
          tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f1f5f9',
            bodyColor: '#f1f5f9',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 12,
            titleFont: { family: 'Plus Jakarta Sans', weight: 'bold' },
            bodyFont: { family: 'Plus Jakarta Sans' },
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: $${context.raw.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
              }
            }
          }
        },
        scales: {
          y: {
            grid: { color: gridColor },
            border: { dash: [5, 5] },
            ticks: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 11 },
              callback: function(value) { return '$' + value.toLocaleString(); }
            }
          },
          x: {
            grid: { display: false },
            ticks: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 11 }
            }
          }
        }
      }
    });
  }

  // Project Ratio Doughnut
  function renderRatioChart(data) {
    const canvas = document.getElementById('chart-ratio');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labelColor = currentTheme === 'dark' ? '#94a3b8' : '#475569';

    window.ratioChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.type_labels,
        datasets: [{
          data: data.type_values,
          backgroundColor: [
            'rgba(99, 102, 241, 0.85)', // Personal (Indigo)
            'rgba(16, 185, 129, 0.85)'  // Freelance (Emerald)
          ],
          borderColor: '#0b0f19',
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 12, weight: '500' },
              padding: 16,
              usePointStyle: true,
              pointStyle: 'circle'
            }
          },
          tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f1f5f9',
            bodyColor: '#f1f5f9',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 10,
            titleFont: { family: 'Plus Jakarta Sans', weight: 'bold' },
            bodyFont: { family: 'Plus Jakarta Sans' }
          }
        },
        cutout: '72%'
      }
    });
  }

  // Gantt Timeline Horizontal Floating Bar Chart
  function renderTimelineChart(data) {
    const canvas = document.getElementById('chart-timeline');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    const labelColor = currentTheme === 'dark' ? '#94a3b8' : '#475569';
    const gridColor = currentTheme === 'dark' ? 'rgba(51, 65, 85, 0.2)' : 'rgba(148, 163, 184, 0.18)';

    // Extract projects schedule data
    const projects = data.timeline_projects;
    const labels = projects.map(p => p.title);
    
    // Convert date strings to timestamps for custom float scale rendering
    const datasetsData = projects.map(p => {
      const start = new Date(p.start_date).getTime();
      const end = new Date(p.end_date).getTime();
      return [start, end];
    });

    // Color code chart bars by project status
    const backgroundColors = projects.map(p => {
      if (p.status === 'Completed') return 'rgba(16, 185, 129, 0.7)'; // Emerald
      if (p.status === 'In Progress') return 'rgba(245, 158, 11, 0.7)'; // Amber
      return 'rgba(148, 163, 184, 0.5)'; // Slate
    });

    const borderColors = projects.map(p => {
      if (p.status === 'Completed') return 'rgba(16, 185, 129, 1)';
      if (p.status === 'In Progress') return 'rgba(245, 158, 11, 1)';
      return 'rgba(148, 163, 184, 0.9)';
    });

    window.timelineChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Timeline',
          data: datasetsData,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1.5,
          borderRadius: 6,
          borderSkipped: false,
          barPercentage: 0.65
        }]
      },
      options: {
        indexAxis: 'y', // Renders bar chart horizontally
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f1f5f9',
            bodyColor: '#f1f5f9',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 12,
            titleFont: { family: 'Plus Jakarta Sans', weight: 'bold' },
            bodyFont: { family: 'Plus Jakarta Sans' },
            callbacks: {
              label: function(context) {
                const project = projects[context.dataIndex];
                const startStr = new Date(context.raw[0]).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
                const endStr = new Date(context.raw[1]).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
                return ` [${project.status}]  ${startStr} to ${endStr}`;
              }
            }
          }
        },
        scales: {
          x: {
            type: 'linear',
            grid: { color: gridColor },
            border: { dash: [5, 5] },
            ticks: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 10 },
              callback: function(value) {
                const date = new Date(value);
                return date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
              }
            }
          },
          y: {
            grid: { display: false },
            ticks: {
              color: labelColor,
              font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }
            }
          }
        }
      }
    });
  }

});
