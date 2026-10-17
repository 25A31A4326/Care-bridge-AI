import React, { useState } from 'react';
import { 
  FileText, Volume2, VolumeX, CheckCircle2, AlertTriangle, 
  AlertCircle, ChevronDown, ChevronUp, Calendar, HeartPulse, X, ShieldAlert 
} from 'lucide-react';
import { speech } from '../../services/speech';

export default function PrescriptionExplanation({ data, language, t, onClose, onScheduleVerified }) {
  const [showSource, setShowSource] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  if (!data) return null;

  const simpleExplanation = language === 'te' 
    ? (data.simple_explanation_te || data.simple_explanation_en || '')
    : (data.simple_explanation_en || data.simple_explanation_te || '');

  const rawText = data.raw_text || '';
  const structuredItems = data.structured_items || [];
  const readability = data.readability || {};
  const validationReport = data.validation_report || {};
  const overallStatus = data.overall_status || 'verified';

  const handleSpeak = () => {
    if (isPlaying) {
      speech.stopSpeaking();
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      speech.speak(
        simpleExplanation,
        language,
        () => setIsPlaying(false),
        () => setIsPlaying(true)
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-5 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-3xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                {language === 'te' ? 'వైద్య పత్ర విశ్లేషణ & వివరణ' : 'Medical Document Analysis & Explanation'}
              </h2>
              <span className="text-xs text-slate-500">
                {data.filename || 'Uploaded Document'} • Method: {data.extraction_method || 'Native'}
              </span>
            </div>
          </div>
          <button 
            onClick={() => { speech.stopSpeaking(); onClose(); }}
            className="p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">

          {/* Overall Status Banner */}
          {overallStatus === 'verified' && (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-start space-x-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-emerald-900">
                  {language === 'te' ? 'పూర్తిగా నిర్ధారించబడింది' : 'Verified Medical Instructions'}
                </h4>
                <p className="text-xs text-emerald-700 mt-0.5">
                  {language === 'te' 
                    ? 'ఈ పత్రంలోని మందుల పేర్లు, సమయాలు మరియు మోతాదులు డాక్టర్ రికార్డులతో సరిపోలాయి.'
                    : 'Medication names, doses, and schedules were safely confirmed against the hospital source text.'}
                </p>
              </div>
            </div>
          )}

          {overallStatus === 'needs_verification' && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-amber-900">
                  {language === 'te' ? 'డాక్టర్‌తో సరిచూసుకోవాలి (Needs Verification)' : 'Doctor Verification Required'}
                </h4>
                <p className="text-xs text-amber-800 mt-0.5">
                  {language === 'te'
                    ? 'చేతిరాత లేదా ఫోటో అస్పష్టంగా ఉండటం వల్ల కొన్ని మోతాదులు లేదా సమయాలు ధృవీకరించబడలేదు. ఆటోమేటిక్ రిమైండర్లు నిలిపివేయబడ్డాయి.'
                    : 'Some medication doses or times are smudged or missing. Automatic reminders cannot be scheduled until verified with your prescribing doctor.'}
                </p>
              </div>
            </div>
          )}

          {overallStatus === 'conflicting' && (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start space-x-3">
              <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-rose-900">
                  {language === 'te' ? 'పరస్పర విరుద్ధమైన సూచనలు ఉన్నాయి (Conflicting Instructions)' : 'Critical Conflict Detected'}
                </h4>
                <p className="text-xs text-rose-800 mt-0.5">
                  {language === 'te'
                    ? 'డాక్యుమెంట్లో వేర్వేరు పేజీలలో వేర్వేరు వ్యవధి లేదా మోతాదు పేర్కొనబడింది. దయచేసి డాక్టర్‌ను సంప్రదించండి.'
                    : 'Conflicting medication instructions detected in the document. Immediate verification with the doctor or surgeon is required.'}
                </p>
              </div>
            </div>
          )}

          {/* Section 1: Simple Explanation ("Simple Explanation" / "సులభమైన వివరణ") */}
          <div className="bg-teal-50/50 rounded-3xl p-5 border border-teal-100">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <HeartPulse className="w-5 h-5 text-teal-700" />
                <h3 className="text-base font-bold text-teal-950">
                  {language === 'te' ? 'సులభమైన వివరణ' : 'Simple Explanation'}
                </h3>
              </div>
              <button
                onClick={handleSpeak}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-teal-600 text-white text-xs font-bold hover:bg-teal-700 transition-all shadow-xs"
              >
                {isPlaying ? <VolumeX className="w-3.5 h-3.5 animate-pulse" /> : <Volume2 className="w-3.5 h-3.5" />}
                <span>{isPlaying ? t.explanation.stopReading : t.explanation.readAloud}</span>
              </button>
            </div>

            <div className="whitespace-pre-line text-[15px] leading-relaxed text-slate-800 font-medium">
              {simpleExplanation}
            </div>

            {/* Readability Metric (English Only, labeled clearly) */}
            {readability && readability.score > 0 && (
              <div className="mt-4 pt-3 border-t border-teal-100/80 flex items-center justify-between text-xs text-slate-500">
                <span className="font-semibold text-slate-600">
                  {readability.metric_name}: <strong className="text-teal-800">{readability.score} / 100</strong> ({readability.label})
                </span>
                <span className="text-[11px] text-slate-400">Validated for elderly readability</span>
              </div>
            )}
          </div>

          {/* Section 2: Structured Instructions Table */}
          <div>
            <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center space-x-1.5">
              <span>{language === 'te' ? 'ధృవీకరించబడిన సూచనల పట్టిక' : 'Structured Medication Instructions'}</span>
            </h3>

            <div className="border border-slate-200 rounded-2xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                    <tr>
                      <th className="p-3">Medicine</th>
                      <th className="p-3">Strength</th>
                      <th className="p-3">Dose</th>
                      <th className="p-3">Frequency & Time</th>
                      <th className="p-3">Food Guidance</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {structuredItems.map((item, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                        <td className="p-3 font-bold text-slate-900">{item.medicine_name}</td>
                        <td className="p-3 text-slate-600">{item.strength}</td>
                        <td className="p-3 text-slate-600">{item.prescribed_dose}</td>
                        <td className="p-3 text-slate-600">
                          <div>{item.frequency}</div>
                          <div className="text-[11px] text-teal-700 font-semibold">{item.exact_time}</div>
                        </td>
                        <td className="p-3 text-slate-600">{item.food_instruction}</td>
                        <td className="p-3">
                          {item.status === 'verified' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                              Verified
                            </span>
                          )}
                          {item.status === 'needs_verification' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                              Needs Verification
                            </span>
                          )}
                          {item.status === 'conflicting' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">
                              Conflict
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Section 3: Expandable Source Comparison ("What the document says" / "డాక్యుమెంట్లో ఏమి రాశారు") */}
          <div className="border border-slate-200 rounded-2xl overflow-hidden">
            <button
              onClick={() => setShowSource(!showSource)}
              className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-slate-600" />
                <span className="text-sm font-bold text-slate-800">
                  {language === 'te' ? 'డాక్యుమెంట్లో ఏమి రాశారు (What the document says)' : 'What the document says (Source Text Comparison)'}
                </span>
              </div>
              {showSource ? <ChevronUp className="w-4 h-4 text-slate-600" /> : <ChevronDown className="w-4 h-4 text-slate-600" />}
            </button>

            {showSource && (
              <div className="p-4 bg-slate-900 text-slate-200 font-mono text-xs rounded-b-2xl overflow-x-auto max-h-60 leading-relaxed">
                <pre className="whitespace-pre-wrap">{rawText || 'No source text available.'}</pre>
              </div>
            )}
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Strict source verification enforced. Never alter doses without consulting a physician.
          </span>
          <button
            onClick={() => { speech.stopSpeaking(); onClose(); }}
            className="px-5 py-2.5 rounded-xl bg-slate-800 text-white font-bold text-xs hover:bg-slate-900 transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
