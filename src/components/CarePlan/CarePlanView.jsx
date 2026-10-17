import React, { useState, useEffect } from 'react';
import { 
  FileText, Printer, Download, HeartPulse, AlertTriangle, 
  CheckCircle2, Clock, Calendar, ShieldAlert, Sparkles 
} from 'lucide-react';
import { api } from '../../services/api';

export default function CarePlanView({ patientId, language, t }) {
  const [carePlan, setCarePlan] = useState(null);
  const [patient, setPatient] = useState(null);
  const [appointment, setAppointment] = useState(null);
  const [showPrintModal, setShowPrintModal] = useState(false);
  const [pdfLang, setPdfLang] = useState(language);

  useEffect(() => {
    loadCarePlan();
  }, [patientId]);

  const loadCarePlan = async () => {
    try {
      const res = await api.getCurrentCarePlan(patientId);
      if (res && res.care_plan) {
        setCarePlan(res.care_plan);
        setPatient(res.patient);
        setAppointment(res.appointment);
      }
    } catch (e) {
      console.error("Error loading care plan:", e);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const downloadPdfUrl = api.getFridgeSheetPdfUrl(patientId, pdfLang);

  if (!carePlan) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-700">No Care Plan Available</h2>
        <p className="text-sm text-slate-500 mt-1">
          Upload a discharge summary or prescription to automatically generate your verified care plan.
        </p>
      </div>
    );
  }

  const isTe = language === 'te';
  const title = isTe ? carePlan.title_te : carePlan.title_en;
  const summary = isTe ? carePlan.summary_te : carePlan.summary_en;
  const diet = isTe ? carePlan.diet_te : carePlan.diet_en;
  const activity = isTe ? carePlan.activity_te : carePlan.activity_en;
  const warnings = isTe ? carePlan.warning_signs_te : carePlan.warning_signs_en;
  const medicines = carePlan.medicines_list || [];

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 space-y-6 animate-in fade-in duration-200">
      
      {/* Header with Print / Download Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200 no-print">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md">
            Verified Clinical Care Plan
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight mt-1">
            {title}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Patient: <strong>{patient?.full_name}</strong> (Age {patient?.age})
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={handlePrint}
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 transition-colors shadow-2xs"
          >
            <Printer className="w-4 h-4 text-teal-600" />
            <span>{t.careplan.printSheet}</span>
          </button>

          <a
            href={downloadPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition-all shadow-xs"
          >
            <Download className="w-4 h-4" />
            <span>{t.careplan.downloadPdf}</span>
          </a>
        </div>
      </div>

      {/* Verification Status Banner */}
      <div className="p-4 rounded-2xl bg-teal-50/80 border border-teal-200 flex items-start space-x-3 text-xs text-teal-900">
        <CheckCircle2 className="w-5 h-5 text-teal-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Source-Grounded Verification:</span> {carePlan.discrepancy_notes}
        </div>
      </div>

      {/* Main Printable Card Layout */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print-page">
        
        {/* Printable Header Banner */}
        <div className="border-b border-slate-200 pb-4">
          <div className="text-xs font-bold text-teal-700 uppercase tracking-widest">
            CareBridge AI — Patient Daily Care Sheet (ఫ్రిడ్జ్ చార్ట్)
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 mt-1">
            {patient?.full_name}
          </h2>
          <div className="text-xs text-slate-500 mt-1 flex flex-wrap gap-4">
            <span>Age: {patient?.age} Yrs</span>
            <span>Emergency Contact: {patient?.emergency_contact}</span>
            <span>Date: {new Date().toLocaleDateString()}</span>
          </div>
        </div>

        {/* Clinical Summary */}
        <div>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-1">
            {isTe ? 'వైద్య సారాంశం' : 'Clinical Summary'}
          </h3>
          <p className="text-sm text-slate-700 leading-relaxed">
            {summary}
          </p>
        </div>

        {/* Medicines Section */}
        <div>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">
            {isTe ? '1. ధృవీకరించబడిన మందుల వేళలు' : '1. Verified Medication Schedule'}
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {medicines.map((m, idx) => (
              <div key={idx} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50">
                <div className="font-bold text-sm text-slate-900">{m.name}</div>
                <div className="text-xs text-teal-700 font-semibold mt-1">Dose: {m.dose}</div>
                <div className="text-xs text-slate-600 mt-0.5">Time: {m.time}</div>
                <div className="text-[11px] text-slate-500 mt-1 font-telugu italic">{m.telugu}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Diet & Activity Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-teal-50/40 border border-teal-100">
            <h4 className="text-xs font-bold uppercase text-teal-900 tracking-wider mb-1">
              {isTe ? 'ఆహార నియమాలు (Diet)' : 'Dietary Instructions'}
            </h4>
            <p className="text-xs text-slate-700 leading-relaxed">{diet}</p>
          </div>

          <div className="p-4 rounded-2xl bg-teal-50/40 border border-teal-100">
            <h4 className="text-xs font-bold uppercase text-teal-900 tracking-wider mb-1">
              {isTe ? 'శారీరక శ్రమ / వ్యాయామం (Activity)' : 'Activity & Movement'}
            </h4>
            <p className="text-xs text-slate-700 leading-relaxed">{activity}</p>
          </div>
        </div>

        {/* Follow-up Appointment */}
        {appointment && (
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50 flex items-start space-x-3">
            <Calendar className="w-5 h-5 text-teal-600 shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-bold text-slate-800 uppercase">
                {isTe ? 'తదుపరి డాక్టర్ దర్శనం' : 'Next Follow-Up Appointment'}
              </div>
              <div className="text-xs text-slate-700 mt-0.5">
                <strong>{appointment.doctor_or_dept}</strong> on <strong>{appointment.appointment_date}</strong> at {appointment.appointment_time}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">{appointment.instructions}</div>
            </div>
          </div>
        )}

        {/* Emergency Warning Signs */}
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs">
          <div className="flex items-center space-x-1.5 font-bold text-rose-900 mb-1">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <span>{isTe ? 'అత్యవసర హెచ్చరిక లక్షణాలు (Emergency Signs)' : 'Emergency Warning Signs — Seek Urgent Care'}</span>
          </div>
          <p className="text-rose-800 leading-relaxed">{warnings}</p>
        </div>

        {/* Fridge Sheet Footer Disclaimer */}
        <div className="pt-3 border-t border-slate-200 text-center text-[10px] text-slate-400">
          CareBridge AI Care Sheet • For personal reference. Strictly verified from hospital records. Never stop or change medications without your doctor.
        </div>

      </div>

    </div>
  );
}
