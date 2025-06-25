import React, { useState, useRef } from "react";
import axios from "axios";
import { 
  Upload, 
  FileText, 
  Volume2, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Banknote,
  Shield,
  Languages,
  PlayCircle,
  PauseCircle
} from "lucide-react";
import styles from './App.module.css';

function App() {
  const [audioURL, setAudioURL] = useState(null);
  const [explanation, setExplanation] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  const handleUpload = async (file) => {
    if (!file) return;

    setIsLoading(true);
    setError("");
    setExplanation("");
    setAudioURL(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setAudioURL(res.data.audio_url);
      setExplanation(res.data.explanation);
    } catch (err) {
      console.error("Upload error:", err);
      setError("Upload failed. Please try again. / अपलोड असफल। कृपया पुनः प्रयास करें।");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const toggleAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerTop}>
            <div className={styles.logoContainer}>
              <Banknote className={styles.logoIcon} />
            </div>
            <div className={styles.headerTitles}>
              <h1>Banking Document Explainer</h1>
              <p>बैंकिंग दस्तावेज़ व्याख्याकार</p>
            </div>
          </div>
          
          <div className={styles.headerFeatures}>
            <div className={styles.featureItem}>
              <Shield className={styles.featureIcon} />
              <span>Secure & Private / सुरक्षित और निजी</span>
            </div>
            <div className={styles.featureItem}>
              <Languages className={styles.featureIcon} />
              <span>Hindi Explanations / हिंदी में व्याख्या</span>
            </div>
            <div className={styles.featureItem}>
              <Volume2 className={styles.featureIcon} />
              <span>Audio Support / ऑडियो सहायता</span>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.mainContent}>
        {/* Upload Section */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardHeaderTitle}>
              <FileText className={styles.cardHeaderIcon} />
              Upload Your Document / अपना दस्तावेज़ अपलोड करें
            </h2>
            <p className={styles.cardHeaderSubtitle}>
              Upload banking or financial documents to get detailed explanations in Hindi
            </p>
            <p className={styles.cardHeaderSubtitleSmall}>
              हिंदी में विस्तृत व्याख्या के लिए बैंकिंग या वित्तीय दस्तावेज़ अपलोड करें
            </p>
          </div>

          <div className={styles.cardContent}>
            <div
              className={`${styles.uploadZone} ${
                isDragOver ? styles.uploadZoneDragOver : ''
              } ${isLoading ? styles.uploadZoneLoading : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !isLoading && fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className={styles.hiddenInput}
                disabled={isLoading}
              />

              {isLoading ? (
                <div className={styles.uploadContent}>
                  <Loader2 className={styles.loadingIcon} />
                  <div>
                    <p className={styles.loadingText}>
                      Processing your document...
                    </p>
                    <p className={styles.loadingSubtext}>
                      आपके दस्तावेज़ को प्रोसेस किया जा रहा है...
                    </p>
                  </div>
                </div>
              ) : (
                <div className={styles.uploadContent}>
                  <Upload className={styles.uploadIcon} />
                  <div>
                    <p className={styles.uploadText}>
                      Click to upload or drag and drop
                    </p>
                    <p className={styles.uploadSubtext}>
                      अपलोड करने के लिए क्लिक करें या ड्रैग और ड्रॉप करें
                    </p>
                    <button
                      className={styles.uploadButton}
                      disabled={isLoading}
                    >
                      Choose File / फ़ाइल चुनें
                    </button>
                  </div>
                  <p className={styles.uploadFormats}>
                    Supported formats: JPG, PNG, PDF / समर्थित प्रारूप: JPG, PNG, PDF
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className={styles.errorAlert}>
                <AlertCircle className={styles.errorIcon} />
                <p className={styles.errorText}>{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {(explanation || audioURL) && (
          <div className={styles.resultsSection}>
            {/* Explanation Card */}
            {explanation && (
              <div className={`${styles.card} ${styles.explanationCard}`}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.cardHeaderTitle}>
                    <CheckCircle className={styles.cardHeaderIcon} />
                    Document Explanation / दस्तावेज़ व्याख्या
                  </h3>
                </div>
                <div className={styles.cardContent}>
                  <div className={styles.explanationContent}>
                    <p className={styles.explanationText}>
                      {explanation}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Audio Player Card */}
            {audioURL && (
              <div className={`${styles.card} ${styles.audioCard}`}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.cardHeaderTitle}>
                    <Volume2 className={styles.cardHeaderIcon} />
                    Audio Explanation / ऑडियो व्याख्या
                  </h3>
                  <p className={styles.cardHeaderSubtitle}>
                    Listen to the explanation in Hindi / हिंदी में व्याख्या सुनें
                  </p>
                </div>
                <div className={styles.cardContent}>
                  <div className={styles.audioContent}>
                    <div className={styles.audioControls}>
                      <button
                        onClick={toggleAudio}
                        className={styles.audioButton}
                      >
                        {isPlaying ? (
                          <PauseCircle className={styles.audioButtonIcon} />
                        ) : (
                          <PlayCircle className={styles.audioButtonIcon} />
                        )}
                      </button>
                      <div className={styles.audioPlayer}>
                        <audio
                          ref={audioRef}
                          src={audioURL}
                          onPlay={() => setIsPlaying(true)}
                          onPause={() => setIsPlaying(false)}
                          onEnded={() => setIsPlaying(false)}
                          className={styles.audioElement}
                          controls
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Features Grid */}
        {!explanation && !audioURL && !isLoading && (
          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <div className={`${styles.featureIconContainer} ${styles.blue}`}>
                <FileText className={`${styles.featureCardIcon} ${styles.blue}`} />
              </div>
              <h3 className={styles.featureTitle}>Smart Analysis</h3>
              <p className={styles.featureDescription}>AI-powered document analysis for banking and financial documents</p>
              <p className={styles.featureDescriptionHindi}>बैंकिंग दस्तावेजों का स्मार्ट विश्लेषण</p>
            </div>

            <div className={styles.featureCard}>
              <div className={`${styles.featureIconContainer} ${styles.emerald}`}>
                <Languages className={`${styles.featureCardIcon} ${styles.emerald}`} />
              </div>
              <h3 className={styles.featureTitle}>Hindi Explanations</h3>
              <p className={styles.featureDescription}>Get detailed explanations in Hindi for better understanding</p>
              <p className={styles.featureDescriptionHindi}>बेहतर समझ के लिए हिंदी में व्याख्या</p>
            </div>

            <div className={styles.featureCard}>
              <div className={`${styles.featureIconContainer} ${styles.purple}`}>
                <Volume2 className={`${styles.featureCardIcon} ${styles.purple}`} />
              </div>
              <h3 className={styles.featureTitle}>Audio Support</h3>
              <p className={styles.featureDescription}>Listen to explanations with high-quality audio narration</p>
              <p className={styles.featureDescriptionHindi}>ऑडियो के साथ व्याख्या सुनें</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;