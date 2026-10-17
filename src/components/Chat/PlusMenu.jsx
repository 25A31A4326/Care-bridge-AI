import React, { useRef } from 'react';
import { Camera, Package, FileText, ClipboardList, FileSpreadsheet, X } from 'lucide-react';

export default function PlusMenu({ isOpen, onClose, onFileSelect, t, language }) {
  const fileInputRef = useRef(null);
  const selectedTypeRef = useRef('prescription');

  if (!isOpen) return null;

  const handleOptionClick = (uploadType) => {
    selectedTypeRef.current = uploadType;
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file, selectedTypeRef.current);
      onClose();
    }
  };

  const options = [
    {
      type: 'prescription',
      icon: Camera,
      title_en: 'Upload prescription photo',
      title_te: 'ప్రిస్క్రిప్షన్ ఫోటో అప్‌లోడ్',
      desc_en: 'Photo of paper prescription from doctor',
      desc_te: 'డాక్టర్ రాసిన కాగితం ప్రిస్క్రిప్షన్ ఫోటో',
      color: 'bg-emerald-100 text-emerald-700'
    },
    {
      type: 'medicine_package',
      icon: Package,
      title_en: 'Upload medicine package photo',
      title_te: 'మందుల ప్యాకెట్ ఫోటో అప్‌లోడ్',
      desc_en: 'Photo of strip or box (confirms name only)',
      desc_te: 'మందుల ప్యాకెట్ లేదా స్ట్రిప్ ఫోటో',
      color: 'bg-amber-100 text-amber-700'
    },
    {
      type: 'discharge_summary',
      icon: ClipboardList,
      title_en: 'Upload discharge summary',
      title_te: 'డిశ్చార్జ్ సమ్మరీ అప్‌లోడ్',
      desc_en: 'Hospital discharge papers or care plan',
      desc_te: 'ఆసుపత్రి నుండి ఇచ్చిన డిశ్చార్జ్ పత్రాలు',
      color: 'bg-blue-100 text-blue-700'
    },
    {
      type: 'medical_report',
      icon: FileSpreadsheet,
      title_en: 'Upload medical report',
      title_te: 'మెడికల్ ల్యాబ్ రిపోర్ట్ అప్‌లోడ్',
      desc_en: 'Lab results, blood tests, or diagnostic notes',
      desc_te: 'రక్త పరీక్షలు లేదా ల్యాబ్ రిపోర్ట్',
      color: 'bg-purple-100 text-purple-700'
    },
    {
      type: 'pdf',
      icon: FileText,
      title_en: 'Upload PDF document',
      title_te: 'పీడీఎఫ్ డాక్యుమెంట్ అప్‌లోడ్',
      desc_en: 'Digital PDF files of medical records',
      desc_te: 'డిజిటల్ పీడీఎఫ్ మెడికల్ ఫైల్స్',
      color: 'bg-teal-100 text-teal-700'
    }
  ];

  return (
    <>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.pdf,.txt"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Modal Backdrop */}
      <div 
        className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-end sm:items-center justify-center p-3 sm:p-4"
        onClick={onClose}
      >
        <div 
          className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 animate-in fade-in slide-in-from-bottom-6 duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h3 className="text-lg font-bold text-slate-800">
                {language === 'te' ? 'వైద్య పత్రాన్ని జతచేయండి' : 'Attach Medical Document'}
              </h3>
              <p className="text-xs text-slate-500">
                {language === 'te' 
                  ? 'సహాయక విశ్లేషణ కోసం మీ పత్రం రకాన్ని ఎంచుకోండి'
                  : 'Select the document type for safe, source-grounded extraction'}
              </p>
            </div>
            <button 
              onClick={onClose}
              className="p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="mt-4 space-y-2.5 max-h-[60vh] overflow-y-auto pr-1">
            {options.map((opt) => {
              const IconComp = opt.icon;
              return (
                <button
                  key={opt.type}
                  onClick={() => handleOptionClick(opt.type)}
                  className="w-full flex items-center space-x-3.5 p-3.5 rounded-2xl border border-slate-100 hover:border-teal-500 hover:bg-teal-50/40 text-left transition-all group"
                >
                  <div className={`w-11 h-11 rounded-xl ${opt.color} flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform`}>
                    <IconComp className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-bold text-slate-800">
                      {language === 'te' ? opt.title_te : opt.title_en}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {language === 'te' ? opt.desc_te : opt.desc_en}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-center">
            <span className="text-[11px] text-slate-400">
              Supports JPG, JPEG, PNG, and PDF (Max 16 MB). Saved to private secure storage.
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
