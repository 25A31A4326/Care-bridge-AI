import React from 'react';
import { 
  HeartHandshake, MessageSquare, Pill, FileText, Users, 
  Printer, Languages, UserCheck, ChevronDown 
} from 'lucide-react';

export default function Navbar({ 
  currentTab, 
  setCurrentTab, 
  language, 
  setLanguage, 
  currentPatient, 
  allPatients, 
  onSwitchPatient, 
  t 
}) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18 py-3">
          
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('chat')}>
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-teal-600 to-teal-400 text-white flex items-center justify-center shadow-md shadow-teal-500/20">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">
                  {language === 'te' ? 'కేర్‌బ్రిడ్జ్ AI' : 'CareBridge AI'}
                </span>
                <span className="text-[10px] font-semibold bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full border border-teal-200">
                  Safe Care
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                {language === 'te' ? 'మీ మందులు, మీ భాష, మీ ఆరోగ్యం' : 'Your Medicine, Your Language, Your Care'}
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setCurrentTab('chat')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                currentTab === 'chat'
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/30'
                  : 'text-slate-600 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>{t.nav.chat}</span>
            </button>

            <button
              onClick={() => setCurrentTab('medicines')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                currentTab === 'medicines'
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/30'
                  : 'text-slate-600 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              <Pill className="w-4 h-4" />
              <span>{t.nav.medicines}</span>
            </button>

            <button
              onClick={() => setCurrentTab('documents')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                currentTab === 'documents'
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/30'
                  : 'text-slate-600 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>{t.nav.documents}</span>
            </button>

            <button
              onClick={() => setCurrentTab('careplan')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                currentTab === 'careplan'
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/30'
                  : 'text-slate-600 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              <Printer className="w-4 h-4" />
              <span>{t.nav.careplan}</span>
            </button>

            <button
              onClick={() => setCurrentTab('caregiver')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all ${
                currentTab === 'caregiver'
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/30'
                  : 'text-slate-600 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>{t.nav.caregiver}</span>
            </button>
          </nav>

          {/* Right Controls: Demo Patient Switcher & Language Switcher */}
          <div className="flex items-center space-x-2">
            
            {/* Demo Patient Selector Dropdown */}
            <div className="relative group">
              <button className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-teal-200 bg-teal-50/70 text-teal-900 text-xs font-semibold hover:bg-teal-100/70 transition-colors">
                <UserCheck className="w-3.5 h-3.5 text-teal-600" />
                <span className="max-w-[120px] truncate">{currentPatient?.full_name?.split(' ')[0] || 'Patient'}</span>
                <ChevronDown className="w-3.5 h-3.5 text-teal-600" />
              </button>
              
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 hidden group-hover:block z-50">
                <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Select Synthetic Demo Patient
                </div>
                {allPatients.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => onSwitchPatient(p.id)}
                    className={`w-full text-left px-3 py-2 rounded-xl text-xs transition-colors flex items-center justify-between ${
                      currentPatient?.id === p.id ? 'bg-teal-50 text-teal-900 font-bold' : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div>
                      <div className="font-semibold">{p.full_name || p.username}</div>
                      <div className="text-[10px] text-slate-500">
                        {p.role === 'caregiver' ? 'Caregiver Account' : `Age ${p.age || 'N/A'}`}
                      </div>
                    </div>
                    {currentPatient?.id === p.id && (
                      <span className="w-2 h-2 rounded-full bg-teal-500"></span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Language Switcher Button */}
            <button
              onClick={() => setLanguage(language === 'te' ? 'en' : 'te')}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:border-teal-500 hover:bg-teal-50/50 text-xs font-bold text-slate-800 transition-all"
              title="Toggle Telugu / English"
            >
              <Languages className="w-3.5 h-3.5 text-teal-600" />
              <span>{language === 'te' ? 'English' : 'తెలుగు'}</span>
            </button>

          </div>

        </div>

        {/* Mobile secondary navigation strip */}
        <div className="flex md:hidden overflow-x-auto py-2 space-x-1 border-t border-slate-100 no-scrollbar">
          <button
            onClick={() => setCurrentTab('chat')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap ${
              currentTab === 'chat' ? 'bg-teal-600 text-white' : 'text-slate-600'
            }`}
          >
            {t.nav.chat}
          </button>
          <button
            onClick={() => setCurrentTab('medicines')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap ${
              currentTab === 'medicines' ? 'bg-teal-600 text-white' : 'text-slate-600'
            }`}
          >
            {t.nav.medicines}
          </button>
          <button
            onClick={() => setCurrentTab('documents')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap ${
              currentTab === 'documents' ? 'bg-teal-600 text-white' : 'text-slate-600'
            }`}
          >
            {t.nav.documents}
          </button>
          <button
            onClick={() => setCurrentTab('careplan')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap ${
              currentTab === 'careplan' ? 'bg-teal-600 text-white' : 'text-slate-600'
            }`}
          >
            {t.nav.careplan}
          </button>
          <button
            onClick={() => setCurrentTab('caregiver')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap ${
              currentTab === 'caregiver' ? 'bg-teal-600 text-white' : 'text-slate-600'
            }`}
          >
            {t.nav.caregiver}
          </button>
        </div>

      </div>
    </header>
  );
}
