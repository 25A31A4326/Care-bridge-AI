// In-App Sound Alarm & Browser Notification Manager

class NotificationService {
  constructor() {
    this.audioCtx = null;
  }

  // Play a gentle, high-clarity medical reminder chime using Web Audio API
  playReminderChime() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      
      if (!this.audioCtx) {
        this.audioCtx = new AudioContext();
      }

      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = 'sine';
      // Pleasant two-tone chime (523Hz C5 -> 659Hz E5)
      osc.frequency.setValueAtTime(523.25, now);
      osc.frequency.setValueAtTime(659.25, now + 0.15);

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.exponentialRampToValueAtTime(0.3, now + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start(now);
      osc.stop(now + 0.6);
    } catch (e) {
      console.warn("Audio alarm warning:", e);
    }
  }

  async requestPermission() {
    if (!('Notification' in window)) {
      return { supported: false, granted: false };
    }
    try {
      const permission = await Notification.requestPermission();
      return {
        supported: true,
        granted: permission === 'granted',
        status: permission
      };
    } catch (e) {
      return { supported: true, granted: false, error: e.message };
    }
  }

  hasPermission() {
    return 'Notification' in window && Notification.permission === 'granted';
  }

  showNotification(title, body) {
    // Always trigger sound chime
    this.playReminderChime();

    if (this.hasPermission()) {
      try {
        new Notification(title, {
          body,
          icon: '/favicon.svg',
          badge: '/favicon.svg',
          vibrate: [200, 100, 200]
        });
      } catch (e) {
        console.warn("Notification error:", e);
      }
    }
  }
}

export const notificationService = new NotificationService();
