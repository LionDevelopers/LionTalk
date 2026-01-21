// src/app/page.tsx
'use client';

import React, { useState, useMemo } from 'react';
import rawData from '../data/seminars.json'; 
import { Seminar, SeminarSeriesData } from '../types';
import { SeminarCard } from '../components/SeminarCard';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  // 1. State to toggle visibility of past seminars "upon request"
  const [showRecentPast, setShowRecentPast] = useState(false);

  const seminars: Seminar[] = useMemo(() => {
    const seminarGroups = rawData as unknown as SeminarSeriesData[];
    
    return seminarGroups.flatMap((group) => 
      group.entries.map((entry) => ({
        ...entry,
        department: group.department,
        series: group.series, 
      }))
    );
  }, []);

  const { todaySeminars, upcomingSeminars, pastSeminars } = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // 2. Define the 30-day cutoff window
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);

    // Filter by Search Query
    const filtered = seminars.filter((s) => {
      const query = searchQuery.toLowerCase();
      return (
        s.seminar_title.toLowerCase().includes(query) ||
        s.speaker.toLowerCase().includes(query) ||
        s.abstract.toLowerCase().includes(query) ||
        s.date.toLowerCase().includes(query) ||
        s.location.toLowerCase().includes(query) ||
        s.department.toLowerCase().includes(query) ||
        (s.series && s.series.toLowerCase().includes(query))
      );
    });

    // Segment
    const todayList: Seminar[] = [];
    const upcomingList: Seminar[] = [];
    const pastList: Seminar[] = [];

    filtered.forEach((seminar) => {
      const seminarDate = new Date(seminar.date);
      seminarDate.setHours(0, 0, 0, 0);

      if (seminarDate.getTime() === today.getTime()) {
        todayList.push(seminar);
      } else if (seminarDate.getTime() > today.getTime()) {
        upcomingList.push(seminar);
      } else {
        // 3. Only add to pastList if it happened within the last 30 days
        if (seminarDate.getTime() >= thirtyDaysAgo.getTime()) {
          pastList.push(seminar);
        }
      }
    });

    // Sort Past Seminars (Newest first)
    pastList.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

    return { todaySeminars: todayList, upcomingSeminars: upcomingList, pastSeminars: pastList };
  }, [seminars, searchQuery]);

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🦁 LionTalk</h1>
          <p className="text-lg text-gray-600 mb-8">
            Brought to you by LionDevelopers @ Columbia University
          </p>
          
          <div className="max-w-xl mx-auto relative">
            <input
              type="text"
              placeholder="Search by title, speaker, topic, or department..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-4 pr-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm text-gray-900"
            />
          </div>
        </div>

        <div className="space-y-12">
          {/* TODAY */}
          {todaySeminars.length > 0 && (
            <section>
              <h2 className="text-2xl font-bold text-indigo-700 mb-6 border-b border-indigo-200 pb-2">
                Happening Today
              </h2>
              <div className="space-y-6">
                {todaySeminars.map((seminar, index) => (
                  <SeminarCard key={`today-${index}`} seminar={seminar} />
                ))}
              </div>
            </section>
          )}

          {/* UPCOMING */}
          {upcomingSeminars.length > 0 && (
            <section>
              <h2 className="text-2xl font-bold text-gray-800 mb-6 border-b border-gray-200 pb-2">
                Upcoming Seminars
              </h2>
              <div className="space-y-6">
                {upcomingSeminars.map((seminar, index) => (
                  <SeminarCard key={`upcoming-${index}`} seminar={seminar} />
                ))}
              </div>
            </section>
          )}

          {/* PAST (Last 30 Days) - Only shown upon request */}
          {pastSeminars.length > 0 && (
            <section className="pt-4">
              <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-2">
                <h2 className="text-2xl font-bold text-gray-500">
                  Recent Past Seminars <span className="text-sm font-normal text-gray-400">(Last 30 days)</span>
                </h2>
                
                {/* 4. Toggle Button */}
                <button 
                  onClick={() => setShowRecentPast(!showRecentPast)}
                  className="text-sm font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none transition-colors"
                >
                  {showRecentPast ? 'Hide' : 'Show'}
                </button>
              </div>

              {/* 5. Conditional Rendering based on state */}
              {showRecentPast && (
                <div className="space-y-6 opacity-90 transition-all duration-300 ease-in-out">
                  {pastSeminars.map((seminar, index) => (
                    <SeminarCard key={`past-${index}`} seminar={seminar} />
                  ))}
                </div>
              )}
            </section>
          )}

          {/* EMPTY STATE */}
          {todaySeminars.length === 0 && upcomingSeminars.length === 0 && pastSeminars.length === 0 && (
            <div className="text-center py-12">
              <p className="text-xl text-gray-500">No seminars found matching "{searchQuery}"</p>
              <button 
                onClick={() => setSearchQuery('')}
                className="mt-4 text-indigo-600 font-medium hover:underline"
              >
                Clear Search
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}