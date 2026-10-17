import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Eye, AlertTriangle, CheckCircle2, 
  ShieldAlert, Sparkles, Clock, Calendar 
} from 'lucide-react';
import { api } from '../../services/api';
import PrescriptionExplanation from '../Prescription/PrescriptionExplanation';

export default function DocumentManager({ patientId, language, t, selectedDocId, onClearSelectedDoc }) {
  const [documents, setDocuments] = useState([]);
  const [activeModalData, setActiveModalData] = useState(null);

  useEffect(() => {
    loadDocs();
  }, [patientId]);

  useEffect(() => {
    if (selectedDocId) {
      viewDocDetails(selectedDocId);
    }
  }, [selectedDocId]);

  const loadDocs = async () => {
    try {
      const res = await api.listDocuments(patientId);
      if (res && res.documents) {
        setDocuments(res.documents);
      }
    } catch (e) {
      console.error("Error loading documents:", e);
    }
  };

  const viewDocDetails = async (docId) => {
    try {
      const res = await api.getDocument(docId);
      if (res && res.document) {
        const doc = res.document;
        setActiveModalData({
          filename: doc.original_filename,
          upload_type: doc.upload_type,
          extraction_status: doc.status,
          extraction_method: doc.extraction_method,
          quality_assessment: doc.quality_assessment,
          raw_text: doc.raw_text,
          simple_explanation_en: doc.simple_explanation_en,
          simple_explanation_te: doc.simple_explanation_te,
          structured_items: doc.structured_instructions,
          readability: doc.readability,
          validation_report: doc.validation_report,
          overall_status: doc.status
        });
      }
    } catch (e) {
      console.error("Error viewing document:", e);
    }
  };

  const closeModal = () => {
    setActiveModalData(null);
    if (onClearSelectedDoc) onClearSelectedDoc();
  };

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 space-y-6 animate-in fade-in duration-200">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight flex items-center space-x-2.5">
            <FileText className="w-8 h-8 text-teal-600" />
            <span>{t.nav.documents}</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Safe non-public medical document records with verified OCR and simple explanations
          </p>
        </div>
      </div>

      {/* Documents Grid / List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {documents.map((doc) => {
          const isVerified = doc.status === 'extracted' || doc.quality_assessment === 'clear';
          const isBlurry = doc.quality_assessment === 'blurry' || doc.status === 'needs_verification';
          const isConflict = doc.quality_assessment === 'conflicting';

          return (
            <div 
              key={doc.id}
              className="bg-white rounded-3xl border border-slate-200 p-5 shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-slate-800 line-clamp-1">
                        {doc.original_filename}
                      </h3>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Type: {doc.upload_type?.replace('_', ' ')} • Size: {Math.round(doc.file_size / 1024)} KB
                      </div>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div>
                    {isConflict ? (
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">
                        Conflict Detected
                      </span>
                    ) : isBlurry ? (
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                        Needs Verification
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        Verified Clean
                      </span>
                    )}
                  </div>
                </div>

                <div className="mt-4 p-3 rounded-2xl bg-slate-50 text-xs text-slate-600">
                  <span className="font-semibold text-slate-700">Quality Assessment:</span> {doc.quality_assessment || 'Analyzed'}
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Uploaded: {new Date(doc.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                <a
                  href={`/api/documents/download/${doc.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-xs font-bold text-slate-600 hover:text-teal-700 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Secure File</span>
                </a>

                <button
                  onClick={() => viewDocDetails(doc.id)}
                  className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition-all shadow-2xs"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>View Explanation</span>
                </button>
              </div>

            </div>
          );
        })}
      </div>

      {/* Prescription Explanation Modal */}
      {activeModalData && (
        <PrescriptionExplanation
          data={activeModalData}
          language={language}
          t={t}
          onClose={closeModal}
        />
      )}

    </div>
  );
}
