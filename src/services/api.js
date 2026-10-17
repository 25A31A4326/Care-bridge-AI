const API_BASE = '/api';

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Auth & Demo Users
  getDemoUsers: async () => {
    const res = await fetch(`${API_BASE}/auth/demo_users`);
    return res.json();
  },

  switchDemoUser: async (userId) => {
    const res = await fetch(`${API_BASE}/auth/switch_demo_user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    return res.json();
  },

  setLanguage: async (userId, language) => {
    const res = await fetch(`${API_BASE}/auth/language`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, language })
    });
    return res.json();
  },

  // Chat
  getChatHistory: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/chat/history?patient_id=${patientId}`);
    return res.json();
  },

  sendMessage: async (patientId = 1, content, language = 'te', isVoice = false) => {
    const res = await fetch(`${API_BASE}/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId, content, language, is_voice: isVoice })
    });
    return res.json();
  },

  clearChat: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId })
    });
    return res.json();
  },

  // Documents
  uploadDocument: async (formData) => {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData
    });
    return res.json();
  },

  listDocuments: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/documents/list?patient_id=${patientId}`);
    return res.json();
  },

  getDocument: async (docId) => {
    const res = await fetch(`${API_BASE}/documents/${docId}`);
    return res.json();
  },

  // Medicines
  getSchedules: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/medicines/schedule?patient_id=${patientId}`);
    return res.json();
  },

  createSchedule: async (scheduleData) => {
    const res = await fetch(`${API_BASE}/medicines/schedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scheduleData)
    });
    return res.json();
  },

  getTodayDoses: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/medicines/doses/today?patient_id=${patientId}`);
    return res.json();
  },

  getCalendarDoses: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/medicines/doses/calendar?patient_id=${patientId}`);
    return res.json();
  },

  updateDoseStatus: async (doseId, status, notes = '', userId = 1) => {
    const res = await fetch(`${API_BASE}/medicines/doses/${doseId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, notes, user_id: userId })
    });
    return res.json();
  },

  // Caregiver
  getCaregiverRelationships: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/caregiver/relationships?patient_id=${patientId}`);
    return res.json();
  },

  authorizeCaregiver: async (authData) => {
    const res = await fetch(`${API_BASE}/caregiver/authorize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(authData)
    });
    return res.json();
  },

  revokeCaregiver: async (relId) => {
    const res = await fetch(`${API_BASE}/caregiver/revoke/${relId}`, {
      method: 'POST'
    });
    return res.json();
  },

  getPatientStatusForCaregiver: async (caregiverId, patientId = 1) => {
    const res = await fetch(`${API_BASE}/caregiver/patient-status?caregiver_id=${caregiverId}&patient_id=${patientId}`);
    return res.json();
  },

  // Care Plan & PDF
  getCurrentCarePlan: async (patientId = 1) => {
    const res = await fetch(`${API_BASE}/careplan/current?patient_id=${patientId}`);
    return res.json();
  },

  getFridgeSheetPdfUrl: (patientId = 1, lang = 'en') => {
    return `${API_BASE}/careplan/fridge-sheet-pdf?patient_id=${patientId}&lang=${lang}`;
  }
};
