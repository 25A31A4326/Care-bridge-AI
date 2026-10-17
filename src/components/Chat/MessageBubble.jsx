import React, { useState } from 'react';
import { Volume2, VolumeX, Sparkles, User, FileText, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';
import { speech } from '../../services/speech';

export default function MessageBubble({ message, language, t, onOpenDocDetails }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [voiceNotice, setVoiceNotice] = useState('');
  const isUser = message.sender_role === 'user';
  
  // Choose content based on language
  const textContent = language === 'te' 
    ? (message.content_te || message.content_en || '')
    : (message.content_en || message.content_te || '');

  const handleSpeak = () => {
    if (isPlaying) {
      speech.stopSpeaking();
      setIsPlaying(false);
    } else {
      setVoiceNotice('');
      setIsPlaying(true);
      speech.speak(
        textContent,
        language,
        () => setIsPlaying(false),    // onEnd
        () => setIsPlaying(true),     // onStart
        (msg) => setVoiceNotice(msg)  // onNoVoice
      );
    }
  };

  // Format bold markdown or line breaks simply
  const renderFormattedText = (text) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Bold format **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <span key={idx} className="block min-h-[1.2em]">
          {parts.map((p, i) => {
            if (p.startsWith('**') && p.endsWith('**')) {
              return <strong key={i} className="font-bold text-slate-900">{p.slice(2, -2)}</strong>;
            }
            return p;
          })}
        </span>
      );
    });
  };

  return (
    <div className={`flex w-full mb-5 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start max-w-2xl sm:max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'} space-x-3`}>
        
        {/* Avatar */}
        <div className={`w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 mt-0.5 shadow-xs ${
          isUser 
            ? 'bg-slate-700 text-white' 
            : 'bg-gradient-to-tr from-teal-600 to-teal-500 text-white shadow-teal-500/20'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
        </div>

        {/* Bubble */}
        <div className={`relative px-5 py-4 rounded-3xl text-[16px] sm:text-[17px] leading-relaxed transition-shadow ${
          isUser
            ? 'bg-teal-600 text-white rounded-tr-xs shadow-sm font-medium'
            : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-xs shadow-sm hover:shadow-md'
        }`}>
          
          {/* Main Text Content */}
          <div className="space-y-1">
            {renderFormattedText(textContent)}
          </div>

          {/* Action Row for Assistant Bubble: Speaker button & Source Citation */}
          {!isUser && (
            <div className="mt-3 pt-2.5 border-t border-slate-100 space-y-1.5">
              <div className="flex items-center justify-between text-xs text-slate-500">
              
              <button
                onClick={handleSpeak}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full border transition-all ${
                  isPlaying 
                    ? 'bg-teal-100 text-teal-800 border-teal-300 font-bold'
                    : 'bg-slate-50 hover:bg-teal-50 text-slate-600 hover:text-teal-700 border-slate-200'
                }`}
                title={isPlaying ? t.explanation.stopReading : t.explanation.readAloud}
              >
                {isPlaying ? <VolumeX className="w-4 h-4 text-teal-700 animate-pulse" /> : <Volume2 className="w-4 h-4 text-teal-600" />}
                <span>{isPlaying ? t.explanation.stopReading : t.explanation.readAloud}</span>
              </button>

              {message.source_document_id && (
                <button
                  onClick={() => onOpenDocDetails && onOpenDocDetails(message.source_document_id)}
                  className="flex items-center space-x-1 text-teal-700 hover:text-teal-800 hover:underline font-semibold"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Source Document #{message.source_document_id}</span>
                </button>
              )}

              </div>
              {/* Voice notice (shown when Telugu TTS is unavailable) */}
              {voiceNotice && (
                <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-2.5 py-1.5">
                  ⚠️ {voiceNotice}
                </p>
              )}
            </div>
          )}


        </div>

      </div>
    </div>
  );
}
