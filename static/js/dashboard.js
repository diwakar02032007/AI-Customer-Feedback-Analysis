// ========================================================
// InsightAI - Dashboard Charts Controller (7 Data-Driven Charts)
// Renders Sentiment, Trends, Categories, Ratings, Emotions,
// Priority Severity, and Aspect-Based Sentiment Analysis
// ========================================================

document.addEventListener('DOMContentLoaded', async function () {
    const trendCanvas = document.getElementById('dashboardTrendChart');
    const sentimentDistCanvas = document.getElementById('dashboardSentimentDistChart');
    const categoryCanvas = document.getElementById('dashboardCategoryChart');
    const ratingCanvas = document.getElementById('dashboardRatingChart');
    const aspectCanvas = document.getElementById('dashboardAspectChart');
    const emotionCanvas = document.getElementById('dashboardEmotionChart');
    const priorityCanvas = document.getElementById('dashboardPriorityChart');

    if (!trendCanvas && !sentimentDistCanvas && !categoryCanvas) return;

    try {
        const response = await fetch('/api/analytics-data');
        if (!response.ok) return;
        const data = await response.json();

        // 1. Sentiment Trends Over Time (Smooth Line / Area)
        if (trendCanvas) {
            const hasTrends = data.trends && data.trends.labels && data.trends.labels.length > 0;
            const labels = hasTrends ? data.trends.labels : ['No Data'];
            const posData = hasTrends ? data.trends.positive : [0];
            const negData = hasTrends ? data.trends.negative : [0];
            const neuData = hasTrends ? data.trends.neutral : [0];

            new Chart(trendCanvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Positive',
                            data: posData,
                            borderColor: InsightChartColors.emerald,
                            backgroundColor: InsightChartColors.emeraldSoft,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointHoverRadius: 7
                        },
                        {
                            label: 'Negative',
                            data: negData,
                            borderColor: InsightChartColors.rose,
                            backgroundColor: InsightChartColors.roseSoft,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointHoverRadius: 7
                        },
                        {
                            label: 'Neutral',
                            data: neuData,
                            borderColor: InsightChartColors.slate,
                            backgroundColor: 'transparent',
                            borderDash: [4, 4],
                            tension: 0.35,
                            borderWidth: 1.5,
                            pointRadius: 2
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

        // 2. Sentiment Distribution Donut Chart
        if (sentimentDistCanvas) {
            const pos = data.kpis.positive_feedback || 0;
            const neu = data.kpis.neutral_feedback || 0;
            const neg = data.kpis.negative_feedback || 0;
            const hasSent = (pos + neu + neg) > 0;

            new Chart(sentimentDistCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: hasSent ? [pos, neu, neg] : [0, 1, 0],
                        backgroundColor: [
                            InsightChartColors.emerald,
                            InsightChartColors.slate,
                            InsightChartColors.rose
                        ],
                        borderWidth: 3,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 14,
                                font: { weight: '600', size: 12 }
                            }
                        }
                    }
                }
            });
        }

        // 3. Feedback Category Distribution Bar Chart
        if (categoryCanvas) {
            const hasCats = data.categories && data.categories.labels && data.categories.labels.length > 0;
            new Chart(categoryCanvas, {
                type: 'bar',
                data: {
                    labels: hasCats ? data.categories.labels : ['No Categories'],
                    datasets: [{
                        label: 'Feedback Volume',
                        data: hasCats ? data.categories.counts : [0],
                        backgroundColor: InsightChartColors.palette,
                        borderRadius: 6,
                        maxBarThickness: 32
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#f1f5f9' },
                            ticks: { precision: 0 }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11, weight: '500' } }
                        }
                    }
                }
            });
        }

        // 4. Rating Distribution (1 to 5 Stars) Bar Chart
        if (ratingCanvas) {
            const hasRatings = data.ratings && data.ratings.labels && data.ratings.labels.length > 0;
            new Chart(ratingCanvas, {
                type: 'bar',
                data: {
                    labels: hasRatings ? data.ratings.labels : ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
                    datasets: [{
                        label: 'Customer Ratings',
                        data: hasRatings ? data.ratings.counts : [0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#ef4444', // 1 star - red
                            '#f97316', // 2 star - orange
                            '#eab308', // 3 star - yellow
                            '#84cc16', // 4 star - lime
                            '#10b981'  // 5 star - emerald
                        ],
                        borderRadius: 6,
                        maxBarThickness: 28
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
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

        // 5. Aspect-Based Sentiment Analysis Grouped Bar Chart
        if (aspectCanvas) {
            const hasAspects = data.aspects && data.aspects.labels && data.aspects.labels.length > 0;
            new Chart(aspectCanvas, {
                type: 'bar',
                data: {
                    labels: hasAspects ? data.aspects.labels : ['UI/UX', 'Support', 'Pricing', 'Quality'],
                    datasets: [
                        {
                            label: 'Positive',
                            data: hasAspects ? data.aspects.positive : [0, 0, 0, 0],
                            backgroundColor: InsightChartColors.emerald,
                            borderRadius: 4,
                            maxBarThickness: 16
                        },
                        {
                            label: 'Negative',
                            data: hasAspects ? data.aspects.negative : [0, 0, 0, 0],
                            backgroundColor: InsightChartColors.rose,
                            borderRadius: 4,
                            maxBarThickness: 16
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

        // 6. Customer Emotion Distribution Donut
        if (emotionCanvas) {
            const hasEmotions = data.emotions && data.emotions.labels && data.emotions.labels.length > 0;
            new Chart(emotionCanvas, {
                type: 'doughnut',
                data: {
                    labels: hasEmotions ? data.emotions.labels : ['Neutral'],
                    datasets: [{
                        data: hasEmotions ? data.emotions.counts : [1],
                        backgroundColor: [
                            '#10b981', // Joy
                            '#64748b', // Neutral
                            '#f43f5e', // Anger
                            '#3b82f6', // Sadness
                            '#8b5cf6', // Surprise
                            '#f59e0b'  // Fear
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '68%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 10,
                                font: { size: 12, weight: '600' }
                            }
                        }
                    }
                }
            });
        }

        // 7. Priority Distribution Bar Chart
        if (priorityCanvas) {
            const hasPriorities = data.priorities && data.priorities.labels && data.priorities.labels.length > 0;
            new Chart(priorityCanvas, {
                type: 'bar',
                data: {
                    labels: hasPriorities ? data.priorities.labels : ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        label: 'Tickets',
                        data: hasPriorities ? data.priorities.counts : [0, 0, 0, 0],
                        backgroundColor: [
                            '#991b1b', // Critical
                            '#ef4444', // High
                            '#f59e0b', // Medium
                            '#64748b'  // Low
                        ],
                        borderRadius: 6,
                        maxBarThickness: 32
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
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

    } catch (e) {
        console.error('Error fetching dashboard telemetry:', e);
    }
});
