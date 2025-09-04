"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import type { Meeting } from "@/types";

export default function MeetingsPage() {
  const router = useRouter();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const res = await api.get("/meetings");
        setMeetings(res.data as Meeting[]);
      } catch (err) {
        console.error("Error fetching meetings:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMeetings();
  }, []);

  // Create a new meeting
  const handleCreateMeeting = async () => {
    setCreating(true);
    try {
      const res = await api.post("/meetings", { title: "New Meeting" });
      const newMeeting = res.data as Meeting;
      router.push(`/meetings/${newMeeting.id}`);
    } catch (err) {
      console.error("Error creating meeting:", err);
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading meetings...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Header */}
      <header>
        <h1 className="text-2xl font-bold text-gray-900">
          AI Meeting Assistant
        </h1>
        <p className="text-gray-500">
          Record, transcribe, and summarize meetings with AI
        </p>
      </header>

      {/* Recording Card */}
      <div className="bg-blue-50 border border-blue-200 p-6 rounded-xl flex items-center justify-between shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Ready to Record
          </h2>
          <p className="text-sm text-gray-600">
            Click start to begin recording
          </p>
        </div>
        <button
          onClick={handleCreateMeeting}
          disabled={creating}
          className="bg-blue-600 text-white px-5 py-2 rounded-lg shadow hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {creating ? "Creating..." : "🎙️ Start Recording"}
        </button>
      </div>

      {/* Recent Meetings */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Recent Meetings{" "}
            <span className="text-gray-400 text-sm">
              ({meetings.length} meetings)
            </span>
          </h2>
          <button
            onClick={() => router.push("/meetings")}
            className="text-sm text-indigo-600 hover:underline"
          >
            View All
          </button>
        </div>

        {meetings.length === 0 ? (
          <p className="text-gray-500 text-sm">
            No meetings yet. Create one above.
          </p>
        ) : (
          <div className="space-y-4">
            {meetings.map((meeting) => {
              const latestSummary =
                meeting.transcript?.summaries &&
                meeting.transcript.summaries.length > 0
                  ? meeting.transcript.summaries[0].summary_text
                  : null;

              return (
                <div
                  key={meeting.id}
                  onClick={() => router.push(`/meetings/${meeting.id}`)}
                  className="p-4 bg-white rounded-xl border shadow-sm hover:shadow-md cursor-pointer transition"
                >
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-gray-900">
                      {meeting.title}
                    </h3>
                    {meeting.transcript ? (
                      <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">
                        Transcript Available
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs rounded-full bg-gray-200 text-gray-600">
                        No Transcript
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-gray-500">
                    📅 {new Date(meeting.date).toLocaleDateString()}
                  </div>

                  {latestSummary && (
                    <p className="text-sm text-gray-600 mt-2 line-clamp-1">
                      {latestSummary}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
