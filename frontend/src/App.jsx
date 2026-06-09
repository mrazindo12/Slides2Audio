import { useState, useRef, useCallback } from 'react';
import { 
  UploadCloud, 
  FileText, 
  X, 
  AlertCircle, 
  AudioLines, 
  Download, 
  RefreshCcw, 
  Sparkles,
  Disc3
} from 'lucide-react';
import './App.css';

// Background Ambience
const AmbientBackground = () => (
  <div className="ambient-glow" aria-hidden="true">
    <div className="ambient-blob blob-1"></div>
    <div className="ambient-blob blob-2"></div>
    <div className="ambient-blob blob-3"></div>
  </div>
);

// Physics-based Magnetic Button
const MagneticButton = ({ children, onClick, className = '' }) => {
  const btnRef = useRef(null);

  const handleMouseMove = (e) => {
    const btn = btnRef.current;
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    // apply slight translation based on mouse position
    btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
  };

  const handleMouseLeave = () => {
    const btn = btnRef.current;
    if (!btn) return;
    // reset position
    btn.style.transform = `translate(0px, 0px)`;
  };

  return (
    <button
      ref={btnRef}
      className={`magnetic-btn ${className}`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </button>
  );
};

// Visualizer Loader
const VisualizerLoader = () => (
  <div className="visualizer-container">
    <div className="bars">
      <div className="bar"></div>
      <div className="bar"></div>
      <div className="bar"></div>
      <div className="bar"></div>
      <div className="bar"></div>
      <div className="bar"></div>
    </div>
    <div className="loading-text">Extracting & Synthesizing</div>
  </div>
);

const EDGE_TTS_VOICES = [
  { id: 'en-US-AriaNeural', name: 'Aria (Female, US)' },
  { id: 'en-US-GuyNeural', name: 'Guy (Male, US)' },
  { id: 'en-GB-SoniaNeural', name: 'Sonia (Female, UK)' },
  { id: 'en-GB-RyanNeural', name: 'Ryan (Male, UK)' },
  { id: 'en-AU-NatashaNeural', name: 'Natasha (Female, AU)' },
  { id: 'en-AU-WilliamNeural', name: 'William (Male, AU)' }
];

function App() {
  const [file, setFile] = useState(null);
  const [voice, setVoice] = useState('en-US-AriaNeural');
  const [text, setText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragActive, setIsDragActive] = useState(false);
  
  const audioRef = useRef(null);
  const fileInputRef = useRef(null);

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

  const handleConvert = async () => {
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('voice', voice);

    try {
      const response = await fetch('http://127.0.0.1:8000/convert', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Conversion failed. The file may contain no readable text.');
      }
      
      const data = await response.json();
      setText(data.text_content);
      setAudioUrl(`http://127.0.0.1:8000/audio/${data.audio_filename}`);
    } catch (err) {
      setError(err.message || 'Failed to convert file. Please check connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setText('');
    setAudioUrl('');
    setError('');
  };

  return (
    <>
      <AmbientBackground />
      <div className="app-container">
        <nav className="app-navbar glass-panel">
          <div className="logo-container">
            <Disc3 className="logo-icon" size={28} />
            <span className="logo-text">Slide2Audio</span>
          </div>
        </nav>
        
        <main className="app-main">
          {!loading && !audioUrl && (
            <div className="hero-wrapper">
              <div className="pill-badge">
                <Sparkles size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                AI Audio Engine
              </div>
              <h1 className="hero-title">Fluid Synthesis</h1>
              <p className="hero-subtitle">Transform your documents and presentations into high-fidelity speech. Experience seamless reading with our advanced text-to-speech engine.</p>
            </div>
          )}

          {!loading && !audioUrl && (
            <div 
              className="dropzone-container glass-panel"
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
              
              {!file ? (
                <>
                  <div className="icon-ring">
                    <UploadCloud size={32} />
                  </div>
                  <div className="dropzone-text" style={{ textAlign: 'center' }}>
                    <h3>Drop your document</h3>
                    <p>Or click to browse files</p>
                  </div>
                  <div className="format-badges">
                    <span className="badge">.PDF</span>
                    <span className="badge">.PPTX</span>
                    <span className="badge">.DOCX</span>
                    <span className="badge">.TXT</span>
                  </div>
                </>
              ) : (
                <div className="file-card-wrapper" onClick={(e) => e.stopPropagation()}>
                  <div className="selected-file-glass">
                    <div className="file-meta">
                      <FileText size={32} className="file-icon-styled" />
                      <div>
                        <span className="file-name" title={file.name}>{file.name}</span>
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      </div>
                    </div>
                    <button className="remove-action" onClick={handleRemoveFile} aria-label="Remove file">
                      <X size={20} />
                    </button>
                  </div>
                  
                  <div className="voice-selector">
                    <select 
                      value={voice} 
                      onChange={(e) => setVoice(e.target.value)}
                      className="voice-dropdown"
                      aria-label="Select Voice"
                    >
                      {EDGE_TTS_VOICES.map(v => (
                        <option key={v.id} value={v.id}>{v.name}</option>
                      ))}
                    </select>
                  </div>

                  <MagneticButton onClick={handleConvert}>
                    <AudioLines size={24} />
                    <span>Synthesize</span>
                  </MagneticButton>
                </div>
              )}
            </div>
          )}
          
          {loading && <VisualizerLoader />}

          {!loading && audioUrl && text && (
            <div className="result-container">
              <div className="audio-card glass-panel">
                <div className="vinyl-record">
                  <div className="vinyl-center">
                    <div className="vinyl-hole"></div>
                  </div>
                </div>
                <audio controls src={audioUrl} ref={audioRef} className="custom-audio-player" autoPlay>
                  Your browser does not support the audio element.
                </audio>
                <div className="action-row">
                  <a href={audioUrl} download="Slide2Audio_Output.mp3" className="action-btn" aria-label="Download MP3">
                    <Download size={18} />
                    Download
                  </a>
                  <button onClick={handleReset} className="action-btn" aria-label="Convert Another">
                    <RefreshCcw size={18} />
                    Restart
                  </button>
                </div>
              </div>

              <div className="transcript-card glass-panel">
                <div className="transcript-header">
                  <div className="terminal-dots">
                    <div className="dot r"></div>
                    <div className="dot y"></div>
                    <div className="dot g"></div>
                  </div>
                  <div className="transcript-title">Extracted Script</div>
                </div>
                <div className="transcript-content">
                  {text}
                </div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle size={24} />
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