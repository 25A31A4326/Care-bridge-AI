import React, { useState, useEffect } from 'react';
import { 
  Pill, CheckCircle2, Clock, AlertTriangle, Bell, BellRing, 
  Calendar as CalendarIcon, ShieldCheck, XCircle, Volume2 
} from 'lucide-react';
import { api } from '../../services/api';
import { notificationService } from '../../services/notifications';

export default function MedicineManagement({ patientId, language, t }) {
  const [todayDoses, setTodayDoses] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [calendarDays, setCalendarDays] = useState([]);
  const [summary, setSummary] = useState({ total: 0, taken: 0, pending: 0, missed: 0 });
  const [activeSubTab, setActiveSubTab] = useState('checklist'); // 'checklist', 'calendar', 'schedules'
  const [notificationStatus, setNotificationStatus] = useState('unknown');
  const [missedSafetyNotice, setMissedSafetyNotice] = useState(null);

  useEffect(() => {
    loadMedicineData();
  }, [patientId]);

  const loadMedicineData = async () => {
    try {
      const [todayRes, schedRes, calRes] = await Promise.all([
        api.getTodayDoses(patientId),
        api.getSchedules(patientId),
        api.getCalendarDoses(patientId)
      ]);

      if (todayRes && todayRes.doses) {
        setTodayDoses(todayRes.doses);
        setSummary(todayRes.summary);
      }
      if (schedRes && schedRes.schedules) {
        setSchedules(schedRes.schedules);
      }
      if (calRes && calRes.calendar) {
        setCalendarDays(calRes.calendar);
      }
    } catch (e) {
      console.error("Error loading medicine data:", e);
    }
  };

  const handleUpdateStatus = async (doseId, status) => {
    try {
      const res = await api.updateDoseStatus(doseId, status, '', patientId);
      if (res && res.status) {
        if (status === 'taken') {
          notificationService.playReminderChime();
        }
        if (res.missed_dose_safety) {
          setMissedSafetyNotice(res.missed_dose_safety);
        } else {
          setMissedSafetyNotice(null);
        }
        loadMedicineData();
      }
    } catch (e) {
      console.error("Error updating status:", e);
    }
  };

  const handleEnableNotifications = async () => {
    const res = await notificationService.requestPermission();
    setNotificationStatus(res.granted ? 'granted' : 'denied');
    if (res.granted) {
      notificationService.showNotification(
        "CareBridge AI Reminders Active",
        language === 'te' 
          ? "మీ మందుల వేళలకు అలారం మోగుతుంది." 
          : "Reminders active. Audio chime will play during your scheduled doses."
      );
    }
  };

  const handleTestAlarm = () => {
    notificationService.showNotification(
      "CareBridge AI Medicine Reminder",
      "Test Alarm: It's time to take your afternoon medication with water."
    );
  };

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 space-y-6 animate-in fade-in duration-200">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight flex items-center space-x-2.5">
            <Pill className="w-8 h-8 text-teal-600" />
            <span>{t.medicines.title}</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {t.medicines.subtitle}
          </p>
        </div>

        {/* Alarm & Notification Permission Banner */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleTestAlarm}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 transition-colors shadow-2xs"
            title="Test reminder sound"
          >
            <Volume2 className="w-4 h-4 text-teal-600" />
            <span>Test Alarm</span>
          </button>

          <button
            onClick={handleEnableNotifications}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-teal-600 text-white hover:bg-teal-700 text-xs font-bold transition-all shadow-xs"
          >
            <BellRing className="w-4 h-4" />
            <span>Enable Reminders</span>
          </button>
        </div>
      </div>

      {/* Missed Dose Safety Alert if triggered */}
      {missedSafetyNotice && (
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-300 flex items-start space-x-3 text-amber-950 animate-in fade-in duration-200">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-bold">
              {language === 'te' ? 'ముఖ్యమైన భద్రతా హెచ్చరిక (Missed Dose Safety)' : 'Missed Dose Safety Guidance'}
            </h4>
            <p className="text-xs mt-1 text-amber-900 leading-relaxed">
              {language === 'te' ? missedSafetyNotice.te : missedSafetyNotice.en}
            </p>
          </div>
          <button 
            onClick={() => setMissedSafetyNotice(null)}
            className="text-amber-500 hover:text-amber-800 text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
          <div className="text-xs font-bold text-slate-400 uppercase">Today's Doses</div>
          <div className="text-2xl font-black text-slate-800 mt-1">{summary.total}</div>
        </div>
        <div className="bg-emerald-50/60 p-4 rounded-2xl border border-emerald-200 shadow-2xs">
          <div className="text-xs font-bold text-emerald-700 uppercase">Taken</div>
          <div className="text-2xl font-black text-emerald-800 mt-1">{summary.taken}</div>
        </div>
        <div className="bg-amber-50/60 p-4 rounded-2xl border border-amber-200 shadow-2xs">
          <div className="text-xs font-bold text-amber-700 uppercase">Pending</div>
          <div className="text-2xl font-black text-amber-800 mt-1">{summary.pending}</div>
        </div>
        <div className="bg-rose-50/60 p-4 rounded-2xl border border-rose-200 shadow-2xs">
          <div className="text-xs font-bold text-rose-700 uppercase">Missed</div>
          <div className="text-2xl font-black text-rose-800 mt-1">{summary.missed}</div>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex border-b border-slate-200 space-x-4">
        <button
          onClick={() => setActiveSubTab('checklist')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all ${
            activeSubTab === 'checklist'
              ? 'border-teal-600 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          {t.medicines.todayChecklist}
        </button>
        <button
          onClick={() => setActiveSubTab('calendar')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all ${
            activeSubTab === 'calendar'
              ? 'border-teal-600 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          {t.medicines.sevenDayCalendar}
        </button>
        <button
          onClick={() => setActiveSubTab('schedules')}
          className={`pb-3 text-sm font-bold border-b-2 transition-all ${
            activeSubTab === 'schedules'
              ? 'border-teal-600 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Verified Schedules ({schedules.length})
        </button>
      </div>

      {/* Sub Tab 1: Today's Checklist */}
      {activeSubTab === 'checklist' && (
        <div className="space-y-3">
          {todayDoses.length === 0 ? (
            <div className="bg-white p-8 rounded-3xl border border-slate-200 text-center text-slate-500">
              No doses scheduled for today. Upload a verified prescription to activate reminders.
            </div>
          ) : (
            todayDoses.map((d) => {
              const timePart = d.scheduled_time.split(' ')[1] || d.scheduled_time;
              const isTaken = d.status === 'taken';
              const isMissed = d.status === 'missed';
              const isPending = d.status === 'pending';

              return (
                <div
                  key={d.id}
                  className={`p-4 sm:p-5 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    isTaken 
                      ? 'bg-emerald-50/40 border-emerald-200' 
                      : isMissed 
                      ? 'bg-rose-50/40 border-rose-200' 
                      : 'bg-white border-slate-200 shadow-2xs hover:shadow-xs'
                  }`}
                >
                  <div className="flex items-start space-x-3.5">
                    <div className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 mt-0.5 ${
                      isTaken ? 'bg-emerald-100 text-emerald-700' : isMissed ? 'bg-rose-100 text-rose-700' : 'bg-teal-100 text-teal-700'
                    }`}>
                      <Clock className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-bold text-slate-900">{d.medicine_name}</span>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                          {d.strength}
                        </span>
                        <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full">
                          {timePart}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        Dose: <strong className="text-slate-700">{d.dose}</strong> • {d.food_relation === 'after_food' ? 'After food (భోజనం తర్వాత)' : 'Before food'}
                      </div>
                      {isTaken && (
                        <div className="text-[11px] text-emerald-700 font-semibold mt-1 flex items-center space-x-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>{t.medicines.takenAt}: {d.taken_at ? new Date(d.taken_at).toLocaleTimeString() : 'Recorded'}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 shrink-0">
                    {isPending && (
                      <>
                        <button
                          onClick={() => handleUpdateStatus(d.id, 'taken')}
                          className="flex items-center space-x-1 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-xs"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          <span>{t.medicines.markTaken}</span>
                        </button>
                        <button
                          onClick={() => handleUpdateStatus(d.id, 'snoozed')}
                          className="px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold transition-colors"
                        >
                          {t.medicines.remindLater}
                        </button>
                        <button
                          onClick={() => handleUpdateStatus(d.id, 'missed')}
                          className="px-3 py-2 rounded-xl border border-rose-200 text-rose-700 hover:bg-rose-50 text-xs font-semibold transition-colors"
                        >
                          {t.medicines.markMissed}
                        </button>
                      </>
                    )}
                    {isTaken && (
                      <span className="px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold">
                        Completed [OK]
                      </span>
                    )}
                    {isMissed && (
                      <button
                        onClick={() => handleUpdateStatus(d.id, 'taken')}
                        className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700"
                      >
                        Change to Taken
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}

          {/* Browser Notification Disclaimer */}
          <div className="mt-4 p-4 rounded-2xl bg-slate-100 text-slate-600 text-xs leading-relaxed border border-slate-200">
            <strong>Notice on Reminder Reliability:</strong> {t.medicines.browserNotificationNote}
          </div>
        </div>
      )}

      {/* Sub Tab 2: 7-Day Calendar */}
      {activeSubTab === 'calendar' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-7 gap-3">
            {calendarDays.map((day, idx) => (
              <div 
                key={idx} 
                className={`p-3.5 rounded-2xl border text-center transition-all ${
                  day.is_today 
                    ? 'border-teal-500 bg-teal-50/50 ring-2 ring-teal-500/20' 
                    : 'border-slate-200 bg-white'
                }`}
              >
                <div className="text-xs font-bold text-slate-500">{day.day_name}</div>
                <div className="text-lg font-black text-slate-800 my-1">
                  {day.date.split('-')[2]}
                </div>
                {day.is_today && (
                  <span className="text-[10px] font-extrabold text-teal-800 uppercase px-1.5 py-0.5 bg-teal-100 rounded-md">
                    Today
                  </span>
                )}
                <div className="mt-3 space-y-1 text-left">
                  <div className="text-[10px] text-slate-500">Total: {day.total}</div>
                  <div className="text-[10px] font-bold text-emerald-700">Taken: {day.taken}</div>
                  <div className="text-[10px] font-bold text-rose-700">Missed: {day.missed}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub Tab 3: Verified Schedules */}
      {activeSubTab === 'schedules' && (
        <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50">
            <h3 className="text-sm font-bold text-slate-800">
              Prescription-Grounded Medicine Schedules
            </h3>
            <p className="text-xs text-slate-500">
              Only verified schedules with confirmed clock times trigger automatic reminders.
            </p>
          </div>

          <div className="divide-y divide-slate-100">
            {schedules.map((s) => (
              <div key={s.id} className="p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-800">{s.medicine_name}</span>
                    <span className="text-xs text-slate-500">{s.strength}</span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                      Verified
                    </span>
                  </div>
                  <div className="text-xs text-slate-600 mt-1">
                    Dose: {s.dose} • {s.frequency} at {s.exact_times} ({s.food_relation})
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    {s.verification_notes || 'Confirmed from hospital discharge summary'}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500 font-medium">Duration: {s.duration_days} days</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
