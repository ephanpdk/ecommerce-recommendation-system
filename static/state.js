export const state = {
    token: localStorage.getItem('token'),
    user: localStorage.getItem('user'),
    metrics: null,
    sessionLogs: [],
    charts: {
        pca: null,
        sil: null,
        corr: null,
        imp: null,
        sim: null,
        elbow: null,
        pie: null,
        radar: null
    }
};

export function setToken(newToken) {
    state.token = newToken;
}

export function setUser(newUser) {
    state.user = newUser;
}

export function setMetrics(newMetrics) {
    state.metrics = newMetrics;
}

export function setSessionLogs(logs) {
    state.sessionLogs = logs;
}