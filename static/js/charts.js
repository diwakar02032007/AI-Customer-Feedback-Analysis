// ========================================================
// InsightAI - Chart.js Enterprise Styling & Defaults
// ========================================================

const InsightChartColors = {
    primary: '#4f46e5',
    primaryLight: '#c7d2fe',
    primarySoft: 'rgba(79, 70, 229, 0.08)',
    emerald: '#10b981',
    emeraldSoft: 'rgba(16, 185, 129, 0.12)',
    amber: '#f59e0b',
    amberSoft: 'rgba(245, 158, 11, 0.12)',
    rose: '#f43f5e',
    roseSoft: 'rgba(244, 63, 94, 0.12)',
    sky: '#0ea5e9',
    skySoft: 'rgba(14, 165, 233, 0.12)',
    slate: '#64748b',
    slateSoft: 'rgba(100, 116, 139, 0.1)',
    palette: ['#4f46e5', '#10b981', '#f59e0b', '#0ea5e9', '#ec4899', '#8b5cf6', '#64748b']
};

if (window.Chart) {
    Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif";
    Chart.defaults.color = '#64748b';
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
    Chart.defaults.plugins.tooltip.titleFont = { size: 13, weight: '700' };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 12, weight: '500' };
    Chart.defaults.plugins.tooltip.boxPadding = 6;
    Chart.defaults.plugins.tooltip.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.padding = 16;
}
