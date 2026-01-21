import React from 'react';
// Ensure 'Seminar' type in types.ts includes 'series?: string;'
import { Seminar } from '../types';

export const SeminarCard = ({ seminar }: { seminar: Seminar }) => {
  const isHoliday = seminar.speaker === "N/A";

  // Helper to generate Google Calendar Link
  const getGoogleCalendarLink = (seminar: Seminar) => {
    try {
      // 1. Parse the Date: "20-Jan-26" -> [20, Jan, 26]
      const monthMap: { [key: string]: number } = {
        Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5,
        Jul: 6, Aug: 7, Sep: 8, Sept: 8, Oct: 9, Nov: 10, Dec: 11
      };
      
      const [dayStr, monthStr, yearStr] = seminar.date.split('-');
      const day = parseInt(dayStr, 10);
      const month = monthMap[monthStr];
      const year = 2000 + parseInt(yearStr, 10); // Assume 2000s

      // 2. Parse the Time: "4:10 pm - 5:00 pm"
      const [startTimeStr, endTimeStr] = seminar.time.split('-').map(s => s.trim());

      const parseTime = (timeString: string) => {
        const match = timeString.match(/(\d+):(\d+)\s*(am|pm)/i);
        if (!match) return { hours: 0, minutes: 0 };
        
        let [_, h, m, meridiem] = match;
        let hours = parseInt(h, 10);
        const minutes = parseInt(m, 10);

        if (meridiem.toLowerCase() === 'pm' && hours < 12) hours += 12;
        if (meridiem.toLowerCase() === 'am' && hours === 12) hours = 0;
        
        return { hours, minutes };
      };

      const start = parseTime(startTimeStr);
      const end = parseTime(endTimeStr);

      // 3. Create Date Objects
      const startDate = new Date(year, month, day, start.hours, start.minutes);
      // Fallback: If end time parsing fails, assume 1 hour duration
      let endDate = new Date(year, month, day, end.hours, end.minutes);
      if (isNaN(endDate.getTime()) || endDate <= startDate) {
         endDate = new Date(startDate.getTime() + 60 * 60 * 1000); 
      }

      // 4. Format for Google (YYYYMMDDTHHmmssZ)
      const fmt = (date: Date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "");

      const params = new URLSearchParams({
        action: "TEMPLATE",
        text: `LionTalk: ${seminar.seminar_title}`,
        dates: `${fmt(startDate)}/${fmt(endDate)}`,
        // UPDATED: Added Department AND Series to details
        details: `Department: ${seminar.department}\nSeries: ${seminar.series || 'N/A'}\nSpeaker: ${seminar.speaker}\nAffiliation: ${seminar.affiliation}\n\nAbstract: ${seminar.abstract}`,
        location: seminar.location,
      });

      return `https://calendar.google.com/calendar/render?${params.toString()}`;
    } catch (e) {
      console.error("Error generating calendar link", e);
      return "#";
    }
  };

  return (
    <div
      className={`rounded-lg shadow-md overflow-hidden border ${
        isHoliday
          ? 'bg-gray-100 border-gray-200 opacity-75'
          : 'bg-white border-gray-200'
      }`}
    >
      <div className="p-6">
        {/* Header: Date, Time, Location AND Department/Series */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4">
          {/* Left Side: Date/Time/Location */}
          <div>
            <div className="flex items-center space-x-2 text-indigo-600 font-semibold">
              <span>{seminar.date}</span>
              <span>•</span>
              <span>{seminar.time}</span>
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {seminar.location}
            </div>
          </div>
          
          {/* Right Side: Department Badge & Series */}
          {!isHoliday && (
            <div className="flex flex-col items-start sm:items-end mt-2 sm:mt-0 gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                {seminar.department}
              </span>
              
              {seminar.series && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800">
                  {seminar.series}
                </span>
              )}
            </div>
          )}

        </div>

        {/* Title */}
        <h2
          className={`text-2xl font-bold mb-2 ${
            isHoliday ? 'text-gray-500 italic' : 'text-gray-900'
          }`}
        >
          {seminar.seminar_title}
        </h2>

        {/* Speaker Info */}
        {!isHoliday && (
          <>
            <div className="mb-4">
              <span className="text-lg font-medium text-gray-800">
                {seminar.speaker}
              </span>
              {seminar.affiliation && (
                <span className="text-gray-600 ml-2">
                  ({seminar.affiliation})
                </span>
              )}
            </div>

            {/* Details: Abstract & Bio */}
            <div className="space-y-4 text-gray-700">
              <details className="group">
                <summary className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none">
                  Read Abstract
                </summary>
                <p className="mt-2 text-sm leading-relaxed border-l-4 border-indigo-100 pl-4">
                  {seminar.abstract}
                </p>
              </details>

              {seminar.bio && (
                <details className="group">
                  <summary className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800 focus:outline-none">
                    Speaker Bio
                  </summary>
                  <p className="mt-2 text-sm leading-relaxed border-l-4 border-indigo-100 pl-4 italic">
                    {seminar.bio}
                  </p>
                </details>
              )}

              {/* Add to Calendar Button */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <a 
                  href={getGoogleCalendarLink(seminar)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
                >
                  <span className="mr-2">📅</span> Add to Google Calendar
                </a>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};