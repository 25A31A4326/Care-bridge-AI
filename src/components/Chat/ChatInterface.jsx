import React, { useState, useEffect, useRef } from 'react';
import { Plus, Mic, Send, Sparkles, Loader2, FileUp, AlertCircle, HeartHandshake } from 'lucide-react';
import MessageBubble from './MessageBubble';
import PlusMenu from './PlusMenu';
import VoiceInputModal from './VoiceInputModal';
import PrescriptionExplanation from '../Prescription/PrescriptionExplanation';
import { api } from '../../services/api';

export default function ChatInterface({ patientId, language, t, onOpenDocDetails }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPlusMenuOpen, setIsPlusMenuOpen] = useState(false);
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadResultModalData, setUploadResultModalData] = useState(null);
  const messagesEndRef = useRef(null);

  // Load chat history
  useEffect(() => {
    loadChatHistory();
  }, [patientId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, uploadProgress]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const res = await api.getChatHistory(patientId);
      if (res && res.messages) {
        setMessages(res.messages);
      }
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
  };

  const handleSendMessage = async (textToSend = null) => {
    const text = (textToSend !== null ? textToSend : inputValue).trim();
    if (!text || isLoading) return;

    setInputValue('');
    setIsLoading(true);

    // Optimistically add user message
    const tempUserMsg = {
      id: Date.now(),
      sender_role: 'user',
      content_en: language === 'en' ? text : text,
      content_te: language === 'te' ? text : text,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const res = await api.sendMessage(patientId, text, language);
      if (res && res.assistant_message) {
        setMessages(prev => [...prev, res.assistant_message]);
      }
    } catch (e) {
      console.error("Error sending message:", e);
      const errorMsg = {
        id: Date.now() + 1,
        sender_role: 'assistant',
        content_en: "Sorry, I encountered an error communicating with the healthcare server. Please try again.",
        content_te: "క్షమించండి, సర్వర్‌తో కనెక్ట్ అవ్వడంలో సమస్య ఎదురైంది. దయచేసి మళ్ళీ ప్రయత్నించండి."
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file, uploadType) => {
    setUploadProgress({
      filename: file.name,
      status: 'uploading',
      message: language === 'te' ? 'పత్రం అప్‌లోడ్ అవుతోంది...' : 'Uploading document securely...'
    });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);
    formData.append('upload_type', uploadType);

    try {
      setUploadProgress({
        filename: file.name,
        status: 'extracting',
        message: language === 'te' ? 'అక్షరాలను విశ్లేషిస్తున్నాము (OCR)...' : 'Extracting text and verifying instructions (OCR)...'
      });

      const res = await api.uploadDocument(formData);
      
      if (res && res.status === 'success') {
        setUploadProgress(null);
        setUploadResultModalData(res);

        // Add assistant notification in chat
        const assistMsg = {
          id: Date.now(),
          sender_role: 'assistant',
          content_en: `I have analyzed **${res.filename}** (${res.extraction_status.toUpperCase()}).\n\n${res.simple_explanation_en}`,
          content_te: `నేను మీ **${res.filename}** పత్రాన్ని విశ్లేషించాను.\n\n${res.simple_explanation_te}`,
          source_document_id: res.document_id
        };
        setMessages(prev => [...prev, assistMsg]);
      } else {
        setUploadProgress({
          filename: file.name,
          status: 'error',
          message: res?.error || 'Document processing failed.'
        });
      }
    } catch (e) {
      setUploadProgress({
        filename: file.name,
        status: 'error',
        message: e.message || 'File upload error.'
      });
    }
  };

  const quickPrompts = language === 'te' ? [
    "నా మందులు ఎప్పుడు తీసుకోవాలి?",
    "నా డాక్టర్ ప్రిస్క్రిప్షన్లో ఏమి రాశారు?",
    "నా తదుపరి డాక్టర్ అపాయింట్‌మెంట్ ఎప్పుడు?",
    "డిశ్చార్జ్ సమ్మరీని సులభంగా వివరించండి"
  ] : [
    "What is the next medicine in my schedule?",
    "What does my prescription say?",
    "When is my follow-up appointment?",
    "Explain my discharge summary in simple terms"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-4.5rem)] max-w-4xl mx-auto w-full px-2 sm:px-4">
      
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto pt-4 pb-2 px-2 sm:px-3 space-y-4">
        
        {/* Welcome Greeting Banner */}
        {messages.length <= 1 && (
          <div className="py-6 sm:py-10 text-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-16 h-16 rounded-3xl bg-teal-100 text-teal-700 flex items-center justify-center mx-auto mb-4 shadow-sm shadow-teal-600/10">
              <Sparkles className="w-8 h-8" />
            </div>
            
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight mb-2">
              {language === 'te' ? 'కేర్‌బ్రిడ్జ్ AI సహాయకుడు' : 'CareBridge AI Assistant'}
            </h1>
            
            <p className="text-slate-600 max-w-md mx-auto text-base sm:text-lg font-medium">
              {t.greeting}
            </p>

            {/* Quick Prompt Pills */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-6 max-w-xl mx-auto">
              {quickPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(p)}
                  className="px-4 py-2 rounded-2xl border border-slate-200 bg-white hover:border-teal-500 hover:bg-teal-50/50 text-xs sm:text-sm font-semibold text-slate-700 transition-all shadow-2xs hover:shadow-xs active:scale-98"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message Bubble List */}
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            language={language}
            t={t}
            onOpenDocDetails={onOpenDocDetails}
          />
        ))}

        {/* Upload In-Progress State */}
        {uploadProgress && (
          <div className="p-4 rounded-2xl bg-teal-50/80 border border-teal-200 flex items-center space-x-3 text-sm text-teal-900 animate-pulse">
            <FileUp className="w-5 h-5 text-teal-600 shrink-0" />
            <div className="flex-1">
              <div className="font-bold">{uploadProgress.filename}</div>
              <div className="text-xs text-teal-700 mt-0.5">{uploadProgress.message}</div>
            </div>
            <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
          </div>
        )}

        {/* Thinking / Loading Indicator */}
        {isLoading && (
          <div className="flex items-center space-x-2 p-4 text-slate-500 text-sm">
            <div className="w-8 h-8 rounded-2xl bg-teal-600 text-white flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="flex items-center space-x-1.5 bg-white border border-slate-200 px-4 py-2.5 rounded-2xl shadow-xs">
              <span className="text-xs font-semibold text-teal-800">
                {language === 'te' ? 'ఆలోచిస్తున్నాను...' : 'Reviewing verified medical instructions...'}
              </span>
              <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce"></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Persistent Rounded Message Composer at Bottom */}
      <div className="py-3 px-1 sm:px-2 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent">
        <div className="relative flex items-center bg-white rounded-3xl border-2 border-slate-200/90 hover:border-teal-500/80 focus-within:border-teal-500 focus-within:ring-4 focus-within:ring-teal-500/10 shadow-lg shadow-slate-200/50 p-2 transition-all">
          
          {/* 1. Plus (+) Attachment Button */}
          <button
            onClick={() => setIsPlusMenuOpen(true)}
            className="w-11 h-11 rounded-2xl flex items-center justify-center text-slate-600 hover:text-teal-700 hover:bg-teal-50 transition-colors shrink-0"
            title={t.composer.attachMenu}
          >
            <Plus className="w-6 h-6 stroke-[2.5]" />
          </button>

          {/* 2. Text Input */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder={t.composer.placeholder}
            className="flex-1 px-3 py-2 text-base text-slate-900 bg-transparent placeholder-slate-400 focus:outline-none font-medium"
            disabled={isLoading}
          />

          {/* 3. Microphone Button */}
          <button
            onClick={() => setIsVoiceModalOpen(true)}
            className="w-11 h-11 rounded-2xl flex items-center justify-center text-slate-600 hover:text-teal-700 hover:bg-teal-50 transition-colors shrink-0"
            title={t.composer.tapToSpeak}
          >
            <Mic className="w-5 h-5" />
          </button>

          {/* 4. Send Button */}
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading}
            className="w-11 h-11 rounded-2xl bg-teal-600 text-white flex items-center justify-center hover:bg-teal-700 transition-all shadow-md shadow-teal-600/30 disabled:opacity-40 disabled:hover:bg-teal-600 disabled:shadow-none shrink-0 ml-1 active:scale-95"
            title={t.composer.send}
          >
            <Send className="w-5 h-5 stroke-[2.5]" />
          </button>

        </div>

        <div className="text-center mt-1.5">
          <span className="text-[11px] text-slate-400">
            CareBridge AI is designed for elderly support. Source-grounded advice only. Always consult your doctor.
          </span>
        </div>
      </div>

      {/* Plus Attachment Popover Menu */}
      <PlusMenu
        isOpen={isPlusMenuOpen}
        onClose={() => setIsPlusMenuOpen(false)}
        onFileSelect={handleFileUpload}
        t={t}
        language={language}
      />

      {/* Voice Recognition Modal */}
      <VoiceInputModal
        isOpen={isVoiceModalOpen}
        onClose={() => setIsVoiceModalOpen(false)}
        onSubmit={(voiceText) => handleSendMessage(voiceText)}
        language={language}
        t={t}
      />

      {/* Prescription Explanation Modal upon upload */}
      {uploadResultModalData && (
        <PrescriptionExplanation
          data={uploadResultModalData}
          language={language}
          t={t}
          onClose={() => setUploadResultModalData(null)}
        />
      )}

    </div>
  );
}
