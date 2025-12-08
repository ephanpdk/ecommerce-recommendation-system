import { API } from './config.js';
import { state, setToken, setUser } from './state.js';
import { toast, toggleModal } from './utils.js';

export function renderAuth() {
    const area = document.getElementById('auth-section');
    if(!area) return;

    if(state.token) {
        const init = state.user ? state.user[0].toUpperCase() : 'U';
        area.innerHTML = `
            <div class="flex items-center gap-3 ml-4 pl-4 border-l border-slate-200">
                <div class="text-right hidden sm:block">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Active</div>
                    <div class="text-xs font-bold text-slate-900">${state.user}</div>
                </div>
                <div class="h-9 w-9 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-600 text-xs">${init}</div>
                <button onclick="window.logout()" class="text-slate-400 hover:text-red-500 transition ml-1"><i class="fa-solid fa-power-off"></i></button>
            </div>`;
    } else {
        area.innerHTML = `<button onclick="window.toggleModal('authModal')" class="ml-4 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2 rounded-lg transition shadow-lg shadow-indigo-200">LOGIN ACCESS</button>`;
    }
}

export async function doAuth(type) {
    const email = type==='login' ? document.getElementById('loginEmail').value : document.getElementById('regEmail').value;
    const pass = type==='login' ? document.getElementById('loginPass').value : document.getElementById('regPass').value;
    const name = type==='register' ? document.getElementById('regName').value : null;

    if(!email || !pass) return toast('Input required', 'error');

    const endpoint = type==='login' ? '/auth/login' : '/auth/register';
    const body = type==='login' ? {email, password: pass} : {email, password: pass, name};

    try {
        const res = await fetch(`${API}${endpoint}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        if(res.ok) {
            if(type==='register') {
                toast('Account created', 'success');
                switchAuthTab('login');
            } else {
                const data = await res.json();
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', email.split('@')[0]);
                setToken(data.access_token);
                setUser(email.split('@')[0]);
                toggleModal('authModal');
                renderAuth();
                toast('Login Successful', 'success');
            }
        } else toast('Auth Failed', 'error');
    } catch(e) { toast('Connection Error', 'error'); }
}

export function switchAuthTab(type) {
    document.getElementById('loginForm').classList.toggle('hidden', type !== 'login');
    document.getElementById('registerForm').classList.toggle('hidden', type === 'login');
    document.getElementById('tabLogin').className = type==='login' ? "flex-1 py-2 text-xs font-bold rounded-md bg-white shadow-sm text-slate-800 transition" : "flex-1 py-2 text-xs font-bold rounded-md text-slate-500 hover:text-slate-700 transition";
    document.getElementById('tabRegister').className = type!=='login' ? "flex-1 py-2 text-xs font-bold rounded-md bg-white shadow-sm text-slate-800 transition" : "flex-1 py-2 text-xs font-bold rounded-md text-slate-500 hover:text-slate-700 transition";
}

export function logout() {
    localStorage.clear();
    setToken(null);
    setUser(null);
    renderAuth();
    toast('Logged Out', 'info');
}

export function handleLogin() { doAuth('login'); }
export function handleRegister() { doAuth('register'); }