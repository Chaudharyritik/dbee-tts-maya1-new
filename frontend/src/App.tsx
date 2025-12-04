import { useState } from 'react';
import axios from 'axios';
import { Play, Download, History, Mic, Sparkles, Volume2 } from 'lucide-react';
import { cn } from './lib/utils';

interface SynthesisResponse {
  audio_base64: string;
  sample_rate: number;
}

interface HistoryItem {
  id: string;
  text: string;
  audioUrl: string;
  timestamp: Date;
}

function App() {
  const [text, setText] = useState('');
  const [voiceDesc, setVoiceDesc] = useState('Young British female, energetic');
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const insertTag = (tag: string) => {
    setText((prev) => prev + ` <${tag}> `);
  };

  const handleSynthesize = async () => {
    if (!text.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post<SynthesisResponse>('/api/synthesize', {
        text,
        voice_description: voiceDesc,
        speed: 1.0,
      });

      const audioData = response.data.audio_base64;
      const binaryString = window.atob(audioData);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      setAudioUrl(url);
      setHistory((prev) => [
        {
          id: Date.now().toString(),
          text: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
          audioUrl: url,
          timestamp: new Date(),
        },
        ...prev,
      ]);
    } catch (error) {
      console.error('Synthesis failed:', error);
      alert('Failed to synthesize audio. Ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-gray-800 p-6 flex items-center justify-between bg-secondary/30 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/20 rounded-lg">
            <Sparkles className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Maya1 TTS Studio</h1>
        </div>
        <div className="text-sm text-muted-foreground">
          Powered by Maya Research
        </div>
      </header>

      <main className="flex-1 container mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Controls */}
        <div className="lg:col-span-7 space-y-6">

          {/* Voice Description */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Mic className="w-4 h-4" /> Voice Description
            </label>
            <input
              type="text"
              value={voiceDesc}
              onChange={(e) => setVoiceDesc(e.target.value)}
              className="w-full bg-secondary/50 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all placeholder:text-gray-600"
              placeholder="e.g., Old American man, deep voice, slow pace"
            />
          </div>

          {/* Text Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-muted-foreground">Input Text</label>
              <div className="flex gap-2">
                {['laugh', 'cry', 'whisper', 'gasp', 'sigh'].map((tag) => (
                  <button
                    key={tag}
                    onClick={() => insertTag(tag)}
                    className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-2 py-1 rounded-md transition-colors border border-gray-700"
                  >
                    &lt;{tag}&gt;
                  </button>
                ))}
              </div>
            </div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full h-64 bg-secondary/50 border border-gray-700 rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none font-mono text-sm leading-relaxed"
              placeholder="Type something here... Use the tags above for expressions."
            />
          </div>

          {/* Synthesize Button */}
          <button
            onClick={handleSynthesize}
            disabled={isLoading || !text}
            className={cn(
              "w-full py-4 rounded-lg font-bold text-lg shadow-lg transition-all flex items-center justify-center gap-2",
              isLoading
                ? "bg-gray-800 text-gray-500 cursor-not-allowed"
                : "bg-primary hover:bg-primary/90 text-primary-foreground hover:shadow-primary/25 hover:scale-[1.01]"
            )}
          >
            {isLoading ? (
              <>Synthesizing...</>
            ) : (
              <>
                <Volume2 className="w-5 h-5" /> Synthesize Speech
              </>
            )}
          </button>
        </div>

        {/* Right Column: Output & History */}
        <div className="lg:col-span-5 space-y-6">
          {/* Current Player */}
          <div className="bg-secondary/30 border border-gray-800 rounded-xl p-6 space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Play className="w-5 h-5 text-primary" /> Current Output
            </h2>
            {audioUrl ? (
              <div className="space-y-4">
                <audio controls src={audioUrl} className="w-full" autoPlay />
                <div className="flex justify-end">
                  <a
                    href={audioUrl}
                    download={`maya1-synthesis-${Date.now()}.wav`}
                    className="text-sm flex items-center gap-2 text-primary hover:text-primary/80 transition-colors"
                  >
                    <Download className="w-4 h-4" /> Download WAV
                  </a>
                </div>
              </div>
            ) : (
              <div className="h-32 flex items-center justify-center text-muted-foreground text-sm italic border-2 border-dashed border-gray-800 rounded-lg">
                No audio generated yet
              </div>
            )}
          </div>

          {/* History */}
          <div className="bg-secondary/30 border border-gray-800 rounded-xl p-6 flex-1 min-h-[400px]">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <History className="w-5 h-5 text-gray-400" /> History
            </h2>
            <div className="space-y-3">
              {history.length === 0 ? (
                <p className="text-sm text-muted-foreground">Your generation history will appear here.</p>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="p-3 bg-background/50 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors group">
                    <p className="text-sm text-gray-300 line-clamp-2 mb-2">"{item.text}"</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{item.timestamp.toLocaleTimeString()}</span>
                      <button
                        onClick={() => setAudioUrl(item.audioUrl)}
                        className="text-xs bg-primary/10 text-primary px-2 py-1 rounded hover:bg-primary/20 transition-colors"
                      >
                        Play
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
