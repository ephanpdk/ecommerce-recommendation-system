import { API, CLUSTERS, THEMES } from './config.js';
import { state, setMetrics } from './state.js';

export async function loadMetrics() {
    try {
        const res = await fetch(`${API}/cluster/metrics`);
        if(res.ok) {
            const data = await res.json();
            setMetrics(data);
        }
    } catch(e) {}
}

export function renderCharts() {
    const metrics = state.metrics;
    if(!metrics || !metrics.centroids_real) return;

    const silEl = document.getElementById('valSil');
    const inertiaEl = document.getElementById('valInertia');
    if(silEl) silEl.innerText = metrics.silhouette_score;
    if(inertiaEl) inertiaEl.innerText = Math.round(metrics.inertia);

    const ctxPca = document.getElementById('chart-pca');
    if(ctxPca && !state.charts.pca && metrics.advanced_viz) {
        const scatterData = metrics.advanced_viz.pca_scatter;
        const colors = ['#94a3b8', '#3b82f6', '#10b981', '#f59e0b'];
        const datasets = CLUSTERS.map((name, i) => ({
            label: name,
            data: scatterData.filter(d => d.cluster === i).map(d => ({x: d.x, y: d.y})),
            backgroundColor: colors[i]
        }));

        state.charts.pca = new Chart(ctxPca, {
            type: 'scatter',
            data: { datasets: datasets },
            options: { 
                maintainAspectRatio: false,
                scales: { x: {display:false}, y: {display:false} }, 
                plugins: { legend: {position:'bottom', labels: {usePointStyle: true}} } 
            }
        });
    }

    const ctxSil = document.getElementById('chart-silhouette');
    if(ctxSil && !state.charts.sil && metrics.advanced_viz) {
        state.charts.sil = new Chart(ctxSil, {
            type: 'bar',
            data: {
                labels: CLUSTERS,
                datasets: [{ label: 'Coefficient', data: metrics.advanced_viz.silhouette_per_cluster, backgroundColor: ['#94a3b8', '#3b82f6', '#10b981', '#f59e0b'] }]
            },
            options: { 
                maintainAspectRatio: false,
                indexAxis: 'y', 
                plugins: { legend: {display:false} }, 
                scales: { x: {min: -0.1, max: 1} } 
            }
        });
    }

    const ctxCorr = document.getElementById('chart-correlation');
    if(ctxCorr && !state.charts.corr && metrics.advanced_viz) {
        const corrData = metrics.advanced_viz.correlation_matrix;
        const bubbleData = [];
        const feats = ['Rec', 'Freq', 'Mon', 'View', 'Cart']; 
        
        for(let i=0; i<5; i++) {
            for(let j=0; j<5; j++) {
                const val = corrData[i][j];
                bubbleData.push({x: i, y: j, r: Math.abs(val)*10, v: val});
            }
        }

        state.charts.corr = new Chart(ctxCorr, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Correlation',
                    data: bubbleData,
                    backgroundColor: ctx => ctx.raw.v > 0 ? 'rgba(99, 102, 241, 0.7)' : 'rgba(244, 63, 94, 0.7)'
                }]
            },
            options: { 
                maintainAspectRatio: false, 
                plugins: { legend: {display:false}, tooltip: {callbacks: {label: (c)=> `Corr: ${c.raw.v}`}} },
                scales: { 
                    x: { type: 'category', labels: feats, grid: {display:false} },
                    y: { type: 'category', labels: feats, grid: {display:false} }
                }
            }
        });
    }

    const ctxImp = document.getElementById('chart-importance');
    if(ctxImp && !state.charts.imp && metrics.advanced_viz) {
        state.charts.imp = new Chart(ctxImp, {
            type: 'bar',
            data: {
                labels: metrics.advanced_viz.feature_importance.labels.slice(0,5),
                datasets: [{ label: 'Importance', data: metrics.advanced_viz.feature_importance.data.slice(0,5), backgroundColor: '#cbd5e1' }]
            },
            options: { 
                maintainAspectRatio: false,
                plugins: { legend: {display:false} } 
            }
        });
    }

    const ctxSim = document.getElementById('chart-similarity');
    if(ctxSim && !state.charts.sim) {
        state.charts.sim = new Chart(ctxSim, {
            type: 'line',
            data: {
                labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                datasets: [{ label: 'Rec. Match Rate', data: [5, 10, 25, 40, 20], fill: true, borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', tension: 0.4 }]
            },
            options: { 
                maintainAspectRatio: false,
                plugins: { legend: {display:false} }, 
                scales: { y: {display:false}, x: {grid:{display:false}} } 
            }
        });
    }

    const ctxElbow = document.getElementById('chart-elbow');
    if(ctxElbow) {
        if(state.charts.elbow) state.charts.elbow.destroy();
        state.charts.elbow = new Chart(ctxElbow.getContext('2d'), {
            type: 'line',
            data: {
                labels: Object.keys(metrics.elbow_curve),
                datasets: [{ label: 'Inertia', data: Object.values(metrics.elbow_curve), borderColor: '#4f46e5', tension: 0.3, pointBackgroundColor: '#4f46e5' }]
            },
            options: { 
                maintainAspectRatio: false,
                plugins: {legend:{display:false}}, 
                scales:{x:{grid:{display:false}}, y:{grid:{color:'#f1f5f9'}}} 
            }
        });
    }

    const ctxPie = document.getElementById('chart-pie');
    if(ctxPie) {
        if(state.charts.pie) state.charts.pie.destroy();
        state.charts.pie = new Chart(ctxPie.getContext('2d'), {
            type: 'doughnut',
            data: { labels: CLUSTERS, datasets: [{ data: Object.values(metrics.cluster_counts), backgroundColor: ['#94a3b8', '#3b82f6', '#10b981', '#f59e0b'], borderWidth:0 }] },
            options: { 
                maintainAspectRatio: false,
                cutout: '70%', 
                plugins: { legend: { position: 'bottom', labels:{usePointStyle:true, font:{size:10}} } } 
            }
        });
    }

    const ctxRadar = document.getElementById('chart-radar');
    if(ctxRadar) {
        if(state.charts.radar) state.charts.radar.destroy();
        state.charts.radar = new Chart(ctxRadar.getContext('2d'), {
            type: 'radar',
            data: { labels: metrics.feature_readable, datasets: metrics.centroids_scaled.map((d, i) => ({ label: CLUSTERS[i], data: d, borderColor: ['#94a3b8', '#3b82f6', '#10b981', '#f59e0b'][i], fill: false, borderWidth: 2, pointRadius: 0 })) },
            options: { 
                maintainAspectRatio: false,
                layout: { padding: 20 },
                scales: { 
                    r: { 
                        suggestedMin: -1, 
                        suggestedMax: 3, 
                        ticks: {display:false}, 
                        grid: {color:'#f1f5f9'},
                        pointLabels: { font: {size: 11, weight: 'bold'} } 
                    } 
                }, 
                plugins: { legend: { display: false } } 
            }
        });
    }

    const tableBody = document.getElementById('table-centroids');
    if(tableBody) {
            tableBody.innerHTML = metrics.centroids_real.map((c, i) => `
            <tr class="hover:bg-slate-50 border-b border-slate-50">
                <td class="px-6 py-2 font-bold text-[10px] uppercase ${THEMES[i].text}">${CLUSTERS[i]}</td>
                <td class="px-6 py-2 text-right font-mono text-[10px]">$${Math.round(c.Monetary)}</td>
                <td class="px-6 py-2 text-right font-mono text-[10px]">${Math.round(c.Frequency)}</td>
                <td class="px-6 py-2 text-right font-mono text-[10px]">${Math.round(c.Recency)}d</td>
                <td class="px-6 py-2 text-right font-mono text-[10px]">${Math.round(c.Page_Views)}</td>
            </tr>
        `).join('');
    }
}