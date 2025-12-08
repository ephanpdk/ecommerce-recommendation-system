import { API, CLUSTERS, THEMES } from './config.js';
import { state } from './state.js';
import { toast, toggleModal, addLog } from './utils.js';
import { logout } from './auth.js';

export function updateLiveSimulator() {
    const money = parseFloat(document.getElementById('in-money').value);
    const freq = parseInt(document.getElementById('in-freq').value);
    const views = parseInt(document.getElementById('in-views').value);
    const cart = parseInt(document.getElementById('in-cart').value);

    const rfmTag = document.getElementById('live-rfm-tag');
    const rfmBar = document.getElementById('indicator-rfm');

    if (money > 2500) {
        rfmTag.innerText = "HIGH ROLLER";
        rfmTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 transition-colors";
        rfmBar.className = "absolute top-0 left-0 w-1.5 h-full bg-amber-500 transition-all duration-300";
    } else if (money > 500 && freq > 10) {
        rfmTag.innerText = "CONSISTENT";
        rfmTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 transition-colors";
        rfmBar.className = "absolute top-0 left-0 w-1.5 h-full bg-emerald-500 transition-all duration-300";
    } else {
        rfmTag.innerText = "CASUAL / LOW";
        rfmTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500 transition-colors";
        rfmBar.className = "absolute top-0 left-0 w-1 h-full bg-slate-300 transition-all duration-300";
    }

    const engTag = document.getElementById('live-eng-tag');
    const engBar = document.getElementById('indicator-eng');

    if (views > 200 || cart > 20) {
        engTag.innerText = "HYPER ACTIVE";
        engTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700 transition-colors";
        engBar.className = "absolute top-0 left-0 w-1.5 h-full bg-blue-500 transition-all duration-300";
    } else if (views > 50) {
        engTag.innerText = "BROWSING";
        engTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-pink-100 text-pink-700 transition-colors";
        engBar.className = "absolute top-0 left-0 w-1.5 h-full bg-pink-500 transition-all duration-300";
    } else {
        engTag.innerText = "DORMANT";
        engTag.className = "px-3 py-1 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500 transition-colors";
        engBar.className = "absolute top-0 left-0 w-1 h-full bg-slate-300 transition-all duration-300";
    }
}

export function bindSliders() {
    const updateVal = (id, val, pre='', post='') => {
        const key = id.split('-')[1];
        const el = document.getElementById(`disp-${key}`);
        if(el) el.innerText = pre + val + post;
    };

    document.getElementById('in-money').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value, '$'); updateLiveSimulator(); });
    document.getElementById('in-freq').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value); updateLiveSimulator(); });
    document.getElementById('in-rec').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value, '', ' days'); updateLiveSimulator(); });
    document.getElementById('in-views').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value); updateLiveSimulator(); });
    document.getElementById('in-cart').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value); updateLiveSimulator(); });
    document.getElementById('in-wish').addEventListener('input', (e) => { updateVal(e.target.id, e.target.value); updateLiveSimulator(); });
}

export function generateInsights(payload, clusterIdx) {
    if(!state.metrics || !state.metrics.centroids_real) return {
        why: "Data metrics not loaded yet.",
        compare: "Cannot compare without baseline.",
        anomaly: "Unknown."
    };

    const centroid = state.metrics.centroids_real[clusterIdx];
    let why = "User behavior aligns with standard segment profile.";

    if (payload.Page_Views > centroid.Page_Views * 1.2 && payload.Frequency < centroid.Frequency) {
        why = "High engagement intent detected, but conversion rate lags behind segment average.";
    } else if (payload.Page_Views < centroid.Page_Views * 0.8 && payload.Monetary > centroid.Monetary) {
        why = "Decisive buyer pattern: High transaction value with minimal browsing time.";
    } else if (payload.Add_to_Cart_Count > centroid.Add_to_Cart_Count * 1.5 && payload.Frequency <= centroid.Frequency) {
        why = "Cart abandonment risk: User adds significantly more items than they purchase.";
    } else if (payload.Monetary > centroid.Monetary && payload.Recency > 60) {
        why = "Dormant VIP: High historical value but inactive for an extended period.";
    }

    const diffMoney = ((payload.Monetary - centroid.Monetary) / centroid.Monetary) * 100;

    let pressure = "Stable";
    if (payload.Recency > 90) pressure = "High Risk (Churn)";
    else if (payload.Recency > 45 && payload.Monetary > 2000) pressure = "Medium Risk";
    else if (payload.Recency < 7 && payload.Frequency > 10) pressure = "High Opportunity";

    const compare = `Spending ${Math.abs(diffMoney).toFixed(1)}% ${diffMoney >= 0 ? 'above' : 'below'} avg. Status: ${pressure}.`;

    let action = "Maintain standard communication.";
    if (pressure.includes("Churn") && payload.Monetary > 1500) action = "🚨 URGENT: Deploy Win-back Campaign via Direct Call/SMS.";
    else if (payload.Page_Views > 60 && payload.Frequency === 0) action = "💡 OPPORTUNITY: Send First-Purchase Discount Coupon.";
    else if (payload.Add_to_Cart_Count > 10 && payload.Recency < 3) action = "🔥 HOT LEAD: Trigger 'Items in Cart' Reminder immediately.";
    else if (clusterIdx === 3 && payload.Recency < 14) action = "⭐ VIP: Offer Early Access to New Collections.";
    else if (payload.Wishlist_Count > 5) action = "🔔 NUDGE: Notify regarding stock availability for wishlist.";

    return { why, compare, anomaly: action };
}

export function setPreset(type) {
    const presets = {
        'newbie': { money: 30, freq: 2, rec: 60, views: 5, cart: 1, wish: 0, avg: 1.2, unique: 1 },
        'window': { money: 100, freq: 5, rec: 15, views: 150, cart: 8, wish: 10, avg: 2.0, unique: 3 },
        'loyalist': { money: 800, freq: 25, rec: 7, views: 40, cart: 15, wish: 5, avg: 3.5, unique: 10 },
        'sultan': { money: 5000, freq: 45, rec: 3, views: 80, cart: 30, wish: 20, avg: 5.0, unique: 25 }
    };

    const p = presets[type];
    if(!p) return;

    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if(el) {
            el.value = val;
            el.dispatchEvent(new Event('input'));
        }
    };

    setVal('in-money', p.money);
    setVal('in-freq', p.freq);
    setVal('in-rec', p.rec);
    setVal('in-views', p.views);
    setVal('in-cart', p.cart);
    setVal('in-wish', p.wish);
    setVal('in-avg', p.avg);
    setVal('in-unique', p.unique);

    toast(`Preset Applied: ${type.toUpperCase()}`, 'info');
}

export function resetSim() {
    document.getElementById('in-money').value=1000;
    document.getElementById('disp-money').innerText='$1000';
    document.getElementById('in-freq').value=5;
    document.getElementById('in-rec').value=30;
    document.getElementById('in-views').value=50;
    document.getElementById('disp-views').innerText='50';
    document.getElementById('in-cart').value=15;
    document.getElementById('disp-cart').innerText='15';
    updateLiveSimulator();
    toast('Reset', 'info');
}

export async function runPrediction() {
    if(!state.token) { toggleModal('authModal'); toast('Login Required', 'error'); return; }

    const payload = {
        Monetary: parseFloat(document.getElementById('in-money').value),
        Frequency: parseInt(document.getElementById('in-freq').value),
        Recency: parseInt(document.getElementById('in-rec').value),
        Page_Views: parseInt(document.getElementById('in-views').value),
        Add_to_Cart_Count: parseInt(document.getElementById('in-cart').value),
        Avg_Items: parseFloat(document.getElementById('in-avg').value),
        Wishlist_Count: parseInt(document.getElementById('in-wish').value),
        Unique_Products: Math.max(1, Math.ceil(parseInt(document.getElementById('in-freq').value)*0.5))
    };

    document.getElementById('state-idle').classList.add('hidden');
    document.getElementById('state-result').classList.remove('hidden');
    document.getElementById('cluster-name').innerHTML = '<span class="animate-pulse">Analyzing...</span>';

    try {
        const res = await fetch(`${API}/recommend/user`, {
            method:'POST',
            headers:{'Content-Type':'application/json','Authorization': `Bearer ${state.token}`},
            body:JSON.stringify(payload)
        });

        if(res.ok) {
            const data = await res.json();
            renderResult(data);
            addLog(data.cluster, payload.Monetary);
            toast('Success', 'success');
        } else {
            if(res.status===401) logout();
            else toast('API Error', 'error');
        }
    } catch(e) { toast('Server Error', 'error'); }
}

export function renderResult(data) {
    const theme = THEMES[data.cluster] || THEMES[0];
    const name = CLUSTERS[data.cluster] || "Unknown";

    document.getElementById('cluster-name').innerText = name;
    document.getElementById('cluster-name').className = `text-3xl font-bold ${theme.text} leading-none`;
    document.getElementById('cluster-icon').className = `fa-solid ${theme.icon}`;
    document.getElementById('cluster-icon-box').className = `w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-4 shadow-sm ${theme.bg} ${theme.color}`;
    document.getElementById('hero-card').className = `relative bg-white rounded-2xl border ${theme.border} p-8 overflow-hidden shadow-sm transition-all duration-500 fade-enter`;

    document.getElementById('res-dist').innerText = Number(data.metrics?.distance_to_centroid ?? 0).toFixed(4);
    document.getElementById('res-conf').innerText = (data.metrics?.confidence_score ?? 0) + '%';

    const drivers = data.metrics?.feature_drivers || [];
    document.getElementById('driver-list').innerHTML = drivers.length
        ? drivers.map(d => `<li class="flex items-center gap-2 text-xs text-slate-600"><i class="fa-solid ${d.sentiment==='positive'?'fa-arrow-trend-up text-emerald-500':'fa-arrow-trend-down text-rose-500'}"></i><span class="font-bold">${d.feature}</span><span class="text-slate-400">(${d.description}, Z=${d.score.toFixed(2)})</span></li>`).join('')
        : '<li class="text-sm text-slate-400 italic">Balanced behavior.</li>';

    const currentPayload = {
        Monetary: parseFloat(document.getElementById('in-money').value),
        Frequency: parseInt(document.getElementById('in-freq').value),
        Recency: parseInt(document.getElementById('in-rec').value),
        Page_Views: parseInt(document.getElementById('in-views').value),
        Add_to_Cart_Count: parseInt(document.getElementById('in-cart').value),
        Wishlist_Count: parseInt(document.getElementById('in-wish').value)
    };

    const insights = generateInsights(currentPayload, data.cluster);

    document.getElementById('bs-why').innerText = insights.why;
    document.getElementById('bs-compare').innerText = insights.compare;

    const anomalyEl = document.getElementById('bs-anomaly');
    anomalyEl.innerText = insights.anomaly;

    if(insights.anomaly.includes("URGENT")) {
        anomalyEl.className = "text-[10px] font-bold text-red-600 bg-red-50 p-2 rounded border border-red-100 mt-auto animate-pulse";
    } else if (insights.anomaly.includes("OPPORTUNITY") || insights.anomaly.includes("HOT")) {
        anomalyEl.className = "text-[10px] font-bold text-emerald-600 bg-emerald-50 p-2 rounded border border-emerald-100 mt-auto";
    } else {
        anomalyEl.className = "text-[10px] font-bold text-slate-600 bg-slate-50 p-2 rounded border border-slate-200 mt-auto";
    }

    document.getElementById('product-grid').innerHTML = (data.recommendations||[]).map(p => `
        <div class="group bg-white border border-slate-100 rounded-xl p-4 hover:shadow-xl transition-all relative">
            <div class="h-32 bg-slate-50 rounded-lg mb-4 relative overflow-hidden">
                <img src="https://picsum.photos/seed/${p.product_id}/300/200" class="w-full h-full object-cover opacity-90">
                <div class="absolute top-2 left-2 bg-white/90 backdrop-blur px-2 py-1 rounded text-[10px] font-bold text-slate-600">${p.category}</div>
            </div>
            <h4 class="font-bold text-slate-800 text-sm mb-2">${p.name}</h4>
            <div class="flex justify-between items-center pt-3 border-t border-slate-50">
                <span class="font-mono font-bold text-slate-900">$${p.price}</span>
                <button class="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center hover:bg-indigo-600 transition shadow-lg active:scale-90">
                    <i class="fa-solid fa-plus text-xs"></i>
                </button>
            </div>
        </div>
    `).join('');
}