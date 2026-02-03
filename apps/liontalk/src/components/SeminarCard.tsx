import React from 'react';
import { Seminar } from '../types';
import { getGoogleCalendarLink, parseSeminarDate } from '../utils/dates'; //

const ClockIcon = () => (
  <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
);
const MapPinIcon = () => (
  <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
);
const CalendarIcon = () => (
  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
);
const ChevronDownIcon = ({ open }: { open?: boolean }) => (
  <svg className={`w-4 h-4 transform transition-transform duration-200 ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
);

export const SeminarCard = ({ seminar }: { seminar: Seminar }) => {
  const isHoliday = seminar.speaker === "N/A";
  const { monthAbbr, dayDisplay } = parseSeminarDate(seminar.date, seminar.time);

  if (isHoliday) {
    return (
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-6 flex items-center justify-center opacity-75 select-none">
        <div className="text-center">
          <span className="block text-sm font-semibold text-gray-400 uppercase tracking-wider mb-1">{seminar.date}</span>
          <h2 className="text-xl font-medium text-gray-500 italic">{seminar.seminar_title}</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-300 ease-in-out overflow-hidden flex flex-col md:flex-row">
      
      {/* 1. Left Side: Visual Date Badge - COLUMBIA BLUE */}
      <div className="md:w-24 bg-columbia-blue/5 border-b md:border-b-0 md:border-r border-columbia-blue/10 flex md:flex-col items-center justify-center p-4 md:py-0 shrink-0">
        {/* Added suppressHydrationWarning to these two spans to fix the error */}
        <span suppressHydrationWarning className="text-columbia-blue font-bold uppercase text-sm tracking-wider md:mb-1">
          {monthAbbr}
        </span>
        <span suppressHydrationWarning className="text-gray-900 font-extrabold text-2xl md:text-3xl ml-2 md:ml-0">
          {dayDisplay}
        </span>
      </div>

      <div className="flex-1 p-5 sm:p-6 flex flex-col">
        {/* Header: Tags */}
        <div className="flex flex-wrap gap-2 mb-3">
          {/* Department: Light Blue BG, Dark Blue Text */}
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold bg-columbia-light/20 text-columbia-blue">
            {seminar.department}
          </span>
          {/* Series: Turquoise */}
          {seminar.series && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold bg-columbia-turquoise/10 text-columbia-turquoise border border-columbia-turquoise/20">
              {seminar.series}
            </span>
          )}
        </div>

        {/* Title */}
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 leading-tight mb-2 group-hover:text-columbia-blue transition-colors">
          {seminar.seminar_title}
        </h2>

        {/* Speaker */}
        <div className="mb-4">
          <span className="text-base sm:text-lg font-medium text-gray-800">
            {seminar.speaker}
          </span>
          {seminar.affiliation && (
            <span className="text-gray-500 text-sm sm:text-base ml-2 font-normal">
              — {seminar.affiliation}
            </span>
          )}
        </div>

        {/* Meta Info Grid: Time & Location */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5 text-sm text-gray-600">
          <div className="flex items-center group/meta">
            <span className="text-columbia-medium group-hover/meta:text-columbia-blue transition-colors"><ClockIcon /></span>
            <span>{seminar.time}</span>
          </div>
          <div className="flex items-center group/meta">
            <span className="text-columbia-medium group-hover/meta:text-columbia-blue transition-colors"><MapPinIcon /></span>
            <span className="truncate" title={seminar.location}>{seminar.location}</span>
          </div>
        </div>

        <div className="h-px bg-gray-100 w-full mb-4"></div>

        {/* Interactive Sections */}
        <div className="space-y-3 flex-1">
          <details className="group/abstract">
            <summary className="list-none cursor-pointer flex items-center justify-between text-sm font-medium text-gray-500 hover:text-columbia-blue transition-colors focus:outline-none">
              <span>Abstract</span>
              <div className="group-open/abstract:rotate-180 transition-transform duration-200">
                <ChevronDownIcon />
              </div>
            </summary>
            {/* Abstract border: Columbia Light Blue */}
            <p className="mt-3 text-sm text-gray-700 leading-relaxed border-l-4 border-columbia-light pl-4 py-1">
              {seminar.abstract}
            </p>
          </details>

          {seminar.bio && (
            <details className="group/bio">
              <summary className="list-none cursor-pointer flex items-center justify-between text-sm font-medium text-gray-500 hover:text-columbia-blue transition-colors focus:outline-none">
                <span>Speaker Bio</span>
                 <div className="group-open/bio:rotate-180 transition-transform duration-200">
                  <ChevronDownIcon />
                </div>
              </summary>
              <p className="mt-3 text-sm text-gray-600 leading-relaxed italic border-l-4 border-columbia-light pl-4 py-1">
                {seminar.bio}
              </p>
            </details>
          )}
        </div>

        {/* Footer: Calendar Button */}
        <div className="mt-6 flex justify-end">
          <a 
            href={getGoogleCalendarLink(seminar)} //
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-columbia-blue bg-white border border-columbia-blue/30 rounded-lg hover:bg-columbia-blue hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-columbia-blue"
          >
            <CalendarIcon />
            Add to Calendar
          </a>
        </div>
      </div>
    </div>
  );
};