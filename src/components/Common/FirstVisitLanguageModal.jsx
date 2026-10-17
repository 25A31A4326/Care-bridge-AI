import React from 'react';
import { Languages, HeartHandshake } from 'lucide-react';

export default function FirstVisitLanguageModal({ onSelectLanguage }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 border border-teal-100 text-center animate-in fade-in zoom-in-95 duration-200">
        <div className="w-16 h-16 bg-teal-100 text-teal-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <HeartHandshake className="w-8 h-8" />
        </div>

        <h2 className="text-2xl font-bold text-slate-800 mb-2">Welcome to CareBridge AI</h2>
        <p className="text-teal-700 font-medium mb-6">మీ మందులు, మీ భాష, మీ ఆరోగ్యం</p>

        <p className="text-slate-600 mb-6 text-sm">
          Please select your preferred language. You can change this at any time from the top bar.
        </p>

        <div className="grid grid-cols-1 gap-4">
          <button
            onClick={() => onSelectLanguage('te')}
            className="flex items-center justify-between p-5 rounded-2xl border-2 border-teal-500 bg-teal-50/50 hover:bg-teal-100/70 transition-all text-left group"
          >
            <div>
              <div className="text-xl font-bold text-teal-900 font-telugu">తెలుగు (Telugu)</div>
              <div className="text-xs text-teal-700 mt-1">సులభమైన తెలుగు సూచనలు మరియు వాయిస్ సహాయం</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center text-sm font-bold group-hover:scale-105 transition-transform">
              తే
            </div>
          </button>

          <button
            onClick={() => onSelectLanguage('en')}
            className="flex items-center justify-between p-5 rounded-2xl border-2 border-slate-200 hover:border-teal-500 hover:bg-slate-50 transition-all text-left group"
          >
            <div>
              <div className="text-xl font-bold text-slate-800">English</div>
              <div className="text-xs text-slate-500 mt-1">Simple English explanations & voice assistance</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold group-hover:bg-teal-600 group-hover:text-white transition-colors">
              En
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
