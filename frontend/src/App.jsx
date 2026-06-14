import { useState, useRef, useCallback, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  X, 
  AlertCircle, 
  AudioLines, 
  Download, 
  RefreshCcw, 
  Sparkles,
  Disc3,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Volume1,
  Clipboard,
  Check,
  Trash2,
  BookOpen,
  Music,
  History
} from 'lucide-react';
import './App.css';

// Ambient Glow Background Component
const AmbientBackground = () => (
  <div className="ambient-glow" aria-hidden="true">
    <div className="ambient-blob blob-1"></div>
    <div className="ambient-blob blob-2"></div>
    <div className="ambient-blob blob-3"></div>
  </div>
);

// Voice Catalog Data
const EDGE_TTS_VOICES = [
  { id: 'en-US-AriaNeural', name: 'Aria', accent: 'US Accent', desc: 'Female • Crisp', flag: '🇺🇸', gender: 'female' },
  { id: 'en-US-GuyNeural', name: 'Guy', accent: 'US Accent', desc: 'Male • Conversational', flag: '🇺🇸', gender: 'male' },
  { id: 'en-GB-SoniaNeural', name: 'Sonia', accent: 'UK Accent', desc: 'Female • Clear & Warm', flag: '🇬🇧', gender: 'female' },
  { id: 'en-GB-RyanNeural', name: 'Ryan', accent: 'UK Accent', desc: 'Male • Balanced', flag: '🇬🇧', gender: 'male' },
  { id: 'en-AU-NatashaNeural', name: 'Natasha', accent: 'AU Accent', desc: 'Female • Lively', flag: '🇦🇺', gender: 'female' },
  { id: 'en-AU-WilliamNeural', name: 'William', accent: 'AU Accent', desc: 'Male • Natural', flag: '🇦🇺', gender: 'male' }
];

function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('synthesizer'); // 'synthesizer' | 'library'

  // Input States
  const [file, setFile] = useState(null);
  const [voice, setVoice] = useState('en-US-AriaNeural');
  const [mode, setMode] = useState('lecture'); // 'lecture' | 'direct'
  
  // Status States
  const [text, setText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [audioFilename, setAudioFilename] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragActive, setIsDragActive] = useState(false);
  
  // Clipboard copied feedback state
  const [copied, setCopied] = useState(false);

  // Conversion History (Stored in LocalStorage)
  const [history, setHistory] = useState([]);

  // Audio Player Node States
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  
  const audioRef = useRef(null);
  const fileInputRef = useRef(null);

  // Load history on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('slide2audio_history');
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (e) {
      console.error('Failed to load history', e);
    }
  }, []);

  // Sync player volume updates
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  // Audio HTML Listeners hooks
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  // Drag and Drop callbacks
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const processFile = useCallback((selectedFile) => {
    const validTypes = ['.txt', '.pdf', '.docx', '.pptx'];
    const isValid = validTypes.some(type => selectedFile.name.toLowerCase().endsWith(type));
    
    if (!isValid) {
      setError('Unsupported format. Please upload .txt, .pdf, .docx, or .pptx');
      return;
    }

    setFile(selectedFile);
    setText('');
    setAudioUrl('');
    setAudioFilename('');
    setError('');
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  }, [processFile]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };
  
  const handleRemoveFile = (e) => {
    e.stopPropagation();
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Convert File API request
  const handleConvert = async () => {
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('voice', voice);
    formData.append('mode', mode);

    try {
      const response = await fetch('/convert', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Conversion failed. The file may contain no readable text.');
      }
      
      const data = await response.json();
      const relativeAudioUrl = `/audio/${data.audio_filename}`;
      
      setText(data.text_content);
      setAudioFilename(data.audio_filename);
      setAudioUrl(relativeAudioUrl);

      // Save to history list
      const selectedVoiceObj = EDGE_TTS_VOICES.find(v => v.id === voice) || EDGE_TTS_VOICES[0];
      const newHistoryItem = {
        id: Date.now(),
        fileName: file.name,
        fileSize: formatFileSize(file.size),
        voiceName: `${selectedVoiceObj.name} (${selectedVoiceObj.flag} ${selectedVoiceObj.accent})`,
        mode: mode,
        audioFilename: data.audio_filename,
        textContent: data.text_content,
        date: new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
      };

      const updatedHistory = [newHistoryItem, ...history];
      setHistory(updatedHistory);
      localStorage.setItem('slide2audio_history', JSON.stringify(updatedHistory));

    } catch (err) {
      setError(err.message || 'Failed to convert file. Please check connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Reset current panel back to upload state
  const handleReset = () => {
    setFile(null);
    setText('');
    setAudioUrl('');
    setAudioFilename('');
    setError('');
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  };

  // Custom Audio player triggers
  const togglePlayPause = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch(e => console.error("Playback interrupted", e));
      setIsPlaying(true);
    }
  };

  const handleScrubChange = (e) => {
    const val = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (val > 0 && isMuted) {
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const formatTime = (secs) => {
    if (isNaN(secs)) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  // Clipboard copy helper
  const handleCopyToClipboard = () => {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(err => {
      console.error('Could not copy text: ', err);
    });
  };

  // Library actions helper
  const handleLoadFromHistory = (item) => {
    handleReset();
    setFile({ name: item.fileName, size: 0 }); // dummy object to pass file checking
    setText(item.textContent);
    setAudioFilename(item.audioFilename);
    setAudioUrl(`/audio/${item.audioFilename}`);
    
    // Pick the correct mode/voice
    const matchVoice = EDGE_TTS_VOICES.find(v => item.voiceName.includes(v.name));
    if (matchVoice) setVoice(matchVoice.id);
    setMode(item.mode);
    
    setActiveTab('synthesizer');
  };

  const handleDeleteHistoryItem = (id, e) => {
    e.stopPropagation();
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('slide2audio_history', JSON.stringify(updated));
  };

  // Helper to render script transcripts with custom visual bubbles for podcast discussion turns
  const renderTranscriptContent = () => {
    if (!text) return null;

    // Parse script into HOST, EXPERT, STUDENT turns using robust regex (handling optional markdown formatting)
    const speakerRegex = /^(?:\*\*|\*|__|_)?\s*(HOST|EXPERT|STUDENT)\s*(?:\*\*|\*|__|_)?\s*:\s*(.*)$/i;
    const lines = text.split('\n');
    const turns = [];
    let currentSpeaker = null;
    let currentContent = [];

    for (let line of lines) {
      line = line.trim();
      if (!line) continue;
      
      const match = line.match(speakerRegex);

      if (match) {
        if (currentSpeaker && currentContent.length > 0) {
          turns.push({ speaker: currentSpeaker, content: currentContent.join(' ') });
        }
        currentSpeaker = match[1].toUpperCase();
        currentContent = [match[2].trim()];
      } else {
        if (currentSpeaker) {
          currentContent.push(line);
        } else {
          currentSpeaker = "HOST";
          currentContent.push(line);
        }
      }
    }

    if (currentSpeaker && currentContent.length > 0) {
      turns.push({ speaker: currentSpeaker, content: currentContent.join(' ') });
    }

    const isDiscussion = turns.length >= 2 && turns.some(t => t.speaker === "EXPERT" || t.speaker === "STUDENT");

    if (isDiscussion) {
      return (
        <div className="discussion-chat">
          {turns.map((turn, idx) => (
            <div key={idx} className={`chat-turn ${turn.speaker.toLowerCase()}`}>
              <div className="chat-avatar-badge">
                <span className="chat-icon">
                  {turn.speaker === 'HOST' ? '🎙️' : turn.speaker === 'EXPERT' ? '🔬' : '🙋'}
                </span>
                <span className="chat-name">{turn.speaker}</span>
              </div>
              <div className="chat-bubble">
                {turn.content}
              </div>
            </div>
          ))}
        </div>
      );
    }

    // Render lecture/direct mode text with proper paragraph formatting
    const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim());
    if (paragraphs.length <= 1) {
      // If there's no blank-line separation, split on single newlines for basic paragraph flow
      const singleLines = text.split('\n').filter(l => l.trim());
      return (
        <div className="plain-transcript">
          {singleLines.map((line, idx) => (
            <p key={idx} className="transcript-paragraph">{line.trim()}</p>
          ))}
        </div>
      );
    }
    return (
      <div className="plain-transcript">
        {paragraphs.map((para, idx) => (
          <p key={idx} className="transcript-paragraph">{para.trim()}</p>
        ))}
      </div>
    );
  };

  return (
    <>
      <AmbientBackground />
      <div className="app-container">
        
        {/* Navigation Navbar */}
        <nav className="app-navbar glass-panel">
          <div className="logo-container">
            <Disc3 className={`logo-icon ${isPlaying ? 'is-playing' : ''}`} size={28} />
            <span className="logo-text">Slide2Audio</span>
          </div>
          
          <div className="nav-tabs">
            <button 
              className={`tab-btn ${activeTab === 'synthesizer' ? 'active' : ''}`}
              onClick={() => setActiveTab('synthesizer')}
            >
              <Music size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
              Synthesizer
            </button>
            <button 
              className={`tab-btn ${activeTab === 'library' ? 'active' : ''}`}
              onClick={() => setActiveTab('library')}
            >
              <History size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
              My Library ({history.length})
            </button>
          </div>
        </nav>
        
        <main className="app-main">
          {activeTab === 'synthesizer' ? (
            <>
              {/* Hero Header */}
              {!loading && !audioUrl && (
                <div className="hero-wrapper">
                  <div className="pill-badge">
                    <Sparkles size={13} />
                    OpenRouter AI Enabled
                  </div>
                  <h1 className="hero-title">Fluid Synthesis</h1>
                  <p className="hero-subtitle">
                    Transform slides, reports, and PDFs into premium conversational spoken audio. 
                    Synthesized locally with high-fidelity speech outputs.
                  </p>
                </div>
              )}

              {/* Upload Dropzone */}
              {!loading && !audioUrl && !file && (
                <div 
                  className={`dropzone-container glass-panel ${isDragActive ? 'drag-active' : ''}`}
                  onClick={() => fileInputRef.current?.click()}
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragEnter}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  role="button"
                  tabIndex={0}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    onChange={handleFileChange} 
                    accept=".txt,.pdf,.docx,.pptx"
                    className="file-input"
                    aria-label="Upload document"
                  />
                  <div className="icon-ring">
                    <UploadCloud size={30} />
                  </div>
                  <div className="dropzone-text" style={{ textAlign: 'center' }}>
                    <h3>Drop your slides or documents</h3>
                    <p>Or click to browse your local files</p>
                  </div>
                  <div className="format-badges">
                    <span className="badge">.PDF</span>
                    <span className="badge">.PPTX</span>
                    <span className="badge">.DOCX</span>
                    <span className="badge">.TXT</span>
                  </div>
                </div>
              )}

              {/* Setup Configuration Panel */}
              {!loading && !audioUrl && file && (
                <div className="setup-panel glass-panel">
                  <div className="setup-header">
                    <div className="file-info">
                      <div className="file-icon-bg">
                        <FileText size={22} />
                      </div>
                      <div>
                        <span className="setup-file-name" title={file.name}>{file.name}</span>
                        {file.size > 0 && <span className="setup-file-size">{formatFileSize(file.size)}</span>}
                      </div>
                    </div>
                    <button className="btn-remove" onClick={handleRemoveFile} aria-label="Remove file">
                      <X size={16} />
                    </button>
                  </div>

                  <div className="config-grid">
                    {/* Mode Selection */}
                    <div className="config-section">
                      <span className="section-label">
                        <BookOpen size={14} />
                        Reading Mode
                      </span>
                      <div className="mode-selector">
                        <button 
                          className={`mode-card ${mode === 'lecture' ? 'active' : ''}`}
                          onClick={() => setMode('lecture')}
                        >
                          <div className="mode-bullet"></div>
                          <div className="mode-details">
                            <h4>AI Lecture Script</h4>
                            <p>Rewrites contents into a fluid, conversational lecture using OpenRouter LLM before speaking.</p>
                          </div>
                        </button>
                        <button 
                          className={`mode-card ${mode === 'discussion' ? 'active' : ''}`}
                          onClick={() => setMode('discussion')}
                        >
                          <div className="mode-bullet"></div>
                          <div className="mode-details">
                            <h4>AI Discussion (Podcast)</h4>
                            <p>Rewrites contents into a multi-voice conversation (Host, Expert, Student) explaining concepts to each other.</p>
                          </div>
                        </button>
                        <button 
                          className={`mode-card ${mode === 'direct' ? 'active' : ''}`}
                          onClick={() => setMode('direct')}
                        >
                          <div className="mode-bullet"></div>
                          <div className="mode-details">
                            <h4>Direct Reading</h4>
                            <p>Speaks the exact extracted text from the document directly without AI modifications.</p>
                          </div>
                        </button>
                      </div>
                    </div>

                    {/* Custom Voice Card Grid */}
                    <div className="config-section">
                      <span className="section-label">
                        <AudioLines size={14} />
                        Voice Selector
                      </span>
                      <div className="voice-grid">
                        {EDGE_TTS_VOICES.map((v) => (
                          <button
                            key={v.id}
                            className={`voice-card ${voice === v.id ? 'active' : ''}`}
                            onClick={() => setVoice(v.id)}
                          >
                            <div className="voice-meta-details">
                              <span className="voice-name">{v.name} {v.flag}</span>
                              <span className="voice-desc">{v.desc}</span>
                            </div>
                            <div className="voice-badge-row">
                              <span className="voice-badge accent">{v.accent.split(' ')[0]}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="action-bar">
                    <button className="btn-synthesize" onClick={handleConvert}>
                      <AudioLines size={20} />
                      Generate Spoken Audio
                    </button>
                  </div>
                </div>
              )}
              
              {/* Loader Visualizer */}
              {loading && (
                <div className="loading-panel">
                  <div className="loader-bars">
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                    <div className="loader-bar"></div>
                  </div>
                  <div className="loading-text-glow">
                    {mode === 'lecture' 
                      ? 'Generating AI Lecture Script & Synthesizing Speech...' 
                      : mode === 'discussion'
                        ? 'Generating Podcast Discussion & Synthesizing Multi-Voice Speech...'
                        : 'Extracting Document Text & Synthesizing Speech...'}
                  </div>
                </div>
              )}

              {/* Conversion Results Display */}
              {!loading && audioUrl && text && (
                <div className="results-grid">
                  
                  {/* Custom Glass Audio Player */}
                  <div className="audio-card glass-panel">
                    <div className="audio-title-header" title={file?.name || 'Synthesized Track'}>
                      {file?.name || 'Synthesized Track'}
                    </div>
                    
                    <div className="disc-wrapper">
                      <div className={`visualizer-halo ${isPlaying ? 'is-playing' : ''}`}></div>
                      <div className={`vinyl-disc ${isPlaying ? 'spinning' : ''}`}>
                        <div className="vinyl-core">
                          <div className="vinyl-center-pin"></div>
                        </div>
                      </div>
                    </div>

                    {/* Hidden Native Audio Node */}
                    <audio 
                      ref={audioRef}
                      src={audioUrl}
                      onTimeUpdate={handleTimeUpdate}
                      onLoadedMetadata={handleLoadedMetadata}
                      onEnded={handleAudioEnded}
                      style={{ display: 'none' }}
                    />

                    {/* Custom Player Controls */}
                    <div className="custom-player">
                      <div className="player-timeline">
                        <input 
                          type="range"
                          min={0}
                          max={duration || 0}
                          value={currentTime}
                          onChange={handleScrubChange}
                          className="scrub-bar"
                          aria-label="Timeline scrubbing"
                        />
                        <div className="time-stamps">
                          <span>{formatTime(currentTime)}</span>
                          <span>{formatTime(duration)}</span>
                        </div>
                      </div>

                      <div className="player-actions">
                        <div style={{ width: '38px' }}></div> {/* Spacer */}
                        <button className="btn-media play-pause" onClick={togglePlayPause} aria-label={isPlaying ? 'Pause' : 'Play'}>
                          {isPlaying ? <Pause size={22} fill="currentColor" /> : <Play size={22} fill="currentColor" style={{ marginLeft: '2px' }} />}
                        </button>
                        <button className="btn-media secondary" onClick={toggleMute} aria-label={isMuted ? 'Unmute' : 'Mute'}>
                          {isMuted || volume === 0 ? <VolumeX size={18} /> : volume < 0.4 ? <Volume1 size={18} /> : <Volume2 size={18} />}
                        </button>
                      </div>

                      <div className="volume-block">
                        <input 
                          type="range"
                          min={0}
                          max={1}
                          step={0.05}
                          value={isMuted ? 0 : volume}
                          onChange={handleVolumeChange}
                          className="volume-slider"
                          aria-label="Volume slider"
                        />
                      </div>

                      {/* Animated mini sound wave */}
                      <div className="active-wave">
                        <div className={`wave-line ${isPlaying ? 'active' : ''}`}></div>
                        <div className={`wave-line ${isPlaying ? 'active' : ''}`}></div>
                        <div className={`wave-line ${isPlaying ? 'active' : ''}`}></div>
                        <div className={`wave-line ${isPlaying ? 'active' : ''}`}></div>
                        <div className={`wave-line ${isPlaying ? 'active' : ''}`}></div>
                      </div>
                    </div>

                    <div className="player-footer">
                      <a href={audioUrl} download={`${file?.name || 'output'}.mp3`} className="btn-action-row primary">
                        <Download size={14} />
                        Download MP3
                      </a>
                      <button onClick={handleReset} className="btn-action-row">
                        <RefreshCcw size={14} />
                        Convert New
                      </button>
                    </div>
                  </div>

                  {/* Glass script display panel */}
                  <div className="transcript-card glass-panel">
                    <div className="transcript-header">
                      <div className="transcript-title-block">
                        <div className="terminal-dots">
                          <div className="dot r"></div>
                          <div className="dot y"></div>
                          <div className="dot g"></div>
                        </div>
                        <span className="transcript-title">
                          {mode === 'lecture' 
                            ? 'Generated Lecture Script' 
                            : mode === 'discussion'
                              ? 'Generated Podcast Discussion'
                              : 'Extracted Text Script'}
                        </span>
                      </div>
                      <button className="btn-copy-script" onClick={handleCopyToClipboard}>
                        {copied ? <Check size={13} style={{ color: '#27C93F' }} /> : <Clipboard size={13} />}
                        {copied ? 'Copied' : 'Copy Text'}
                      </button>
                    </div>
                     <div className="transcript-content">
                       {renderTranscriptContent()}
                     </div>
                  </div>

                </div>
              )}
            </>
          ) : (
            
            /* Library / History Tab Panel */
            <div className="library-wrapper">
              <div className="library-header">
                <h2>My Audio Library</h2>
                <p>Access your past audio synthesis conversions. Click play to listen immediately or download files directly.</p>
              </div>

              {history.length > 0 ? (
                <div className="history-list">
                  {history.map((item) => (
                    <div 
                      key={item.id} 
                      className="history-card glass-panel"
                      role="button"
                      onClick={() => handleLoadFromHistory(item)}
                    >
                      <div className="history-main-info">
                        <div className="history-icon-box">
                          <FileText size={20} />
                        </div>
                        <div className="history-card-details">
                          <div className="history-file-title" title={item.fileName}>
                            {item.fileName}
                          </div>
                          <div className="history-meta-row">
                            <span className={`history-meta-badge ${item.mode}`}>
                              {item.mode === 'lecture' 
                                ? 'AI Lecture' 
                                : item.mode === 'discussion'
                                  ? 'AI Discussion'
                                  : 'Direct Text'}
                            </span>
                            <span className="history-meta-dot"></span>
                            <span>{item.voiceName}</span>
                            <span className="history-meta-dot"></span>
                            <span>{item.fileSize}</span>
                            <span className="history-meta-dot"></span>
                            <span>{item.date}</span>
                          </div>
                        </div>
                      </div>

                      <div className="history-actions">
                        <button 
                          className="btn-history-play" 
                          onClick={() => handleLoadFromHistory(item)}
                          aria-label="Load track"
                        >
                          <Play size={15} fill="currentColor" />
                        </button>
                        <a 
                          href={`/audio/${item.audioFilename}`} 
                          download={item.fileName.replace(/\.[^/.]+$/, "") + ".mp3"}
                          className="btn-history-action"
                          onClick={(e) => e.stopPropagation()}
                          aria-label="Download MP3"
                        >
                          <Download size={14} />
                        </a>
                        <button 
                          className="btn-history-action delete" 
                          onClick={(e) => handleDeleteHistoryItem(item.id, e)}
                          aria-label="Delete history track"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-library">
                  <Music className="empty-library-icon" size={48} />
                  <h3>Your library is empty</h3>
                  <p>Synthesize slides or files in the Synthesizer tab to build your custom offline library.</p>
                </div>
              )}
            </div>
          )}
          
          {/* Central Error display banner */}
          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <div>
                <strong>Error: </strong> {error}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}

export default App;