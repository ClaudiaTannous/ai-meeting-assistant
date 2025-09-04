"use client";

import { useState } from "react";
import { useParams } from "next/navigation"; // ✅ get meetingId from URL
import AISummary from "./AISummary";
import Cookies from "js-cookie";

export default function Recorder() {
  const { id } = useParams(); // ✅ /meetings/[id]
  const meetingId = Number(id);

  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcript, setTranscript] = useState<string>("");
  const [recognition, setRecognition] = useState<any>(null);
  const [summary, setSummary] = useState<string>("");

  const startRecording = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition.");
      return;
    }

    const recog = new SpeechRecognition();
    recog.lang = "en-US";
    recog.interimResults = true;
    recog.continuous = true;

    recog.onresult = (event: any) => {
      let finalText = transcript;
      let interimText = "";

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript + " ";
        } else {
          interimText += result[0].transcript;
        }
      }

      setTranscript(finalText + interimText);
    };

    recog.start();
    setRecognition(recog);
    setIsRecording(true);
    setIsPaused(false);
    setSummary("");
  };

  const pauseRecording = () => {
    if (recognition) recognition.stop();
    setIsPaused(true);
    setIsRecording(false);
  };

  const resumeRecording = () => {
    if (recognition) recognition.start();
    setIsPaused(false);
    setIsRecording(true);
  };

  const stopRecording = async () => {
    if (recognition) recognition.stop();
    setIsRecording(false);
    setIsPaused(false);

    console.log("📤 Sending transcript:", transcript);

    if (!transcript.trim()) {
      setSummary("⚠️ No speech detected. Please try again.");
      return;
    }

    try {
      const token = Cookies.get("token");
      if (!token) {
        setSummary("❌ No auth token found. Please log in.");
        return;
      }

      // 1️⃣ Save transcript dynamically for this meeting
      const transcriptRes = await fetch(
        `http://localhost:8000/transcripts/${meetingId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: JSON.stringify({ content: transcript }),
        }
      );

      if (!transcriptRes.ok) {
        setSummary("❌ Failed to save transcript.");
        return;
      }

      const transcriptData = await transcriptRes.json();
      const transcriptId = transcriptData.id;

      // 2️⃣ Generate summary dynamically
      const response = await fetch(
        `http://localhost:8000/summaries/${transcriptId}/ai`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSummary(data.summary_text);
      } else {
        setSummary("❌ Failed to get summary from backend.");
      }
    } catch (err) {
      console.error("Error:", err);
      setSummary("❌ Could not connect to backend.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Recorder + Transcript */}
      <div className="bg-white p-6 rounded-xl shadow-md border">
        <h2 className="text-lg font-semibold mb-3">
          Live Meeting Transcription
        </h2>

        <div className="flex gap-4 mb-4">
          {!isRecording && !isPaused ? (
            <button
              onClick={startRecording}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
            >
              🎙️ Start Recording
            </button>
          ) : isRecording ? (
            <button
              onClick={pauseRecording}
              className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600"
            >
              ⏸️ Pause
            </button>
          ) : (
            <button
              onClick={resumeRecording}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              ▶️ Resume
            </button>
          )}

          {(isRecording || isPaused) && (
            <button
              onClick={stopRecording}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              ⏹️ Stop
            </button>
          )}
        </div>

        <div className="bg-gray-50 p-4 rounded-lg h-60 overflow-y-auto mb-4">
          {transcript ? (
            <p className="text-gray-700 whitespace-pre-wrap">{transcript}</p>
          ) : (
            <p className="text-gray-500 text-sm">Waiting for speech...</p>
          )}
        </div>
      </div>

      {/* AI Summary */}
      <AISummary summary={summary} />
    </div>
  );
}
