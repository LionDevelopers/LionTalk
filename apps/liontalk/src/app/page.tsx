// src/app/page.tsx
'use client';

import React, { useState, useMemo } from 'react';
import rawData from '../data/seminars.json'; 
import { Seminar, SeminarSeriesData } from '../types';
import { SeminarCard } from '../components/SeminarCard';
import { parseSeminarDate } from '../utils/dates';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
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

    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);

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

    const todayList: Seminar[] = [];
    const upcomingList: Seminar[] = [];
    const pastList: Seminar[] = [];

    const startTime = (s: Seminar) => parseSeminarDate(s.date, s.time).startDate?.getTime() ?? 0;

    filtered.forEach((seminar) => {
      const startDate = parseSeminarDate(seminar.date, seminar.time).startDate;
      if (!startDate) return;

      const seminarDate = new Date(startDate);
      seminarDate.setHours(0, 0, 0, 0);

      if (seminarDate.getTime() === today.getTime()) {
        todayList.push(seminar);
      } else if (seminarDate.getTime() > today.getTime()) {
        upcomingList.push(seminar);
      } else {
        if (seminarDate.getTime() >= thirtyDaysAgo.getTime()) {
          pastList.push(seminar);
        }
      }
    });

    // Today: earliest start time first; Upcoming: soonest first; Past: most recent first
    todayList.sort((a, b) => startTime(a) - startTime(b));
    upcomingList.sort((a, b) => startTime(a) - startTime(b));
    pastList.sort((a, b) => startTime(b) - startTime(a));

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

          {/* PAST */}
          {pastSeminars.length > 0 && (
            <section className="pt-4">
              <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-2">
                <h2 className="text-2xl font-bold text-gray-500">
                  Recent Past Seminars <span className="text-sm font-normal text-gray-400">(Last 30 days)</span>
                </h2>
                
                <button 
                  onClick={() => setShowRecentPast(!showRecentPast)}
                  className="text-sm font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none transition-colors"
                >
                  {showRecentPast ? 'Hide' : 'Show'}
                </button>
              </div>

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