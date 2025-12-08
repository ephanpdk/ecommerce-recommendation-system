import { CLUSTERS, THEMES } from './config.js';
import { state, setSessionLogs } from './state.js';
import { switchView } from './main.js';

export function toast(msg, type='info') {
    const d = document.createElement('div');
    const c = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-red-500' : 'bg-slate-800';
    d.className = `${c} text-white px-4 py-3 rounded-lg shadow-xl text-xs font-bold flex items-center gap-3 transform transition-all duration-300 translate-x-full opacity-0 backdrop-blur-md z-[100] mb-2 pointer-events-none`;
    d.innerHTML = `<i class="fa-solid ${type==='success'?'fa-check':'fa-info'}"></i> ${msg}`;
    const container = document.getElementById('toast-container');
    if (container) {
        container.appendChild(d);
        setTimeout(() => d.classList.remove('translate-x-full', 'opacity-0'), 10);
        setTimeout(() => d.remove(), 3000);
    }
}

export function toggleModal(id) {
    if(id === 'specsModal' || id === 'aboutModal') { switchView('pipeline'); return; }
    const el = document.getElementById(id);
    if(!el) return;
    el.classList.toggle('hidden');
}

export function addLog(cluster, money) {
    const time = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    let logs = JSON.parse(localStorage.getItem('sessionLogs') || '[]');
    logs.unshift({cluster, money, time});
    if(logs.length > 10) logs.pop();
    localStorage.setItem('sessionLogs', JSON.stringify(logs));
    setSessionLogs(logs);

    const table = document.getElementById('log-table');
    if(table) {
        if(table.innerHTML.includes('No activity')) table.innerHTML = '';
        table.innerHTML = `<tr class="hover:bg-slate-50 transition border-b border-slate-50 fade-enter"><td class="px-6 py-2 text-xs text-slate-400 font-mono">${time}</td><td class="px-6 py-2 text-xs font-bold ${THEMES[cluster].text}">${CLUSTERS[cluster]}</td><td class="px-6 py-2 text-xs text-right font-bold text-slate-600">$${money}</td><td class="px-6 py-2 text-center"><i class="fa-solid fa-circle-check text-emerald-500 text-xs"></i></td></tr>` + table.innerHTML;
    }
}