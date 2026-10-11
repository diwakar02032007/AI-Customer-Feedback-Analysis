// ========================================================
// InsightAI - Analytics Dashboard Charts
// ========================================================

document.addEventListener('DOMContentLoaded', async function () {
    const trendCanvas = document.getElementById('analyticsTrendChart');
    const emotionCanvas = document.getElementById('analyticsEmotionChart');
    const priorityCanvas = document.getElementById('analyticsPriorityChart');
    const languageCanvas = document.getElementById('analyticsLanguageChart');
    const ratingCanvas = document.getElementById('analyticsRatingChart');
    const aspectCanvas = document.getElementById('analyticsAspectChart');

    if (!trendCanvas && !emotionCanvas) return;

    // Check URL parameters for days
    const urlParams = new URLSearchParams(window.location.search);
    const daysParam = urlParams.get('days') || '30';

    try {
        const response = await fetch(`/api/analytics-data?days=${daysParam}`);
        if (!response.ok) return;
        const data = await response.json();

        // 1. Sentiment Trend Timeline Chart
        if (trendCanvas) {
            new Chart(trendCanvas, {
                type: 'line',
                data: {
                    labels: data.trends.labels.length ? data.trends.labels : ['Day 1', 'Day 2', 'Day 3', 'Day 4'],
                    datasets: [
                        {
                            label: 'Positive Sentiment',
                            data: data.trends.positive,
                            borderColor: InsightChartColors.emerald,
                            backgroundColor: InsightChartColors.emeraldSoft,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 3
                        },
                        {
                            label: 'Neutral Sentiment',
                            data: data.trends.neutral,
                            borderColor: InsightChartColors.slate,
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            tension: 0.35,
                            borderWidth: 1.5,
                            pointRadius: 0
                        },
                        {
                            label: 'Negative Sentiment',
                            data: data.trends.negative,
                            borderColor: InsightChartColors.rose,
                            backgroundColor: InsightChartColors.roseSoft,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', align: 'end' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { precision: 0 }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // 2. Star Rating Distribution Bar Chart
        if (ratingCanvas && data.ratings) {
            new Chart(ratingCanvas, {
                type: 'bar',
                data: {
                    labels: data.ratings.labels,
                    datasets: [{
                        label: 'Review Volume',
                        data: data.ratings.counts,
                        backgroundColor: [
                            '#ef4444', // 1 Star
                            '#f97316', // 2 Stars
                            '#f59e0b', // 3 Stars
                            '#10b981', // 4 Stars
                            '#059669'  // 5 Stars
                        ],
                        borderRadius: 6,
                        barThickness: 28
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { precision: 0 }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // 3. Aspect-Based Sentiment Grouped Bar Chart
        if (aspectCanvas && data.aspects) {
            new Chart(aspectCanvas, {
                type: 'bar',
                data: {
                    labels: data.aspects.labels,
                    datasets: [
                        {
                            label: 'Praise (Positive)',
                            data: data.aspects.positive,
                            backgroundColor: InsightChartColors.emerald,
                            borderRadius: 4
                        },
                        {
                            label: 'Complaints (Negative)',
                            data: data.aspects.negative,
                            backgroundColor: InsightChartColors.rose,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', align: 'end' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { precision: 0 }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // 4. Emotion Breakdown Donut Chart
        if (emotionCanvas) {
            new Chart(emotionCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.emotions.labels,
                    datasets: [{
                        data: data.emotions.counts,
                        backgroundColor: InsightChartColors.palette,
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    },
                    cutout: '68%'
                }
            });
        }

        // 5. Priority Distribution Bar Chart
        if (priorityCanvas) {
            const prioColors = {
                'Critical': '#dc2626',
                'High': '#ea580c',
                'Medium': '#0284c7',
                'Low': '#64748b'
            };
            const barColors = data.priorities.labels.map(l => prioColors[l] || InsightChartColors.primary);

            new Chart(priorityCanvas, {
                type: 'bar',
                data: {
                    labels: data.priorities.labels,
                    datasets: [{
                        label: 'Tickets',
                        data: data.priorities.counts,
                        backgroundColor: barColors,
                        borderRadius: 6,
                        barThickness: 28
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { precision: 0 }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // 6. Multilingual Language Distribution Pie Chart
        if (languageCanvas) {
            new Chart(languageCanvas, {
                type: 'pie',
                data: {
                    labels: data.languages.labels,
                    datasets: [{
                        data: data.languages.counts,
                        backgroundColor: ['#4f46e5', '#ec4899', '#06b6d4'],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    } catch (e) {
        console.error('InsightAI: Analytics charts render error:', e);
    }
});
