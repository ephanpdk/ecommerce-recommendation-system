import { CLUSTERS, THEMES } from './config.js';
import { renderAuth, handleLogin, handleRegister, switchAuthTab, logout } from './auth.js';
import { bindSliders, updateLiveSimulator, setPreset, resetSim, runPrediction } from './simulator.js';
import { loadMetrics, renderCharts } from './charts.js';
import { state, setSessionLogs } from './state.js';
import { toggleModal } from './utils.js';

export function switchView(viewName) {
    ['view-dashboard', 'view-insights', 'view-pipeline'].forEach(id => {
        const el = document.getElementById(id);
        if(el) el.classList.add('hidden');
    });

    const target = document.getElementById(`view-${viewName}`);
    if(target) target.classList.remove('hidden');

    ['nav-dashboard', 'nav-insights', 'nav-pipeline'].forEach(id => {
        const btn = document.getElementById(id);
        if(btn) btn.className = "px-4 py-1.5 rounded-md text-xs font-bold text-slate-500 hover:text-slate-700 transition flex items-center gap-2";
    });

    const activeBtn = document.getElementById(`nav-${viewName}`);
    if(activeBtn) {
        activeBtn.className = "px-4 py-1.5 rounded-md text-xs font-bold transition flex items-center gap-2 bg-indigo-600 text-white shadow-md";
    }

    if(viewName === 'insights') {
        if(!state.metrics) {
            loadMetrics().then(() => { setTimeout(renderCharts, 100); });
        } else setTimeout(renderCharts, 50);
    }
}

function init() {
    renderAuth();
    bindSliders();
    updateLiveSimulator();
    loadMetrics();

    const logs = localStorage.getItem('sessionLogs');
    if(logs) {
        try {
            const parsedLogs = JSON.parse(logs);
            setSessionLogs(parsedLogs);
            const table = document.getElementById('log-table');
            if(parsedLogs.length > 0 && table) {
                table.innerHTML = '';
                parsedLogs.forEach(l => {
                    table.innerHTML += `<tr class="hover:bg-slate-50 transition border-b border-slate-50"><td class="px-6 py-2 text-xs text-slate-400 font-mono">${l.time}</td><td class="px-6 py-2 text-xs font-bold ${THEMES[l.cluster].text}">${CLUSTERS[l.cluster]}</td><td class="px-6 py-2 text-xs text-right font-bold text-slate-600">$${l.money}</td><td class="px-6 py-2 text-center"><i class="fa-solid fa-check text-emerald-500 text-xs"></i></td></tr>`;
                });
            }
        } catch(e) {}
    }
}

// Bind functions to window to make them accessible from HTML onclick attributes
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.switchAuthTab = switchAuthTab;
window.logout = logout;
window.toggleModal = toggleModal;
window.switchView = switchView;
window.setPreset = setPreset;
window.resetSim = resetSim;
window.runPrediction = runPrediction;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);