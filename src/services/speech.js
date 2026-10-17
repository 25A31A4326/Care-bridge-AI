// Web Speech Recognition & Synthesis Service

class SpeechService {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.voices = [];
    
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
      }
      
      if (this.synth) {
        this.loadVoices();
        if (this.synth.onvoiceschanged !== undefined) {
          this.synth.onvoiceschanged = () => this.loadVoices();
        }
      }
    }
  }

  loadVoices() {
    if (!this.synth) return;
    this.voices = this.synth.getVoices();
  }

  isSpeechRecognitionSupported() {
    return !!this.recognition;
  }

  isSpeechSynthesisSupported() {
    return !!this.synth;
  }

  startListening(lang = 'te', onResult, onError, onEnd) {
    if (!this.recognition) {
      if (onError) onError('Speech recognition is not supported in this browser.');
      return;
    }

    this.recognition.lang = lang === 'te' ? 'te-IN' : 'en-US';
    this.isListening = true;

    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (onResult) {
        onResult({
          transcript: finalTranscript || interimTranscript,
          isFinal: !!finalTranscript
        });
      }
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      if (onError) {
        let msg = 'Speech recognition error occurred.';
        if (event.error === 'not-allowed') {
          msg = 'Microphone permission was denied. Please allow microphone access.';
        } else if (event.error === 'no-speech') {
          msg = 'No speech was detected. Please try again.';
        }
        onError(msg);
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (onEnd) onEnd();
    };

    try {
      this.recognition.start();
    } catch (e) {
      this.isListening = false;
      if (onError) onError(e.message);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  speak(text, lang = 'te', onEnd, onStart, onNoVoice) {
    if (!this.synth) return;

    this.stopSpeaking();

    // Always refresh voice list — browsers load voices asynchronously
    this.loadVoices();

    // Clean markdown formatting before speaking
    const cleanText = text.replace(/[*#_`\[\]]/g, '').trim();
    if (!cleanText) return;

    const langCode = lang === 'te' ? 'te-IN' : 'en-US';
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = langCode;
    utterance.rate = 0.85; // Slightly slower for elderly clarity
    utterance.pitch = 1.0;

    // Voice selection: exact match → loose match → fallback
    const voices = this.synth.getVoices();
    const exactMatch = voices.find(v => v.lang === langCode);
    const looseMatch = voices.find(v => v.lang.startsWith(lang === 'te' ? 'te' : 'en'));
    const englishFallback = voices.find(v => v.lang.startsWith('en'));

    if (exactMatch) {
      utterance.voice = exactMatch;
    } else if (looseMatch) {
      utterance.voice = looseMatch;
    } else if (lang === 'te') {
      // No Telugu voice available in this browser
      if (onNoVoice) {
        onNoVoice('Telugu (te-IN) voice is not available in this browser. Reading aloud in English instead.');
      }
      utterance.lang = 'en-US';
      if (englishFallback) utterance.voice = englishFallback;
    } else if (englishFallback) {
      utterance.voice = englishFallback;
    }

    if (onStart) utterance.onstart = onStart;
    if (onEnd) utterance.onend = onEnd;
    utterance.onerror = () => {
      if (onEnd) onEnd();
    };

    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.synth) {
      this.synth.cancel();
    }
  }
}

export const speech = new SpeechService();
