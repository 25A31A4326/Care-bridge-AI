import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Send, RotateCcw, X, AlertCircle } from 'lucide-react';
import { speech } from '../../services/speech';

export default function VoiceInputModal({ isOpen, onClose, onSubmit, language, t }) {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      setTranscript('');
      setErrorMsg('');
      startVoiceRecognition();
    } else {
      speech.stopListening();
      setIsListening(false);
    }
    return () => {
      speech.stopListening();
    };
  }, [isOpen]);

  const startVoiceRecognition = () => {
    setErrorMsg('');
    if (!speech.isSpeechRecognitionSupported()) {
      setErrorMsg(t.voice.speechNotSupported);
      return;
    }

    setIsListening(true);
    speech.startListening(
      language,
      (result) => {
        setTranscript(result.transcript);
      },
      (err) => {
        setIsListening(false);
        setErrorMsg(err);
      },
      () => {
        setIsListening(false);
      }
    );
  };

  const handleStop = () => {
    speech.stopListening();
    setIsListening(false);
  };

  const handleSubmit = () => {
    if (transcript.trim()) {
      onSubmit(transcript.trim());
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isListening ? 'bg-red-500 animate-ping' : 'bg-slate-300'}`} />
            <h3 className="text-base font-bold text-slate-800">
              {isListening 
                ? (language === 'te' ? 'వింటున్నాను... మాట్లాడండి' : 'Listening... Speak now') 
                : (language === 'te' ? 'మీ మాటలు పరిశీలించండి' : 'Review Your Speech')}
            </h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Listening Animation / Mic Graphic */}
        <div className="my-6 text-center">
          <button
            onClick={isListening ? handleStop : startVoiceRecognition}
            className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto transition-all shadow-lg ${
              isListening
                ? 'bg-red-500 text-white animate-pulse ring-8 ring-red-100'
                : 'bg-teal-600 text-white hover:bg-teal-700'
            }`}
          >
            {isListening ? <Mic className="w-9 h-9" /> : <MicOff className="w-8 h-8" />}
          </button>
          
          <p className="mt-3 text-xs font-semibold text-slate-500">
            {isListening 
              ? (language === 'te' ? 'మాట్లాడటం పూర్తయ్యాక మైక్ ఆపండి' : 'Tap to pause when finished')
              : (language === 'te' ? 'మళ్ళీ మాట్లాడటానికి మైక్ నొక్కండి' : 'Tap to start recording again')}
          </p>
          <div className="text-[11px] text-teal-700 font-medium mt-1">
            Language: {language === 'te' ? 'Telugu (తెలుగు te-IN)' : 'English (en-US)'}
          </div>
        </div>

        {/* Error Notice */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-2xl bg-amber-50 border border-amber-200 flex items-start space-x-2 text-xs text-amber-900">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">{errorMsg}</span>
              <p className="mt-1 text-slate-600">You can also type your message in the text box.</p>
            </div>
          </div>
        )}

        {/* Transcript Review & Edit Area */}
        <div className="mb-4">
          <label className="block text-xs font-bold text-slate-600 mb-1">
            {t.voice.confirmVoiceText}:
          </label>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            rows={3}
            placeholder={language === 'te' ? 'మీ మాటలు ఇక్కడ కనిపిస్తాయి...' : 'Your spoken words will appear here...'}
            className="w-full p-3.5 text-base rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all resize-none font-medium"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={startVoiceRecognition}
            disabled={isListening}
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <RotateCcw className="w-4 h-4 text-slate-500" />
            <span>{t.voice.retryVoice}</span>
          </button>

          <button
            onClick={handleSubmit}
            disabled={!transcript.trim()}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-teal-600 text-white font-bold text-sm hover:bg-teal-700 transition-all shadow-md shadow-teal-600/30 disabled:opacity-50 disabled:shadow-none"
          >
            <Send className="w-4 h-4" />
            <span>{t.voice.submitToChat}</span>
          </button>
        </div>

      </div>
    </div>
  );
}
