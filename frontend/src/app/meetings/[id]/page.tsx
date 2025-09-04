"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import type { Meeting, Transcript, Summary } from "@/types";
import Recorder from "@/components/Recorder";
interface RecorderProps {
  meetingId: number; // 👈 declare meetingId prop
}

export default function MeetingDetailsPage() {
  const params = useParams();
  const meetingId = parseInt(params?.id as string, 10);

  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    const fetchMeeting = async () => {
      try {
        const res = await api.get(`/meetings/${meetingId}`);
        const data = res.data as Meeting;

        setMeeting(data);
        if (data.transcript) {
          setTranscript(data.transcript);
          setSummaries(data.transcript.summaries || []);
        }
      } catch (err) {
        console.error("Error fetching meeting:", err);
      } finally {
        setLoading(false);
      }
    };

    if (meetingId && !Number.isNaN(meetingId)) fetchMeeting();
  }, [meetingId]);

  const handleGenerateAiSummary = async () => {
    if (!transcript) return;
    setLoadingSummary(true);
    try {
      const res = await api.post(`/summaries/${transcript.id}/ai`);
      const newSummary = res.data as Summary;
      setSummaries((prev) => [newSummary, ...prev]);
    } catch (err) {
      console.error("Error generating AI summary:", err);
    } finally {
      setLoadingSummary(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading meeting...</p>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">Meeting not found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      {/* Meeting header */}
      <div className="bg-white p-6 rounded-xl shadow-md border">
        <h1 className="text-2xl font-bold">{meeting.title}</h1>
        <p className="text-sm text-gray-500">
          {new Date(meeting.date).toLocaleString()}
        </p>
      </div>

      {/* Recorder for live transcription */}
      <Recorder />

      {/* Transcript */}
      {transcript && (
        <div className="bg-white p-6 rounded-xl shadow-md border">
          <h2 className="text-xl font-semibold mb-3">Transcript</h2>
          <p className="text-gray-700 whitespace-pre-wrap">
            {transcript.content}
          </p>
        </div>
      )}

      {/* Summaries */}
      <div className="bg-white p-6 rounded-xl shadow-md border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold">AI Summaries</h2>
          {transcript && (
            <button
              onClick={handleGenerateAiSummary}
              disabled={loadingSummary}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {loadingSummary ? "Generating..." : "Generate AI Summary"}
            </button>
          )}
        </div>

        {summaries.length === 0 ? (
          <p className="text-gray-500">No summaries yet.</p>
        ) : (
          <div className="space-y-4">
            {summaries.map((summary) => (
              <div
                key={summary.id}
                className="p-4 bg-gray-50 rounded-lg border"
              >
                <p className="text-gray-700">{summary.summary_text}</p>
                <p className="text-xs text-gray-400 mt-2">
                  Source: {summary.source} •{" "}
                  {new Date(summary.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
