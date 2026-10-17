import React, { useState, useEffect } from 'react';
import Navbar from './components/Common/Navbar';
import FirstVisitLanguageModal from './components/Common/FirstVisitLanguageModal';
import ChatInterface from './components/Chat/ChatInterface';
import MedicineManagement from './components/Medicine/MedicineManagement';
import DocumentManager from './components/Documents/DocumentManager';
import CaregiverPortal from './components/Caregiver/CaregiverPortal';
import CarePlanView from './components/CarePlan/CarePlanView';
import { api } from './services/api';
import enTranslations from './translations/en.json';
import teTranslations from './translations/te.json';

export default function App() {
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('carebridge_language') || 'te';
  });

  const [showFirstVisitModal, setShowFirstVisitModal] = useState(() => {
    return !localStorage.getItem('carebridge_language_selected');
  });

  const [currentTab, setCurrentTab] = useState('chat'); // 'chat', 'medicines', 'documents', 'careplan', 'caregiver'
  const [patientId, setPatientId] = useState(1);
  const [currentPatient, setCurrentPatient] = useState(null);
  const [allPatients, setAllPatients] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);

  const t = language === 'te' ? teTranslations : enTranslations;

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const res = await api.getDemoUsers();
      if (res && res.users) {
        setAllPatients(res.users);
        const match = res.users.find(u => u.id === patientId) || res.users[0];
        if (match) setCurrentPatient(match);
      }
    } catch (e) {
      console.error("Failed to load demo patients:", e);
    }
  };

  const handleSelectLanguage = async (selectedLang) => {
    setLanguageState(selectedLang);
    localStorage.setItem('carebridge_language', selectedLang);
    localStorage.setItem('carebridge_language_selected', 'true');
    setShowFirstVisitModal(false);

    try {
      await api.setLanguage(patientId, selectedLang);
    } catch (e) {
      console.warn("Language sync notice:", e);
    }
  };

  const handleSetLanguage = async (newLang) => {
    setLanguageState(newLang);
    localStorage.setItem('carebridge_language', newLang);
    try {
      await api.setLanguage(patientId, newLang);
    } catch (e) {
      console.warn("Language sync notice:", e);
    }
  };

  const handleSwitchPatient = async (newPatientId) => {
    setPatientId(newPatientId);
    try {
      const res = await api.switchDemoUser(newPatientId);
      if (res && res.user) {
        setCurrentPatient({
          ...res.user,
          full_name: res.profile?.full_name || res.user.username,
          age: res.profile?.age,
          emergency_contact: res.profile?.emergency_contact
        });
        if (res.user.language_preference) {
          handleSetLanguage(res.user.language_preference);
        }
      }
    } catch (e) {
      console.error("Failed to switch patient:", e);
    }
  };

  const handleOpenDocDetails = (docId) => {
    setSelectedDocId(docId);
    setCurrentTab('documents');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 selection:bg-teal-200 selection:text-teal-900">
      
      {/* First Visit Language Selection Modal */}
      {showFirstVisitModal && (
        <FirstVisitLanguageModal onSelectLanguage={handleSelectLanguage} />
      )}

      {/* Navigation Header */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        language={language}
        setLanguage={handleSetLanguage}
        currentPatient={currentPatient}
        allPatients={allPatients}
        onSwitchPatient={handleSwitchPatient}
        t={t}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {currentTab === 'chat' && (
          <ChatInterface
            patientId={patientId}
            language={language}
            t={t}
            onOpenDocDetails={handleOpenDocDetails}
          />
        )}

        {currentTab === 'medicines' && (
          <MedicineManagement
            patientId={patientId}
            language={language}
            t={t}
          />
        )}

        {currentTab === 'documents' && (
          <DocumentManager
            patientId={patientId}
            language={language}
            t={t}
            selectedDocId={selectedDocId}
            onClearSelectedDoc={() => setSelectedDocId(null)}
          />
        )}

        {currentTab === 'careplan' && (
          <CarePlanView
            patientId={patientId}
            language={language}
            t={t}
          />
        )}

        {currentTab === 'caregiver' && (
          <CaregiverPortal
            patientId={patientId}
            language={language}
            t={t}
          />
        )}
      </main>

    </div>
  );
}
