import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });
export const API_BASE = API;

export const loginStudent = (body) => api.post("/auth/student", body).then((r) => r.data);
export const loginTeacher = (pin) => api.post("/auth/teacher", { pin }).then((r) => r.data);
export const getClasses = () => api.get("/classes").then((r) => r.data);
export const getRooms = () => api.get("/rooms").then((r) => r.data);
export const getSources = () => api.get("/sources").then((r) => r.data);
export const startSession = (body) => api.post("/sessions", body).then((r) => r.data);
export const getSession = (id) => api.get(`/sessions/${id}`).then((r) => r.data);
export const getMissions = (id) => api.get(`/sessions/${id}/missions`).then((r) => r.data);
export const postAttempt = (num, body) => api.post(`/missions/${num}/attempt`, body).then((r) => r.data);
export const postHint = (num, session_id) => api.post(`/missions/${num}/hint`, { session_id }).then((r) => r.data);
export const finishSession = (id) => api.post(`/sessions/${id}/finish`).then((r) => r.data);
export const teacherOverview = (pin, class_code) =>
  api.get("/teacher/overview", { params: { pin, class_code } }).then((r) => r.data);
export const teacherAttempts = (sessionId, pin) =>
  api.get(`/teacher/attempts/${sessionId}`, { params: { pin } }).then((r) => r.data);
export const teacherOverride = (body) => api.post("/teacher/override", body).then((r) => r.data);
export const getLeaderboard = (class_code) =>
  api.get("/leaderboard", { params: { class_code } }).then((r) => r.data);
export const pdfUrl = (id) => `${API}/report/pdf/${id}`;

const KEY = "nm_dossier_state";
export const saveLocal = (data) => localStorage.setItem(KEY, JSON.stringify(data));
export const readLocal = () => {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || null;
  } catch {
    return null;
  }
};
export const clearLocal = () => localStorage.removeItem(KEY);
